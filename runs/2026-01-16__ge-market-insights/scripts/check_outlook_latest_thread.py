#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def _iso_dt(msg: Dict[str, Any]) -> str:
    return str(msg.get("receivedDateTime") or msg.get("sentDateTime") or "")


def _addr(obj: Any) -> str:
    if not isinstance(obj, dict):
        return ""
    ea = obj.get("emailAddress")
    if not isinstance(ea, dict):
        return ""
    addr = ea.get("address")
    name = ea.get("name")
    if isinstance(name, str) and isinstance(addr, str) and name and addr and name != addr:
        return f"{name} <{addr}>"
    return str(addr or "")


def _addr_list(recipients: Any) -> List[str]:
    if not isinstance(recipients, list):
        return []
    out: List[str] = []
    for r in recipients:
        s = _addr(r)
        if s:
            out.append(s)
    return out


def _haystack(msg: Dict[str, Any]) -> str:
    parts = [
        _addr(msg.get("from") or {}),
        " ".join(_addr_list(msg.get("toRecipients"))),
        " ".join(_addr_list(msg.get("ccRecipients"))),
        str(msg.get("subject") or ""),
    ]
    return " ".join(parts).lower()


def _search_messages(
    client: GraphAPIClient,
    *,
    query: str,
    top: int,
    select_fields: str,
) -> List[Dict[str, Any]]:
    resp = client.get(
        "me/messages",
        params={
            "$search": query,
            "$top": int(top),
            "$select": select_fields,
        },
        headers={"ConsistencyLevel": "eventual"},
    )
    items = resp.get("value", []) if isinstance(resp, dict) else []
    return [m for m in items if isinstance(m, dict)]


def _format_dt(iso: str) -> str:
    if not iso:
        return ""
    try:
        s = iso.replace("Z", "+00:00")
        return datetime.fromisoformat(s).isoformat(timespec="minutes")
    except Exception:
        return iso


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find the most recent Outlook email thread matching a contact (via Microsoft Graph)."
    )
    parser.add_argument(
        "--name",
        default="Selina",
        help="Contact name to search for (default: Selina)",
    )
    parser.add_argument(
        "--domain",
        default="ge.com",
        help="Optional domain hint to prefer matches (default: ge.com)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="How many search hits to pull before picking the latest (default: 50)",
    )
    parser.add_argument(
        "--max-thread",
        type=int,
        default=200,
        help="Max messages to fetch for the thread once conversationId is known (default: 200)",
    )
    args = parser.parse_args()

    env = load_graph_env(REPO_ROOT)

    client = GraphAPIClient(
        authenticator=GraphAuthenticator(repo_root=REPO_ROOT, env=env),
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )

    select_fields = (
        "id,subject,conversationId,receivedDateTime,sentDateTime,from,toRecipients,ccRecipients,bodyPreview"
    )

    # Broad query; we'll refine locally.
    query = f'"{args.name}"'
    hits = _search_messages(client, query=query, top=args.top, select_fields=select_fields)

    if not hits:
        print(f"No messages found for search {query} (top={args.top}).")
        return 0

    # Prefer messages where the contact name appears in participant fields and domain hint matches.
    name_l = str(args.name).lower()
    domain_l = str(args.domain or "").lower().strip()

    preferred: List[Dict[str, Any]] = []
    for m in hits:
        hay = _haystack(m)
        if name_l in hay and (not domain_l or domain_l in hay):
            preferred.append(m)

    candidates = preferred if preferred else hits
    candidates.sort(key=_iso_dt, reverse=True)

    latest = candidates[0]
    conv_id = latest.get("conversationId")

    print("Most recent matching message:")
    print(f"- When: {_format_dt(_iso_dt(latest))}")
    print(f"- Subject: {latest.get('subject') or '(no subject)'}")
    print(f"- From: {_addr(latest.get('from'))}")
    print(f"- To: {', '.join(_addr_list(latest.get('toRecipients')))}")
    preview = (latest.get("bodyPreview") or "").strip().replace("\n", " ")
    if preview:
        print(f"- Preview: {preview[:220]}")

    if not isinstance(conv_id, str) or not conv_id:
        print("\nNo conversationId found on that message; cannot expand thread reliably.")
        return 0

    # Expand thread by conversationId.
    thread_resp = client.get(
        "me/messages",
        params={
            "$filter": f"conversationId eq '{conv_id}'",
            "$top": int(args.max_thread),
            "$select": select_fields,
        },
    )
    thread_items = thread_resp.get("value", []) if isinstance(thread_resp, dict) else []
    thread = [m for m in thread_items if isinstance(m, dict)]
    thread.sort(key=_iso_dt)

    print(f"\nThread messages found: {len(thread)}")
    # Print a compact tail of the thread.
    tail = thread[-10:]
    start_idx = max(1, len(thread) - len(tail) + 1)
    for idx, m in enumerate(tail, start=start_idx):
        print(f"[{idx}] {_format_dt(_iso_dt(m))} | {m.get('subject') or '(no subject)'}")
        print(f"    From: {_addr(m.get('from'))}")
        prev = (m.get("bodyPreview") or "").strip().replace("\n", " ")
        if prev:
            print(f"    Preview: {prev[:220]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
