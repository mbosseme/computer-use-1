from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _parse_iso(iso_value: str) -> Optional[datetime]:
    if not iso_value:
        return None
    value = iso_value.replace("Z", "+00:00")
    if "." in value:
        head, tail = value.split(".", 1)
        frac = ""
        rest = ""
        for index, char in enumerate(tail):
            if char.isdigit():
                frac += char
            else:
                rest = tail[index:]
                break
        if len(frac) > 6:
            frac = frac[:6]
        value = f"{head}.{frac}{rest}" if frac else f"{head}{rest}"
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _to_email_list(recipients: Any) -> List[str]:
    values: List[str] = []
    if not isinstance(recipients, list):
        return values
    for entry in recipients:
        if not isinstance(entry, dict):
            continue
        email_address = entry.get("emailAddress")
        if not isinstance(email_address, dict):
            continue
        address = email_address.get("address")
        if isinstance(address, str) and address.strip():
            values.append(address.strip().lower())
    return values


def _from_email(message: Dict[str, Any]) -> str:
    from_obj = message.get("from")
    if isinstance(from_obj, dict):
        email_address = from_obj.get("emailAddress")
        if isinstance(email_address, dict):
            address = email_address.get("address")
            if isinstance(address, str):
                return address.strip().lower()
    return ""


def _iter_graph_paged(
    client: GraphAPIClient,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    next_path: str = path
    next_params: Optional[Dict[str, Any]] = params

    while True:
        payload = client.get(next_path, params=next_params)
        values = payload.get("value", []) if isinstance(payload, dict) else []
        if isinstance(values, list):
            for item in values:
                if isinstance(item, dict):
                    records.append(item)

        next_link = payload.get("@odata.nextLink") if isinstance(payload, dict) else None
        if not isinstance(next_link, str) or not next_link:
            break
        next_path = next_link
        next_params = None

    return records


@dataclass
class WindowConfig:
    past_days: int = 30
    future_days: int = 30


def main() -> int:
    repo_root = _repo_root()
    run_dir = repo_root / "runs" / "2026-03-02__orchestrator"
    exports_dir = run_dir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

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
    principal = me.get("userPrincipalName") or me.get("mail") or "unknown"

    window = WindowConfig()
    now_utc = datetime.now(timezone.utc).replace(microsecond=0)
    past_start = now_utc - timedelta(days=window.past_days)
    future_end = now_utc + timedelta(days=window.future_days)

    start_iso = past_start.isoformat().replace("+00:00", "Z")
    end_iso = future_end.isoformat().replace("+00:00", "Z")
    now_iso = now_utc.isoformat().replace("+00:00", "Z")

    select_mail = (
        "id,subject,receivedDateTime,sentDateTime,from,toRecipients,ccRecipients,"
        "conversationId,hasAttachments,importance,bodyPreview"
    )

    inbox_messages = _iter_graph_paged(
        client,
        "me/mailFolders/Inbox/messages",
        params={
            "$top": 100,
            "$orderby": "receivedDateTime desc",
            "$select": select_mail,
            "$filter": f"receivedDateTime ge {start_iso}",
        },
    )

    sent_messages = _iter_graph_paged(
        client,
        "me/mailFolders/SentItems/messages",
        params={
            "$top": 100,
            "$orderby": "sentDateTime desc",
            "$select": select_mail,
            "$filter": f"sentDateTime ge {start_iso}",
        },
    )

    calendar_events = _iter_graph_paged(
        client,
        "me/calendarView",
        params={
            "startDateTime": start_iso,
            "endDateTime": end_iso,
            "$top": 1000,
            "$select": "id,subject,start,end,isAllDay,showAs,organizer,attendees,location,bodyPreview",
            "$orderby": "start/dateTime",
        },
    )

    recent_inbox_senders = Counter([_from_email(m) for m in inbox_messages if _from_email(m)])
    recent_sent_recipients: Counter[str] = Counter()
    for message in sent_messages:
        for recipient in _to_email_list(message.get("toRecipients")):
            recent_sent_recipients[recipient] += 1

    upcoming_events: List[Dict[str, Any]] = []
    past_events: List[Dict[str, Any]] = []
    for event in calendar_events:
        start_obj = event.get("start") if isinstance(event.get("start"), dict) else {}
        start_dt = _parse_iso(str(start_obj.get("dateTime") or ""))
        if start_dt is None:
            continue
        normalized = start_dt if start_dt.tzinfo else start_dt.replace(tzinfo=timezone.utc)
        if normalized >= now_utc:
            upcoming_events.append(event)
        else:
            past_events.append(event)

    output_payload = {
        "generated_at_utc": now_iso,
        "principal": principal,
        "window": {
            "past_days": window.past_days,
            "future_days": window.future_days,
            "past_start_utc": start_iso,
            "future_end_utc": end_iso,
        },
        "counts": {
            "inbox_messages": len(inbox_messages),
            "sent_messages": len(sent_messages),
            "calendar_events_total": len(calendar_events),
            "calendar_events_past": len(past_events),
            "calendar_events_upcoming": len(upcoming_events),
        },
        "top_inbox_senders": recent_inbox_senders.most_common(25),
        "top_sent_recipients": recent_sent_recipients.most_common(25),
        "inbox_messages": inbox_messages,
        "sent_messages": sent_messages,
        "calendar_events": calendar_events,
    }

    raw_json_path = exports_dir / "graph_context_30d_raw.json"
    raw_json_path.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")

    summary_lines = [
        "# Graph Context Snapshot (Past 30 / Next 30)",
        "",
        f"- Principal: {principal}",
        f"- Generated (UTC): {now_iso}",
        f"- Inbox messages (30d): {len(inbox_messages)}",
        f"- Sent messages (30d): {len(sent_messages)}",
        f"- Calendar events in window: {len(calendar_events)}",
        f"- Past events: {len(past_events)}",
        f"- Upcoming events: {len(upcoming_events)}",
        "",
        "## Top Inbox Senders",
        "",
    ]

    for sender, count in recent_inbox_senders.most_common(15):
        summary_lines.append(f"- {sender}: {count}")

    summary_lines.extend(["", "## Top Sent Recipients", ""])
    for recipient, count in recent_sent_recipients.most_common(15):
        summary_lines.append(f"- {recipient}: {count}")

    summary_md_path = exports_dir / "graph_context_30d_summary.md"
    summary_md_path.write_text("\n".join(summary_lines), encoding="utf-8")

    print(f"Wrote: {raw_json_path}")
    print(f"Wrote: {summary_md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
