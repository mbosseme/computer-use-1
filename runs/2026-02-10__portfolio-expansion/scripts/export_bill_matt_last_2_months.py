from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import export_thread_markdown, html_to_text, search_messages


MATT_ADDR = "matt_bossemeyer@premierinc.com"
BILL_ADDR = "bill_marquardt@premierinc.com"


def _emails(recipients):
    vals = []
    for item in recipients or []:
        addr = ((item or {}).get("emailAddress") or {}).get("address") or ""
        name = ((item or {}).get("emailAddress") or {}).get("name") or ""
        vals.append((name, addr))
    return vals


def _participants(msg):
    parts = set()
    sender = ((msg.get("from") or {}).get("emailAddress") or {}).get("address") or ""
    if sender:
        parts.add(sender.lower())
    for _, addr in _emails(msg.get("toRecipients") or []):
        if addr:
            parts.add(addr.lower())
    for _, addr in _emails(msg.get("ccRecipients") or []):
        if addr:
            parts.add(addr.lower())
    return parts


def _dt(msg):
    raw = (msg.get("receivedDateTime") or msg.get("sentDateTime") or "")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


def _line_recipients(recipients):
    out = []
    for name, addr in _emails(recipients):
        if name and addr and name != addr:
            out.append(f"{name} <{addr}>")
        elif addr:
            out.append(addr)
    return ", ".join(out)


def main() -> None:
    repo = Path(__file__).resolve().parents[3]
    run_id = "2026-02-10__portfolio-expansion"
    out_dir = repo / "runs" / run_id / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)

    env = load_graph_env(repo)
    auth = GraphAuthenticator(repo_root=repo, env=env)
    client = GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(
            base_url=env.base_url,
            scopes=env.scopes,
            planner_timezone=env.planner_timezone,
        ),
    )

    # Thread export first (subject-substring search in helper)
    thread_path = out_dir / "m365_threads" / "re_admin_fee_data_discovery.md"
    thread_path.parent.mkdir(parents=True, exist_ok=True)
    export_thread_markdown(
        client,
        subject="Admin Fee Data Discovery",
        out_path=thread_path,
        max_messages=150,
        timeout_s=120,
    )

    # Broad mailbox search, then deterministic local filtering
    query = '"Bill Marquardt" OR "Bill_Marquardt@PremierInc.com" OR "Matt_Bossemeyer@PremierInc.com"'
    messages = search_messages(client, query=query, top=100, max_messages=1200, timeout_s=120)

    cutoff = datetime.now(timezone.utc) - timedelta(days=62)

    selected = []
    for msg in messages:
        timestamp = _dt(msg)
        if timestamp is None or timestamp < cutoff:
            continue
        participants = _participants(msg)
        if MATT_ADDR not in participants or BILL_ADDR not in participants:
            continue

        selected.append(
            {
                "id": msg.get("id"),
                "subject": msg.get("subject"),
                "receivedDateTime": msg.get("receivedDateTime"),
                "sentDateTime": msg.get("sentDateTime"),
                "conversationId": msg.get("conversationId"),
                "from": ((msg.get("from") or {}).get("emailAddress") or {}),
                "to": _emails(msg.get("toRecipients") or []),
                "cc": _emails(msg.get("ccRecipients") or []),
                "hasAttachments": msg.get("hasAttachments", False),
                "bodyPreview": msg.get("bodyPreview") or "",
                "bodyText": html_to_text(((msg.get("body") or {}).get("content") or "")),
            }
        )

    selected.sort(key=lambda x: x.get("receivedDateTime") or x.get("sentDateTime") or "", reverse=True)

    json_path = out_dir / "bill_matt_last_2_months_graph.json"
    json_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")

    md_path = out_dir / "bill_matt_last_2_months_graph.md"
    lines = [
        "# Bill <-> Matt Emails (Last 2 Months)",
        f"_Generated UTC: {datetime.now(timezone.utc).isoformat()}_",
        f"_Message count: {len(selected)}_",
        "",
    ]
    for item in selected:
        sender = item.get("from") or {}
        from_line = f"{sender.get('name') or ''} <{sender.get('address') or ''}>".strip()
        lines.extend(
            [
                f"## {item.get('subject') or '(no subject)'}",
                f"- Sent: {item.get('sentDateTime')}",
                f"- Received: {item.get('receivedDateTime')}",
                f"- From: {from_line}",
                f"- To: {_line_recipients([{'emailAddress': {'name': n, 'address': a}} for n, a in item.get('to', [])])}",
                f"- Cc: {_line_recipients([{'emailAddress': {'name': n, 'address': a}} for n, a in item.get('cc', [])])}",
                f"- Conversation ID: {item.get('conversationId')}",
                "",
                "### Preview",
                item.get("bodyPreview") or "",
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(thread_path)
    print(json_path)
    print(md_path)
    print(f"selected={len(selected)}")


if __name__ == "__main__":
    main()
