from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def _repo_root() -> Path:
    # This script lives under runs/<RUN_ID>/scripts/, so repo root is 3 levels up.
    return Path(__file__).resolve().parents[3]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").strip().lower()).strip()


def _looks_like_sender(
    msg: Dict[str, Any],
    *,
    name_query: str,
    sender_email: Optional[str] = None,
) -> bool:
    sender = msg.get("from") or {}
    email_addr = sender.get("emailAddress") or {}
    display_name = str(email_addr.get("name") or "")
    address = str(email_addr.get("address") or "")

    if sender_email and address.strip().lower() == sender_email.strip().lower():
        return True

    nq = _norm(name_query)
    dn = _norm(display_name)
    ad = _norm(address)

    # Strong match on full name, otherwise require both tokens.
    if nq and nq in dn:
        return True

    if nq and nq in ad:
        return True

    tokens = [t for t in nq.split() if t]
    if len(tokens) >= 2 and all(t in dn for t in tokens):
        return True

    if len(tokens) >= 2 and all(t in ad for t in tokens):
        return True

    return False


_TAG_RE = re.compile(r"<[^>]+>")


def _html_to_text(value: str) -> str:
    s = (value or "").replace("\r", "")
    s = _TAG_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _pick_latest(messages: Iterable[Dict[str, Any]], *, name_query: str) -> Optional[Dict[str, Any]]:
    for m in messages:
        if _looks_like_sender(m, name_query=name_query):
            return m
    return None


def _pick_latest_with_email(
    messages: Iterable[Dict[str, Any]],
    *,
    name_query: str,
    sender_email: Optional[str],
) -> Optional[Dict[str, Any]]:
    for m in messages:
        if _looks_like_sender(m, name_query=name_query, sender_email=sender_email):
            return m
    return None


def _iter_inbox_messages(
    client: GraphAPIClient,
    *,
    page_size: int,
    max_pages: int,
    timeout_s: int,
) -> Iterable[Dict[str, Any]]:
    path = "me/mailFolders/Inbox/messages"
    params: Dict[str, Any] = {
        "$top": page_size,
        "$orderby": "receivedDateTime desc",
        "$select": "id,subject,from,receivedDateTime,bodyPreview,body",
    }

    for _page in range(max_pages):
        resp = client.get(path, params=params, timeout=timeout_s)
        items = resp.get("value", []) if isinstance(resp, dict) else []
        if not isinstance(items, list) or not items:
            return

        for it in items:
            if isinstance(it, dict):
                yield it

        next_link = resp.get("@odata.nextLink") if isinstance(resp, dict) else None
        if not next_link:
            return
        path = str(next_link)
        params = {}


def _iter_folder_messages(
    client: GraphAPIClient,
    *,
    folder_id: str,
    page_size: int,
    max_pages: int,
    timeout_s: int,
) -> Iterable[Dict[str, Any]]:
    path = f"me/mailFolders/{folder_id}/messages"
    params: Dict[str, Any] = {
        "$top": page_size,
        "$orderby": "receivedDateTime desc",
        "$select": "id,subject,from,receivedDateTime,bodyPreview,body",
    }

    for _page in range(max_pages):
        resp = client.get(path, params=params, timeout=timeout_s)
        items = resp.get("value", []) if isinstance(resp, dict) else []
        if not isinstance(items, list) or not items:
            return

        for it in items:
            if isinstance(it, dict):
                yield it

        next_link = resp.get("@odata.nextLink") if isinstance(resp, dict) else None
        if not next_link:
            return
        path = str(next_link)
        params = {}


def _iter_child_folders(
    client: GraphAPIClient,
    *,
    parent_folder_id: str,
    timeout_s: int,
) -> Iterable[Tuple[str, str]]:
    path = f"me/mailFolders/{parent_folder_id}/childFolders"
    params: Dict[str, Any] = {"$top": 200, "$select": "id,displayName"}
    while True:
        resp = client.get(path, params=params, timeout=timeout_s)
        items = resp.get("value", []) if isinstance(resp, dict) else []
        if isinstance(items, list):
            for it in items:
                if not isinstance(it, dict):
                    continue
                fid = str(it.get("id") or "").strip()
                name = str(it.get("displayName") or "").strip()
                if fid:
                    yield fid, name

        next_link = resp.get("@odata.nextLink") if isinstance(resp, dict) else None
        if not next_link:
            break
        path = str(next_link)
        params = {}


def _find_descendant_folder_id(
    client: GraphAPIClient,
    *,
    root_folder_id: str,
    target_display_name: str,
    timeout_s: int,
    max_folders: int = 500,
) -> Optional[str]:
    target = _norm(target_display_name)
    if not target:
        return None

    queue = [root_folder_id]
    seen: set[str] = set()
    visited = 0

    while queue and visited < max_folders:
        parent = queue.pop(0)
        if parent in seen:
            continue
        seen.add(parent)
        visited += 1

        for fid, name in _iter_child_folders(client, parent_folder_id=parent, timeout_s=timeout_s):
            if _norm(name) == target:
                return fid
            if fid not in seen:
                queue.append(fid)

    return None


def _search_latest_message(
    client: GraphAPIClient,
    *,
    sender_email: str,
    timeout_s: int,
) -> Optional[Dict[str, Any]]:
    # Use AQS search across the mailbox (not just Inbox).
    # Requires ConsistencyLevel header.
    resp = client.get(
        "me/messages",
        params={
            "$top": 25,
            "$select": "id,subject,from,receivedDateTime,bodyPreview,body",
            "$count": "true",
            "$search": f'"from:{sender_email}"',
        },
        headers={"ConsistencyLevel": "eventual"},
        timeout=timeout_s,
    )
    items = resp.get("value", []) if isinstance(resp, dict) else []
    if not isinstance(items, list) or not items:
        return None

    # Prefer exact sender match; then choose newest receivedDateTime (best-effort).
    exact: list[Dict[str, Any]] = []
    others: list[Dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        _name, addr = _get_sender_display(it)
        if addr.strip().lower() == sender_email.strip().lower():
            exact.append(it)
        else:
            others.append(it)

    def _dt_key(m: Dict[str, Any]) -> str:
        return str(m.get("receivedDateTime") or "")

    if exact:
        return sorted(exact, key=_dt_key, reverse=True)[0]
    if others:
        return sorted(others, key=_dt_key, reverse=True)[0]
    return None


def _safe_filename(s: str) -> str:
    s = _norm(s).replace(" ", "_")
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "email"


def _parse_iso_dt(s: str) -> Optional[datetime]:
    raw = (s or "").strip()
    if not raw:
        return None

    # Graph may return Z or 7 fractional digits; best-effort normalize.
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"

    if "." in raw:
        head, tail = raw.split(".", 1)
        frac = ""
        rest = ""
        for idx, ch in enumerate(tail):
            if ch.isdigit():
                frac += ch
            else:
                rest = tail[idx:]
                break
        if len(frac) > 6:
            frac = frac[:6]
        raw = f"{head}.{frac}{rest}" if frac else f"{head}{rest}"

    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return None


def _get_sender_display(msg: Dict[str, Any]) -> Tuple[str, str]:
    sender = msg.get("from") or {}
    email_addr = sender.get("emailAddress") or {}
    name = str(email_addr.get("name") or "")
    address = str(email_addr.get("address") or "")
    return name, address


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch the latest Inbox email from a sender (by display name heuristic) and write a run-local review."
    )
    parser.add_argument(
        "--sender-name",
        default="Jennifer Gotto",
        help="Sender display name to match (default: Jennifer Gotto)",
    )
    parser.add_argument(
        "--sender-email",
        default=None,
        help="Optional exact sender email address (recommended if display name matching fails)",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Inbox page size to scan (default: 50)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Max pages to scan (default: 10; total messages ~= page-size * max-pages)",
    )
    parser.add_argument(
        "--out",
        help="Optional output markdown path; defaults under runs/<RUN_ID>/exports/",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="HTTP timeout (seconds) for Graph requests (default: 90)",
    )
    parser.add_argument(
        "--inbox-subfolder",
        default="Addressed",
        help="Inbox subfolder name to search if mailbox-wide search fails (default: Addressed)",
    )
    parser.add_argument(
        "--skip-search",
        action="store_true",
        help="Skip server-side Graph search and only scan Inbox (debug option)",
    )
    args = parser.parse_args()

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

    found: Optional[Dict[str, Any]] = None
    scanned = 0

    if args.sender_email and not args.skip_search:
        found = _search_latest_message(
            client,
            sender_email=str(args.sender_email),
            timeout_s=int(args.timeout),
        )

    # If mailbox-wide search doesn't find it (indexing quirks / policies), look under Inbox subfolders.
    if found is None and args.sender_email and args.inbox_subfolder:
        addressed_id = _find_descendant_folder_id(
            client,
            root_folder_id="Inbox",
            target_display_name=str(args.inbox_subfolder),
            timeout_s=int(args.timeout),
        )
        if addressed_id:
            for msg in _iter_folder_messages(
                client,
                folder_id=addressed_id,
                page_size=args.page_size,
                max_pages=args.max_pages,
                timeout_s=int(args.timeout),
            ):
                scanned += 1
                found = _pick_latest_with_email(
                    [msg],
                    name_query=args.sender_name,
                    sender_email=args.sender_email,
                )
                if found is not None:
                    break
    if found is None:
        for msg in _iter_inbox_messages(
        client,
        page_size=args.page_size,
        max_pages=args.max_pages,
        timeout_s=int(args.timeout),
    ):
            scanned += 1
            found = (
                _pick_latest_with_email([msg], name_query=args.sender_name, sender_email=args.sender_email)
                or found
            )
            if found is not None:
                break

    if found is None:
        raise SystemExit(
            f"No matching message found in Inbox scan (scanned {scanned} messages). "
            "If Mail scopes are missing you may see a 403 earlier; otherwise increase --max-pages."
        )

    subject = str(found.get("subject") or "(no subject)")
    received = str(found.get("receivedDateTime") or "")
    sender_name, sender_addr = _get_sender_display(found)
    body_obj = found.get("body") or {}
    body_content = str(body_obj.get("content") or "")
    body_type = str(body_obj.get("contentType") or "")
    body_text = _html_to_text(body_content) if body_type.lower() == "html" else (body_content or "")
    preview = str(found.get("bodyPreview") or "")

    run_id = Path(__file__).resolve().parents[1].name
    slug = args.sender_email or args.sender_name
    default_out = (
        repo_root
        / "runs"
        / run_id
        / "exports"
        / f"latest_email__{_safe_filename(str(slug))}.md"
    )
    out_path = Path(args.out).expanduser() if args.out else default_out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    received_dt = _parse_iso_dt(received)
    received_fmt = received_dt.isoformat(sep=" ") if received_dt else received

    # Keep the export readable: include full body but also a preview and some quick review prompts.
    export = f"""# Latest email from {sender_name or args.sender_name}

## Metadata
- From: {sender_name or '(unknown)'} <{sender_addr or '(unknown)'}>
- Received: {received_fmt or '(unknown)'}
- Subject: {subject}

## Preview
{preview.strip()}

## Body (best-effort)
{body_text.strip()}

## Review (agent)
- Clarity: TBD
- Key asks: TBD
- Risks / ambiguities: TBD
- Suggested reply framing: TBD

"""

    out_path.write_text(export, encoding="utf-8")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
