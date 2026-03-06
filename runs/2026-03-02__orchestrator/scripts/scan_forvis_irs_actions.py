from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# repo bootstrap
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import html_to_text, search_messages, search_sent_messages


def extract_action_excerpt(text: str) -> str:
    clean = re.sub(r"\s+", " ", text or "").strip()
    if not clean:
        return ""

    patterns = [
        r"([^\.\n]{0,200}\b(can you|could you|please|need you to|action required|respond|review|provide|send|confirm|complete)\b[^\.\n]{0,220}[\.?])",
        r"([^\.\n]{0,200}\bby\s+[A-Za-z]+\s+\d{1,2}\b[^\.\n]{0,220}[\.?])",
        r"([^\.\n]{0,200}\b(availability|meeting|artifact|documentation|deliver|submission)\b[^\.\n]{0,220}[\.?])",
    ]

    for pattern in patterns:
        match = re.search(pattern, clean, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return clean[:240] + ("..." if len(clean) > 240 else "")


def build_client(repo_root: Path) -> GraphAPIClient:
    env = load_graph_env(repo_root)
    authenticator = GraphAuthenticator(repo_root=repo_root, env=env)
    return GraphAPIClient(
        authenticator=authenticator,
        config=GraphClientConfig(
            base_url=env.base_url,
            scopes=env.scopes,
            planner_timezone=env.planner_timezone,
        ),
    )


def dt_of(message: Dict[str, Any]) -> str:
    return str(message.get("receivedDateTime") or message.get("sentDateTime") or "")


def fetch_conversation_messages(client: GraphAPIClient, conversation_id: str) -> List[Dict[str, Any]]:
    select_fields = (
        "id,subject,from,toRecipients,ccRecipients,receivedDateTime,sentDateTime,"
        "conversationId,bodyPreview,body"
    )
    safe_id = conversation_id.replace("'", "''")
    path = "me/messages"
    params = {
        "$top": 100,
        "$select": select_fields,
        "$filter": f"conversationId eq '{safe_id}'",
    }

    records: List[Dict[str, Any]] = []
    next_path = path
    next_params: Dict[str, Any] | None = params

    while next_path:
        payload = client.get(next_path, params=next_params)
        values = payload.get("value", []) if isinstance(payload, dict) else []
        if isinstance(values, list):
            for item in values:
                if isinstance(item, dict):
                    records.append(item)

        next_link = payload.get("@odata.nextLink") if isinstance(payload, dict) else None
        if isinstance(next_link, str) and next_link:
            next_path = next_link
            next_params = None
        else:
            next_path = ""

    return records


def main() -> int:
    repo_root = REPO_ROOT
    run_dir = repo_root / "runs" / "2026-03-02__orchestrator"
    exports_dir = run_dir / "exports"

    tasks_path = exports_dir / "todo_incomplete_all.json"
    if not tasks_path.exists():
        raise FileNotFoundError(f"Missing task export: {tasks_path}")

    all_tasks = json.loads(tasks_path.read_text(encoding="utf-8"))

    kw_re = re.compile(
        r"\b(forvis|f\s*-?\s*o\s*-?\s*r\s*-?\s*v\s*-?\s*i\s*-?\s*s|irs|audit)\b",
        re.IGNORECASE,
    )

    focus_tasks: List[Dict[str, Any]] = []
    for task in all_tasks:
        blob = " ".join(
            [
                str(task.get("title") or ""),
                str(task.get("body_full") or ""),
                str(task.get("body_preview") or ""),
                " ".join(task.get("categories") or []),
            ]
        )
        if kw_re.search(blob):
            focus_tasks.append(task)

    client = build_client(repo_root)
    me = client.me()
    my_email = str(me.get("mail") or me.get("userPrincipalName") or "").lower()

    queries = [
        '"Forvis"',
        '"F-O-R-V-I-S"',
        '"IRS audit"',
        '"IRS" AND "Forvis"',
    ]

    messages: List[Dict[str, Any]] = []
    seen_ids = set()

    for query in queries:
        for message in search_messages(client, query=query, top=50, max_messages=250):
            message_id = message.get("id")
            if message_id and message_id not in seen_ids:
                seen_ids.add(message_id)
                messages.append(message)
        for message in search_sent_messages(client, query=query, top=50, max_messages=250):
            message_id = message.get("id")
            if message_id and message_id not in seen_ids:
                seen_ids.add(message_id)
                messages.append(message)

    relevant_messages: List[Dict[str, Any]] = []
    for message in messages:
        from_obj = (message.get("from") or {}).get("emailAddress") or {}
        from_addr = str(from_obj.get("address") or "").lower()
        subject = str(message.get("subject") or "")
        body_preview = str(message.get("bodyPreview") or "")
        body = message.get("body") or {}
        body_text = html_to_text(str(body.get("content") or "")) if isinstance(body, dict) else ""

        blob = " ".join([subject, body_preview, body_text, from_addr]).lower()
        if ("forvis" in blob and ("irs" in blob or "audit" in blob)) or ("forvis.com" in from_addr):
            enriched = dict(message)
            enriched["_from_addr"] = from_addr
            enriched["_blob"] = blob
            relevant_messages.append(enriched)

    grouped_threads: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for message in relevant_messages:
        grouped_threads[str(message.get("conversationId") or message.get("id"))].append(message)

    action_pattern = re.compile(
        r"\?|\b(can you|could you|please|need you to|action required|respond|review|provide|send|confirm|complete)\b",
        re.IGNORECASE,
    )
    team_pattern = re.compile(
        r"\b(stephen|audrey|jesse|mike boyle|elise|bethany|justin|hannah|zach|michael de luna|stephanie)\b",
        re.IGNORECASE,
    )

    open_actions = []
    thread_summaries = []

    for conversation_id, thread_messages in grouped_threads.items():
        full_conversation = fetch_conversation_messages(client, conversation_id)
        if full_conversation:
            ordered = sorted(full_conversation, key=dt_of)
        else:
            ordered = sorted(thread_messages, key=dt_of)

        latest = ordered[-1]

        latest_from = str(latest.get("_from_addr") or "").lower()
        latest_subject = str(latest.get("subject") or "(no subject)")
        latest_datetime = dt_of(latest)

        latest_body = latest.get("body") or {}
        latest_body_text = html_to_text(str(latest_body.get("content") or "")) if isinstance(latest_body, dict) else ""

        latest_text = " ".join(
            [
                str(latest.get("subject") or ""),
                str(latest.get("bodyPreview") or ""),
                latest_body_text,
            ]
        )
        latest_preview = str(latest.get("bodyPreview") or "")
        action_excerpt = extract_action_excerpt(latest_preview or latest_text)

        awaiting_response = bool(latest_from and latest_from != my_email)
        has_explicit_ask = bool(action_pattern.search(latest_text))

        owner = "Matt"
        if team_pattern.search(latest_text):
            owner = "Team (named in thread)"
        if awaiting_response and has_explicit_ask and owner == "Matt":
            owner = "Matt (response likely needed)"

        confidence = "high" if (awaiting_response and has_explicit_ask) else "medium" if awaiting_response else "low"

        if awaiting_response:
            open_actions.append(
                {
                    "conversation_id": conversation_id,
                    "subject": latest_subject,
                    "latest_datetime": latest_datetime,
                    "latest_from": latest_from,
                    "owner": owner,
                    "confidence": confidence,
                    "why_open": "Latest relevant message is not from Matt"
                    + (" and contains an explicit ask/question." if has_explicit_ask else "."),
                    "action_excerpt": action_excerpt,
                    "latest_preview": latest_preview,
                    "thread_total_messages": len(ordered),
                }
            )

        thread_summaries.append(
            {
                "conversation_id": conversation_id,
                "subject_latest": latest_subject,
                "latest_datetime": latest_datetime,
                "latest_from": latest_from,
                "message_count": len(ordered),
            }
        )

    open_actions.sort(key=lambda x: str(x.get("latest_datetime") or ""), reverse=True)
    thread_summaries.sort(key=lambda x: str(x.get("latest_datetime") or ""), reverse=True)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "principal": my_email,
        "focus_task_count": len(focus_tasks),
        "focus_tasks": focus_tasks,
        "relevant_message_count": len(relevant_messages),
        "relevant_thread_count": len(thread_summaries),
        "open_action_count": len(open_actions),
        "open_actions": open_actions,
        "thread_summaries": thread_summaries,
    }

    out_json = exports_dir / "forvis_irs_open_actions_scan.json"
    out_md = exports_dir / "forvis_irs_open_actions_scan.md"

    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines: List[str] = []
    md_lines.append("# Forvis / IRS Audit — Open Actions Scan")
    md_lines.append("")
    md_lines.append(f"- Generated: {payload['generated_at_utc']}")
    md_lines.append(f"- Principal: {my_email}")
    md_lines.append(f"- Matching open To Do tasks: {len(focus_tasks)}")
    md_lines.append(f"- Relevant email messages: {len(relevant_messages)}")
    md_lines.append(f"- Relevant threads: {len(thread_summaries)}")
    md_lines.append(f"- Open actions inferred: {len(open_actions)}")
    md_lines.append("")
    md_lines.append("## Matching To Do Tasks")
    md_lines.append("")

    if focus_tasks:
        for task in focus_tasks:
            md_lines.append(
                f"- [{task.get('list_name', '?')}] {task.get('title', '(untitled)')} "
                f"(importance={task.get('importance', 'normal')}, due={task.get('due_date') or 'none'})"
            )
    else:
        md_lines.append("- None found.")

    md_lines.append("")
    md_lines.append("## Open Actions (needs response/follow-up)")
    md_lines.append("")

    if open_actions:
        for action in open_actions:
            md_lines.append(
                f"- {action['latest_datetime']} | {action['subject']} | from {action['latest_from']} | "
                f"owner={action['owner']} | confidence={action['confidence']} | {action['why_open']} | "
                f"action={action.get('action_excerpt','')}"
            )
    else:
        md_lines.append("- No open actions inferred from current Forvis/IRS thread set.")

    out_md.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(
        f"focus_tasks={len(focus_tasks)} relevant_messages={len(relevant_messages)} open_actions={len(open_actions)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
