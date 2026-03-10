from __future__ import annotations

import argparse
import re
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_filename(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s.strip())
    s = re.sub(r"_+", "_", s)
    return s.strip("_") or "export"


def _html_to_text(html: str) -> str:
    if not html:
        return ""

    text = html
    # Normalize common line break tags to newlines first.
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*div\s*>", "\n", text, flags=re.IGNORECASE)

    # Drop remaining tags.
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)

    # Clean up whitespace.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _format_dt(sent_iso: str, tz_name: str) -> str:
    if not sent_iso:
        return ""

    # Graph usually returns UTC like 2026-01-13T14:00:00Z
    s = sent_iso.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)

    if tz_name and ZoneInfo is not None:
        try:
            dt = dt.astimezone(ZoneInfo(tz_name))
        except Exception:
            pass

    tz_abbrev = dt.strftime("%Z")
    return f"{dt.strftime('%a %Y-%m-%d %I:%M %p')} {tz_abbrev}".replace(" 0", " ").rstrip()


def _email_list(recipients: Any) -> str:
    if not isinstance(recipients, list):
        return ""
    emails: List[str] = []
    for r in recipients:
        if not isinstance(r, dict):
            continue
        addr = ((r.get("emailAddress") or {}) if isinstance(r.get("emailAddress"), dict) else {})
        email = addr.get("address")
        name = addr.get("name")
        if isinstance(email, str) and email:
            if isinstance(name, str) and name and name != email:
                emails.append(f"{name} <{email}>")
            else:
                emails.append(email)
    return ", ".join(emails)


def _iter_sent_messages_to(
    client: GraphAPIClient,
    *,
    recipient_email: str,
    include_cc: bool,
    page_size: int,
    max_messages: int,
) -> Iterable[Dict[str, Any]]:
    # Prefer $filter over $search for determinism, but some tenants do not support
    # filtering on recipients. Fall back to $search when needed.
    email = recipient_email.strip().lower()

    filter_clauses = [
        f"toRecipients/any(r:r/emailAddress/address eq '{email}')",
    ]
    if include_cc:
        filter_clauses.append(f"ccRecipients/any(r:r/emailAddress/address eq '{email}')")

    odata_filter = " or ".join(filter_clauses)
    select_fields = "id,subject,sentDateTime,toRecipients,ccRecipients,bodyPreview,body,webLink,internetMessageId"

    params: Optional[Dict[str, Any]] = {
        "$filter": odata_filter,
        "$orderby": "sentDateTime asc",
        "$top": int(page_size),
        "$select": select_fields,
    }

    # Sent folder:
    # https://graph.microsoft.com/v1.0/me/mailFolders/SentItems/messages
    path = "me/mailFolders/SentItems/messages"

    count = 0
    buffered: List[Dict[str, Any]] = []

    def _flush_buffered() -> Iterable[Dict[str, Any]]:
        nonlocal buffered
        buffered.sort(key=lambda m: str(m.get("sentDateTime") or ""))
        for m in buffered:
            yield m
        buffered = []
    while True:
        try:
            data = client.get(path, params=params)
        except RuntimeError as e:
            # Fall back once from invalid filter to $search.
            msg = str(e)
            if "ErrorInvalidUrlQueryFilter" in msg or "invalid nodes" in msg:
                # $search requires ConsistencyLevel header.
                params = {
                    "$search": f'"recipients:{email}"',
                    "$top": int(page_size),
                    "$select": select_fields,
                }
                data = client.get(
                    "me/mailFolders/SentItems/messages",
                    params=params,
                    headers={"ConsistencyLevel": "eventual"},
                )
                # For $search results, we sort locally later.
                path = "me/mailFolders/SentItems/messages"
            else:
                raise
        items = data.get("value", []) if isinstance(data, dict) else []
        if not isinstance(items, list):
            break

        for msg in items:
            if isinstance(msg, dict):
                # If we're in $search mode (no $orderby), buffer for local sort.
                if params and "$search" in params:
                    buffered.append(msg)
                else:
                    yield msg
                count += 1
                if count >= max_messages:
                    if buffered:
                        yield from _flush_buffered()
                    return

        next_link = data.get("@odata.nextLink") if isinstance(data, dict) else None
        if not isinstance(next_link, str) or not next_link:
            if buffered:
                yield from _flush_buffered()
            return

        # Next link already has query string; clear params.
        path = next_link
        params = None


def export_compiled_sent_mail(
    *,
    out_dir: Path,
    to_email: str,
    include_cc: bool,
    display_timezone: str,
    max_messages: int,
) -> Path:
    repo_root = _repo_root()
    env = load_graph_env(repo_root)

    authenticator = GraphAuthenticator(repo_root=repo_root, env=env)
    client = GraphAPIClient(
        authenticator=authenticator,
        config=GraphClientConfig(
            base_url=env.base_url,
            scopes=env.scopes,
            planner_timezone=env.planner_timezone,
        ),
    )

    me = client.me()
    sender = me.get("userPrincipalName") or me.get("mail") or me.get("displayName")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"compiled_sent_to_{_safe_filename(to_email)}.md"

    lines: List[str] = []
    lines.append(f"# Sent mail compiled export")
    lines.append("")
    lines.append(f"- From: {sender}")
    lines.append(f"- To: {to_email}")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Display timezone: {display_timezone}")
    lines.append("")

    messages = list(
        _iter_sent_messages_to(
            client,
            recipient_email=to_email,
            include_cc=include_cc,
            page_size=50,
            max_messages=max_messages,
        )
    )

    lines.append(f"Total messages: {len(messages)}")
    lines.append("\n---\n")

    for idx, msg in enumerate(messages, start=1):
        subject = msg.get("subject") or "(no subject)"
        sent_dt = _format_dt(str(msg.get("sentDateTime") or ""), display_timezone)
        to_list = _email_list(msg.get("toRecipients"))
        cc_list = _email_list(msg.get("ccRecipients"))
        web_link = msg.get("webLink") or ""
        internet_message_id = msg.get("internetMessageId") or ""

        body_obj = msg.get("body") if isinstance(msg.get("body"), dict) else {}
        body_type = body_obj.get("contentType") if isinstance(body_obj.get("contentType"), str) else ""
        body_content = body_obj.get("content") if isinstance(body_obj.get("content"), str) else ""
        body_preview = msg.get("bodyPreview") if isinstance(msg.get("bodyPreview"), str) else ""

        if body_type.lower() == "html":
            body_text = _html_to_text(body_content)
        else:
            body_text = (body_content or "").strip()

        if not body_text:
            body_text = body_preview.strip()

        lines.append(f"## [{idx}] {subject}")
        lines.append("")
        if sent_dt:
            lines.append(f"- Sent: {sent_dt}")
        if to_list:
            lines.append(f"- To: {to_list}")
        if cc_list:
            lines.append(f"- Cc: {cc_list}")
        if internet_message_id:
            lines.append(f"- Internet-Message-ID: {internet_message_id}")
        if web_link:
            lines.append(f"- WebLink: {web_link}")
        lines.append("")
        lines.append("### Body")
        lines.append("")
        lines.append(body_text if body_text else "(empty)")
        lines.append("\n---\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export sent mail to a recipient into one compiled document")
    parser.add_argument("--to", required=True, help="Recipient email address (match To, and optionally Cc)")
    parser.add_argument(
        "--out-dir",
        default="tmp/mail_exports",
        help="Output directory (will be created). Default: tmp/mail_exports",
    )
    parser.add_argument(
        "--include-cc",
        action="store_true",
        help="Include messages where recipient appears in Cc (in addition to To).",
    )
    parser.add_argument(
        "--display-timezone",
        default="America/New_York",
        help="IANA timezone name used when formatting sent time. Default: America/New_York",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=500,
        help="Maximum number of messages to export (default: 500)",
    )
    args = parser.parse_args()

    out_path = export_compiled_sent_mail(
        out_dir=Path(args.out_dir),
        to_email=args.to,
        include_cc=bool(args.include_cc),
        display_timezone=str(args.display_timezone),
        max_messages=int(args.max),
    )

    print(f"Wrote compiled export: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
