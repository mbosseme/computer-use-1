from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

# Allow running this script directly while still importing the repo package.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator  # noqa: E402
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig  # noqa: E402
from agent_tools.graph.env import load_graph_env  # noqa: E402


def _graph_client(repo_root: Path) -> GraphAPIClient:
    env = load_graph_env(repo_root)
    authenticator = GraphAuthenticator(repo_root=repo_root, env=env)
    config = GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone)
    return GraphAPIClient(authenticator=authenticator, config=config)


def _safe_filename(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", s).strip("_")
    return s[:120] if len(s) > 120 else s


def _first(values: Iterable[str]) -> str | None:
    for v in values:
        if v:
            return v
    return None


def _strip_html(html_body: str) -> str:
    # Minimal HTML-to-text: remove tags, preserve whitespace.
    # This is not perfect, but is deterministic and good enough for searching.
    text = re.sub(r"<\s*br\s*/?>", "\n", html_body, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    # Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _format_recipients(msg: dict[str, Any], key: str) -> str:
    recips = msg.get(key) or []
    parts: list[str] = []
    for r in recips:
        ea = (r or {}).get("emailAddress") or {}
        name = (ea.get("name") or "").strip()
        addr = (ea.get("address") or "").strip()
        if name and addr:
            parts.append(f"{name} <{addr}>")
        elif addr:
            parts.append(addr)
        elif name:
            parts.append(name)
    return ", ".join(parts)


def _select_fields() -> str:
    return ",".join(
        [
            "id",
            "conversationId",
            "subject",
            "from",
            "toRecipients",
            "ccRecipients",
            "sentDateTime",
            "receivedDateTime",
            "bodyPreview",
            "body",
        ]
    )


def _iso_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        # Graph returns ISO8601 like 2026-01-22T14:39:00Z
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _search_latest_message(*, client: GraphAPIClient, query: str, top: int) -> dict[str, Any] | None:
    resp = client.get(
        "me/messages",
        params={
            "$search": f'"{query}"',
            "$top": top,
            "$select": "id,conversationId,subject,from,toRecipients,ccRecipients,receivedDateTime,sentDateTime,bodyPreview",
        },
        headers={"ConsistencyLevel": "eventual"},
    )
    items = resp.get("value") or []
    if not items:
        return None

    def _key(m: dict[str, Any]) -> datetime:
        dt = _iso_dt(m.get("receivedDateTime")) or _iso_dt(m.get("sentDateTime"))
        return dt or datetime.min

    items_sorted = sorted(items, key=_key, reverse=True)
    return items_sorted[0]


def _fetch_conversation(*, client: GraphAPIClient, conversation_id: str) -> list[dict[str, Any]]:
    resp = client.get(
        "me/messages",
        params={
            "$filter": f"conversationId eq '{conversation_id}'",
            "$top": 200,
            "$select": _select_fields(),
        },
    )
    items = list(resp.get("value") or [])
    items.sort(key=lambda m: (_iso_dt(m.get("sentDateTime")) or _iso_dt(m.get("receivedDateTime")) or datetime.min))
    return items


def _write_exports(*, out_dir: Path, stem: str, latest: dict[str, Any], thread: list[dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / f"{stem}.latest.json").write_text(json.dumps(latest, indent=2), encoding="utf-8")
    (out_dir / f"{stem}.thread.json").write_text(json.dumps(thread, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append(f"# Outlook thread export: {latest.get('subject','(no subject)')}")
    lines.append("")
    lines.append(f"Exported: {datetime.utcnow().isoformat(timespec='seconds')}Z")
    lines.append(f"Messages: {len(thread)}")
    lines.append("")

    for i, msg in enumerate(thread, start=1):
        subject = msg.get("subject") or "(no subject)"
        sent = msg.get("sentDateTime") or msg.get("receivedDateTime") or "(no date)"
        sender = ((msg.get("from") or {}).get("emailAddress") or {}).get("address") or "(unknown)"

        lines.append("---")
        lines.append(f"## [{i}] {sent} | {subject}")
        lines.append("")
        lines.append(f"From: {sender}")
        to_line = _format_recipients(msg, "toRecipients")
        cc_line = _format_recipients(msg, "ccRecipients")
        if to_line:
            lines.append(f"To: {to_line}")
        if cc_line:
            lines.append(f"Cc: {cc_line}")
        lines.append("")

        body = msg.get("body") or {}
        content_type = (body.get("contentType") or "").upper()
        content = body.get("content") or ""

        if content_type == "HTML":
            body_text = _strip_html(content)
        else:
            body_text = content.strip()

        # Keep full body for local use; don't try to be clever.
        lines.append(body_text)
        lines.append("")

    (out_dir / f"{stem}.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the latest Selina/Charity GE thread from Outlook via Graph.")
    parser.add_argument(
        "--query",
        default="GE / Premier Market Insights Introduction & Overview",
        help="Search phrase to locate the most recent message in the target thread.",
    )
    parser.add_argument("--top", type=int, default=25, help="How many messages to consider in search.")
    parser.add_argument(
        "--out-dir",
        default="runs/2026-01-16__ge-market-insights/exports/mail_threads",
        help="Output directory for exports.",
    )

    args = parser.parse_args()

    client = _graph_client(REPO_ROOT)
    latest = _search_latest_message(client=client, query=args.query, top=args.top)
    if not latest:
        raise RuntimeError(f"No messages found for query: {args.query!r}")

    conversation_id = latest.get("conversationId")
    if not conversation_id:
        raise RuntimeError("Latest message missing conversationId")

    thread = _fetch_conversation(client=client, conversation_id=conversation_id)

    subject = latest.get("subject") or args.query
    stem = _safe_filename(subject.lower().replace(" ", "_"))
    out_dir = (REPO_ROOT / args.out_dir).resolve()

    _write_exports(out_dir=out_dir, stem=stem, latest=latest, thread=thread)

    print("Export complete.")
    print(f"- Subject: {subject}")
    print(f"- Messages: {len(thread)}")
    print(f"- Out: {out_dir}/{stem}.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
