from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import search_messages, html_to_text


RUN_ID = "2026-02-10__portfolio-expansion"
REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_ROOT = REPO_ROOT / "runs" / RUN_ID
EXPORT_DIR = RUN_ROOT / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

RAW_JSON_PATH = EXPORT_DIR / "m365_context_raw.json"
SUMMARY_MD_PATH = EXPORT_DIR / "m365_context_summary.md"

PROJECT_KEYWORDS = [
    "portfolio expansion",
    "heat map",
    "non-clinical",
    "clinical",
    "workflow history",
    "tsa",
    "service line",
    "fusion team",
    "gpo",
    "spend",
]

TARGET_PEOPLE = {
    "zach_lilly": ["zach lilly", "lilly/zach", "zach"],
    "brian_hall": ["brian hall", "brian"],
    "jennie_hendrix": ["jennie hendrix", "jenny/brian", "jennie", "jenny"],
    "jordan_garrett": ["jordan garrett", "jordan"],
}

PRIORITY_EMAIL_SENDERS = {
    "bill_marquardt": ["bill marquardt", "w marquardt", "marquardt"],
    "bruce_radcliff": ["bruce radcliff", "radcliff"],
    "brian_hall": ["brian hall", "brian"],
}

SEARCH_QUERIES = [
    '"Portfolio Expansion"',
    '"Fusion Team Weekly Check-in"',
    '"Heat Map"',
    '"on/off/non-contract"',
    '"service line"',
    '"Jordan Garrett"',
    '"Zach Lilly"',
    '"Brian Hall"',
    '"Jennie Hendrix"',
    '"Bill Marquardt"',
    '"Bruce Radcliff"',
]


@dataclass
class MessageRecord:
    id: str
    subject: str
    received: str
    sent: str
    conversation_id: str
    sender_name: str
    sender_address: str
    to_recipients: List[str]
    cc_recipients: List[str]
    has_attachments: bool
    body_preview: str
    body_text: str
    internet_message_id: str


@dataclass
class EventRecord:
    id: str
    subject: str
    start: str
    end: str
    organizer: str
    attendees: List[str]
    body_preview: str


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def recipient_strings(recipients: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(recipients, list):
        return out
    for recipient in recipients:
        email_address = (recipient or {}).get("emailAddress") or {}
        name = str(email_address.get("name") or "").strip()
        address = str(email_address.get("address") or "").strip()
        if name and address:
            out.append(f"{name} <{address}>")
        elif address:
            out.append(address)
        elif name:
            out.append(name)
    return out


def get_sender(msg: Dict[str, Any]) -> Tuple[str, str]:
    from_obj = msg.get("from") or {}
    email_address = from_obj.get("emailAddress") if isinstance(from_obj, dict) else {}
    if not isinstance(email_address, dict):
        return "", ""
    return str(email_address.get("name") or ""), str(email_address.get("address") or "")


def to_message_record(msg: Dict[str, Any]) -> MessageRecord:
    sender_name, sender_address = get_sender(msg)
    body_html = ((msg.get("body") or {}).get("content") or "") if isinstance(msg.get("body"), dict) else ""
    return MessageRecord(
        id=str(msg.get("id") or ""),
        subject=str(msg.get("subject") or ""),
        received=str(msg.get("receivedDateTime") or ""),
        sent=str(msg.get("sentDateTime") or ""),
        conversation_id=str(msg.get("conversationId") or ""),
        sender_name=sender_name,
        sender_address=sender_address,
        to_recipients=recipient_strings(msg.get("toRecipients")),
        cc_recipients=recipient_strings(msg.get("ccRecipients")),
        has_attachments=bool(msg.get("hasAttachments")),
        body_preview=str(msg.get("bodyPreview") or ""),
        body_text=html_to_text(body_html),
        internet_message_id=str(msg.get("internetMessageId") or ""),
    )


def message_blob(rec: MessageRecord) -> str:
    return normalize_text(
        "\n".join(
            [
                rec.subject,
                rec.sender_name,
                rec.sender_address,
                rec.body_preview,
                rec.body_text,
                " ".join(rec.to_recipients),
                " ".join(rec.cc_recipients),
            ]
        )
    )


def has_project_signal(rec: MessageRecord) -> bool:
    blob = message_blob(rec)
    return any(keyword in blob for keyword in PROJECT_KEYWORDS)


def find_people_hits(rec: MessageRecord, people_map: Dict[str, List[str]]) -> List[str]:
    blob = message_blob(rec)
    hits: List[str] = []
    for key, aliases in people_map.items():
        if any(alias in blob for alias in aliases):
            hits.append(key)
    return hits


def sort_by_recency(messages: List[MessageRecord]) -> List[MessageRecord]:
    def dt_key(rec: MessageRecord) -> str:
        return rec.received or rec.sent or ""

    return sorted(messages, key=dt_key, reverse=True)


def shorten(text: str, limit: int = 280) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def collect_messages(client: GraphAPIClient) -> Dict[str, MessageRecord]:
    records: Dict[str, MessageRecord] = {}
    for query in SEARCH_QUERIES:
        try:
            messages = search_messages(
                client,
                query=query,
                top=50,
                max_messages=300,
                timeout_s=120,
            )
        except Exception:
            continue
        for msg in messages:
            rec = to_message_record(msg)
            if rec.id:
                records[rec.id] = rec
    return records


def collect_calendar_events(client: GraphAPIClient) -> List[EventRecord]:
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=180)).isoformat()
    end = (now + timedelta(days=30)).isoformat()
    try:
        data = client.get(
            "me/calendarView",
            params={
                "startDateTime": start,
                "endDateTime": end,
                "$top": 1000,
                "$select": "id,subject,start,end,organizer,attendees,bodyPreview",
            },
            timeout=120,
        )
    except Exception:
        return []

    events: List[EventRecord] = []
    for row in data.get("value", []) if isinstance(data, dict) else []:
        organizer_obj = ((row.get("organizer") or {}).get("emailAddress") or {}) if isinstance(row.get("organizer"), dict) else {}
        organizer = str(organizer_obj.get("name") or organizer_obj.get("address") or "")
        attendees: List[str] = []
        for attendee in row.get("attendees", []) if isinstance(row.get("attendees"), list) else []:
            ea = (attendee or {}).get("emailAddress") or {}
            name = str(ea.get("name") or "").strip()
            address = str(ea.get("address") or "").strip()
            if name and address:
                attendees.append(f"{name} <{address}>")
            elif address:
                attendees.append(address)
            elif name:
                attendees.append(name)

        events.append(
            EventRecord(
                id=str(row.get("id") or ""),
                subject=str(row.get("subject") or ""),
                start=str(((row.get("start") or {}).get("dateTime") if isinstance(row.get("start"), dict) else "") or ""),
                end=str(((row.get("end") or {}).get("dateTime") if isinstance(row.get("end"), dict) else "") or ""),
                organizer=organizer,
                attendees=attendees,
                body_preview=str(row.get("bodyPreview") or ""),
            )
        )

    return events


def main() -> None:
    env = load_graph_env(REPO_ROOT)
    auth = GraphAuthenticator(repo_root=REPO_ROOT, env=env)
    client = GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(
            base_url=env.base_url,
            scopes=env.scopes,
            planner_timezone=env.planner_timezone,
        ),
    )

    me = client.me()
    me_upn = str(me.get("userPrincipalName") or me.get("mail") or me.get("id") or "unknown")

    messages_by_id = collect_messages(client)
    all_messages = sort_by_recency(list(messages_by_id.values()))

    sender_hits: Dict[str, List[MessageRecord]] = defaultdict(list)
    people_hits: Dict[str, List[MessageRecord]] = defaultdict(list)
    project_messages: List[MessageRecord] = []

    for rec in all_messages:
        blob = message_blob(rec)

        if has_project_signal(rec):
            project_messages.append(rec)

        for sender_key, aliases in PRIORITY_EMAIL_SENDERS.items():
            sender_blob = normalize_text(f"{rec.sender_name} {rec.sender_address}")
            if any(alias in sender_blob for alias in aliases):
                sender_hits[sender_key].append(rec)

        for person_key in find_people_hits(rec, TARGET_PEOPLE):
            people_hits[person_key].append(rec)

    events = collect_calendar_events(client)

    target_event_terms = [
        "fusion team weekly check-in",
        "portfolio expansion",
        "heat map",
        "service line",
    ]

    relevant_events = []
    for event in events:
        event_blob = normalize_text(
            " ".join([event.subject, event.organizer, event.body_preview, " ".join(event.attendees)])
        )
        if any(term in event_blob for term in target_event_terms):
            relevant_events.append(event)

    relevant_events = sorted(relevant_events, key=lambda e: e.start, reverse=True)

    payload = {
        "run_id": RUN_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "user": me_upn,
        "scope_check": {
            "granted_scopes": env.scopes,
            "teams_chat_access": "unavailable_missing_scopes",
            "required_scopes_for_chat": ["Chat.ReadBasic", "Chat.Read", "Chat.ReadWrite"],
        },
        "counts": {
            "queried_messages_unique": len(all_messages),
            "project_signal_messages": len(project_messages),
            "priority_sender_hits": {k: len(v) for k, v in sender_hits.items()},
            "target_people_mentions": {k: len(v) for k, v in people_hits.items()},
            "relevant_calendar_events": len(relevant_events),
        },
        "project_messages": [rec.__dict__ for rec in project_messages[:250]],
        "priority_sender_messages": {
            key: [rec.__dict__ for rec in sort_by_recency(value)[:150]]
            for key, value in sender_hits.items()
        },
        "target_people_messages": {
            key: [rec.__dict__ for rec in sort_by_recency(value)[:150]]
            for key, value in people_hits.items()
        },
        "relevant_calendar_events": [event.__dict__ for event in relevant_events[:200]],
    }

    RAW_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# M365 Context Collection — Portfolio Expansion")
    lines.append("")
    lines.append(f"Generated (UTC): {payload['generated_at_utc']}")
    lines.append(f"Mailbox: {me_upn}")
    lines.append("")
    lines.append("## Access & Limitations")
    lines.append("")
    lines.append("- Mail + Calendar access succeeded via Microsoft Graph delegated auth.")
    lines.append("- Teams chat extraction is blocked in this token: missing `Chat.Read*` scopes.")
    lines.append("- This report uses mailbox + calendar artifacts as the best available context proxy for Teams conversations.")
    lines.append("")

    lines.append("## Coverage Summary")
    lines.append("")
    lines.append(f"- Unique messages pulled across search set: {payload['counts']['queried_messages_unique']}")
    lines.append(f"- Messages with project signal keywords: {payload['counts']['project_signal_messages']}")
    lines.append(f"- Relevant calendar events: {payload['counts']['relevant_calendar_events']}")
    lines.append("- Priority sender hit counts:")
    for key, value in payload["counts"]["priority_sender_hits"].items():
        lines.append(f"  - {key}: {value}")
    lines.append("- Target people mention counts:")
    for key, value in payload["counts"]["target_people_mentions"].items():
        lines.append(f"  - {key}: {value}")
    lines.append("")

    lines.append("## Priority Sender Emails (Most Recent)")
    lines.append("")
    for sender_key in ["bill_marquardt", "bruce_radcliff", "brian_hall"]:
        records = sort_by_recency(sender_hits.get(sender_key, []))[:20]
        lines.append(f"### {sender_key}")
        if not records:
            lines.append("- No matching messages found in this pass.")
        else:
            for rec in records:
                lines.append(
                    f"- {rec.received or rec.sent} | {rec.sender_name} <{rec.sender_address}> | {rec.subject}"
                )
                lines.append(f"  - Preview: {shorten(rec.body_preview or rec.body_text, 220)}")
        lines.append("")

    lines.append("## Messages Mentioning Target Team Members (Most Recent)")
    lines.append("")
    for person_key in ["zach_lilly", "brian_hall", "jennie_hendrix", "jordan_garrett"]:
        records = sort_by_recency(people_hits.get(person_key, []))[:20]
        lines.append(f"### {person_key}")
        if not records:
            lines.append("- No matching messages found in this pass.")
        else:
            for rec in records:
                lines.append(
                    f"- {rec.received or rec.sent} | {rec.sender_name} <{rec.sender_address}> | {rec.subject}"
                )
                lines.append(f"  - Preview: {shorten(rec.body_preview or rec.body_text, 220)}")
        lines.append("")

    lines.append("## Calendar Events Relevant to Project / Fusion Team")
    lines.append("")
    if not relevant_events:
        lines.append("- No matching calendar events found in the last 180 days + next 30 days window.")
    else:
        for event in relevant_events[:50]:
            attendees_short = ", ".join(event.attendees[:6])
            lines.append(
                f"- {event.start} to {event.end} | {event.subject} | Organizer: {event.organizer}"
            )
            if attendees_short:
                lines.append(f"  - Attendees: {shorten(attendees_short, 240)}")
            if event.body_preview:
                lines.append(f"  - Preview: {shorten(event.body_preview, 220)}")

    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(f"- Raw JSON: {RAW_JSON_PATH}")
    lines.append(f"- Summary: {SUMMARY_MD_PATH}")

    SUMMARY_MD_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {RAW_JSON_PATH}")
    print(f"Wrote {SUMMARY_MD_PATH}")


if __name__ == "__main__":
    main()
