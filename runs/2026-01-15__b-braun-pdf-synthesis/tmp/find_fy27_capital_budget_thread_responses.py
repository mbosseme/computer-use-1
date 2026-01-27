from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# runs/<RUN_ID>/tmp/<this_file>
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator  # noqa: E402
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig  # noqa: E402
from agent_tools.graph.env import load_graph_env  # noqa: E402


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _parse_dt(value: str) -> datetime:
    if not value:
        return datetime.min
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.min


def _sender_name(msg: Dict[str, Any]) -> str:
    f = (msg.get("from") or {}).get("emailAddress") or {}
    return str(f.get("name") or "").strip()


def _sender_addr(msg: Dict[str, Any]) -> str:
    f = (msg.get("from") or {}).get("emailAddress") or {}
    return str(f.get("address") or "").strip()


def _strip_html(value: str) -> str:
    if not value:
        return ""
    # best-effort for email HTML
    value = value.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    value = re.sub(r"</p\s*>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"</div\s*>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<style[\s\S]*?</style>", "", value, flags=re.IGNORECASE)
    value = re.sub(r"<script[\s\S]*?</script>", "", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    # normalize whitespace
    lines = [re.sub(r"\s+$", "", ln) for ln in value.splitlines()]
    # drop obviously empty runs
    cleaned: List[str] = []
    blank = 0
    for ln in lines:
        if not ln.strip():
            blank += 1
            if blank <= 1:
                cleaned.append("")
            continue
        blank = 0
        cleaned.append(ln)
    return "\n".join(cleaned).strip()


def _iter_graph_paged(client: GraphAPIClient, path: str, *, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Iterable[Dict[str, Any]]:
    next_url: Optional[str] = path
    next_params: Optional[Dict[str, Any]] = params

    while next_url:
        resp = client.get(next_url, params=next_params, headers=headers, timeout=90)
        items = resp.get("value") if isinstance(resp, dict) else None
        if isinstance(items, list):
            for it in items:
                if isinstance(it, dict):
                    yield it

        next_link = resp.get("@odata.nextLink") if isinstance(resp, dict) else None
        next_url = str(next_link) if next_link else None
        next_params = None  # nextLink includes its own query


@dataclass
class PersonHit:
    label: str
    match_tokens: List[str]


def main() -> int:
    parser = argparse.ArgumentParser(description="Find latest replies from specific people within a subject thread.")
    parser.add_argument(
        "--subject",
        default="Re: FY27 Capital Budget Planning for SC Data Management - what are your data needs?",
        help="Exact subject to search (AQS subject:\"...\")",
    )
    parser.add_argument(
        "--people",
        default="audrey,elise,bethany",
        help="Comma-separated name/email tokens to match senders (default: audrey,elise,bethany)",
    )
    args = parser.parse_args()

    subject = str(args.subject).strip()
    people_tokens = [t.strip() for t in str(args.people).split(",") if t.strip()]

    targets = [PersonHit(label=t.title(), match_tokens=[t.lower()]) for t in people_tokens]

    env = load_graph_env(REPO_ROOT)
    auth = GraphAuthenticator(repo_root=REPO_ROOT, env=env)
    client = GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )

    # Mailbox-wide search (includes Inbox subfolders).
    # Some tenants reject AQS field queries like subject:"..."; use phrase/keyword search and filter locally.
    headers = {"ConsistencyLevel": "eventual"}

    search_terms: List[str] = []
    subject_no_re = subject
    if subject_no_re.lower().startswith("re:"):
        subject_no_re = subject_no_re[3:].strip()

    # Try exact phrase first, then shorter phrase, then keywords.
    search_terms.append(f'"{subject}"')
    if subject_no_re != subject:
        search_terms.append(f'"{subject_no_re}"')
    search_terms.append('"FY27 Capital Budget Planning"')
    search_terms.append('FY27 Capital Budget Planning SC Data Management data needs')

    hits: List[Dict[str, Any]] = []
    for aqs in search_terms:
        hits = list(
            _iter_graph_paged(
                client,
                "me/messages",
                params={
                    "$search": aqs,
                    "$top": 50,
                    "$select": "id,subject,conversationId,receivedDateTime,from,bodyPreview",
                },
                headers=headers,
            )
        )
        if hits:
            break

    if not hits:
        print("No messages found by subject search.")
        return 0

    # Prefer hits whose subject matches closely.
    subj_norm = _norm(subject)
    subject_hits = [h for h in hits if subj_norm in _norm(str(h.get("subject") or ""))]
    pool = subject_hits or hits

    hits_sorted = sorted(pool, key=lambda m: _parse_dt(str(m.get("receivedDateTime") or "")), reverse=True)
    conv_id = str(hits_sorted[0].get("conversationId") or "").strip()
    if not conv_id:
        print("Found messages but no conversationId on results.")
        return 0

    conv_msgs = list(
        _iter_graph_paged(
            client,
            "me/messages",
            params={
                "$filter": f"conversationId eq '{conv_id}'",
                "$top": 200,
                "$select": "id,subject,conversationId,receivedDateTime,from,bodyPreview,body",
            },
        )
    )

    print(f"Thread subject match: {hits_sorted[0].get('subject')}")
    print(f"Conversation messages found: {len(conv_msgs)}")

    latest_by_token: Dict[str, Dict[str, Any]] = {}

    for msg in conv_msgs:
        sname = _norm(_sender_name(msg))
        saddr = _norm(_sender_addr(msg))
        for t in targets:
            token = t.match_tokens[0]
            if token in sname or token in saddr:
                prev = latest_by_token.get(token)
                if not prev or _parse_dt(str(msg.get("receivedDateTime") or "")) > _parse_dt(str(prev.get("receivedDateTime") or "")):
                    latest_by_token[token] = msg

    missing = [t.match_tokens[0] for t in targets if t.match_tokens[0] not in latest_by_token]
    if missing:
        print(f"WARNING: No replies matched for tokens: {', '.join(missing)}")

    def extract_need_lines(text: str) -> List[str]:
        lines = [ln.strip() for ln in text.splitlines()]
        keep: List[str] = []
        for ln in lines:
            if not ln:
                continue
            if re.match(r"^(?:[-*•]|\d+\)|\d+\.|\([a-zA-Z]\))\s+", ln):
                keep.append(ln)
        # If no bullets, return first non-empty lines as fallback.
        if keep:
            return keep[:40]
        fallback = [ln for ln in lines if ln][:12]
        return fallback

    for token in [t.match_tokens[0] for t in targets]:
        msg = latest_by_token.get(token)
        if not msg:
            continue

        dt = str(msg.get("receivedDateTime") or "")
        subj = str(msg.get("subject") or "")
        name = _sender_name(msg)
        addr = _sender_addr(msg)

        body = msg.get("body")
        body_text = ""
        if isinstance(body, dict):
            content = str(body.get("content") or "")
            ctype = str(body.get("contentType") or "").lower()
            body_text = _strip_html(content) if ctype == "html" else content

        if not body_text:
            body_text = str(msg.get("bodyPreview") or "")

        need_lines = extract_need_lines(body_text)

        print("\n---")
        print(f"{token.title()} — {name} <{addr}> — {dt}")
        print(f"Subject: {subj}")
        print("Extracted items:")
        for ln in need_lines:
            print(f"- {ln}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
