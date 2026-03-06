from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import search_messages


REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_DIR = REPO_ROOT / "runs" / "2026-03-02__orchestrator"
EXPORT_JSON = RUN_DIR / "exports" / "graph_search_diagnostics.json"
EXPORT_MD = RUN_DIR / "exports" / "graph_search_diagnostics.md"


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


def _next_link(resp: Dict[str, Any]) -> Optional[str]:
    v = resp.get("@odata.nextLink")
    return v if isinstance(v, str) and v else None


def _iso_to_dt(v: str) -> Optional[datetime]:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except Exception:
        return None


def sample_mailbox_history(client: GraphAPIClient, max_pages: int = 20, page_size: int = 250) -> Dict[str, Any]:
    path = "me/messages"
    params: Optional[Dict[str, Any]] = {
        "$select": "id,subject,receivedDateTime,sentDateTime,from,internetMessageId",
        "$orderby": "receivedDateTime desc",
        "$top": page_size,
    }

    records: List[Dict[str, Any]] = []
    pages = 0

    while path and pages < max_pages:
        resp = client.get(path, params=params, timeout=90)
        pages += 1
        values = resp.get("value") if isinstance(resp, dict) else None
        if isinstance(values, list):
            records.extend([v for v in values if isinstance(v, dict)])
        path = _next_link(resp) or ""
        params = None

    dts = [_iso_to_dt(str(r.get("receivedDateTime") or r.get("sentDateTime") or "")) for r in records]
    dts = [d for d in dts if d is not None]

    oldest = min(dts).isoformat() if dts else None
    newest = max(dts).isoformat() if dts else None

    return {
        "pages_fetched": pages,
        "messages_fetched": len(records),
        "oldest_message_dt": oldest,
        "newest_message_dt": newest,
        "sample_subjects": [str(r.get("subject") or "") for r in records[:5]],
    }


def probe_long_history(client: GraphAPIClient, max_pages: int = 140, page_size: int = 250) -> Dict[str, Any]:
    path = "me/messages"
    params: Optional[Dict[str, Any]] = {
        "$select": "id,receivedDateTime,sentDateTime",
        "$orderby": "receivedDateTime desc",
        "$top": page_size,
    }

    pages = 0
    total = 0
    oldest_dt: Optional[datetime] = None

    while path and pages < max_pages:
        resp = client.get(path, params=params, timeout=90)
        pages += 1
        values = resp.get("value") if isinstance(resp, dict) else None
        batch = [v for v in values if isinstance(v, dict)] if isinstance(values, list) else []
        total += len(batch)

        for row in batch:
            dt = _iso_to_dt(str(row.get("receivedDateTime") or row.get("sentDateTime") or ""))
            if dt and (oldest_dt is None or dt < oldest_dt):
                oldest_dt = dt

        path = _next_link(resp) or ""
        params = None

    return {
        "pages_fetched": pages,
        "messages_fetched": total,
        "oldest_message_dt": oldest_dt.isoformat() if oldest_dt else None,
    }


def test_older_date_slice(client: GraphAPIClient, before_iso: str = "2024-01-01T00:00:00Z") -> Dict[str, Any]:
    params = {
        "$top": 50,
        "$select": "id,subject,receivedDateTime,sentDateTime,from,bodyPreview",
        "$filter": f"receivedDateTime lt {before_iso}",
        "$orderby": "receivedDateTime desc",
    }

    resp = client.get("me/messages", params=params, timeout=90)
    values = resp.get("value") if isinstance(resp, dict) else []
    msgs = [v for v in values if isinstance(v, dict)] if isinstance(values, list) else []

    return {
        "before_iso": before_iso,
        "count": len(msgs),
        "sample_subjects": [str(m.get("subject") or "") for m in msgs[:8]],
        "sample_dates": [str(m.get("receivedDateTime") or m.get("sentDateTime") or "") for m in msgs[:8]],
    }


def test_aqs_search(client: GraphAPIClient, query: str, folder: Optional[str], top: int = 50) -> Dict[str, Any]:
    try:
        msgs = search_messages(client, query=query, folder=folder, top=top, max_messages=top)
    except Exception as exc:
        return {
            "query": query,
            "folder": folder,
            "count": 0,
            "unique_ids": 0,
            "sample_subjects": [],
            "sample_dates": [],
            "error": str(exc),
        }
    ids = [str(m.get("id") or "") for m in msgs if m.get("id")]
    subjects = [str(m.get("subject") or "") for m in msgs[:5]]
    dts = [str(m.get("receivedDateTime") or m.get("sentDateTime") or "") for m in msgs[:5]]
    return {
        "query": query,
        "folder": folder,
        "count": len(msgs),
        "unique_ids": len(set(ids)),
        "sample_subjects": subjects,
        "sample_dates": dts,
    }


def test_search_api_messages(client: GraphAPIClient, query: str, size: int = 50) -> Dict[str, Any]:
    payload = {
        "requests": [
            {
                "entityTypes": ["message"],
                "query": {"queryString": query},
                "from": 0,
                "size": size,
                "fields": [
                    "id",
                    "subject",
                    "receivedDateTime",
                    "from",
                    "bodyPreview",
                    "internetMessageId",
                ],
            }
        ]
    }

    resp = client.post("search/query", json=payload, timeout=120)
    container = (((resp.get("value") or [{}])[0]).get("hitsContainers") or [{}])[0]
    hits = container.get("hits") or []

    resources = []
    for hit in hits:
        if isinstance(hit, dict) and isinstance(hit.get("resource"), dict):
            resources.append(hit["resource"])

    return {
        "query": query,
        "count": len(resources),
        "sample_subjects": [str(r.get("subject") or "") for r in resources[:5]],
        "sample_dates": [str(r.get("receivedDateTime") or "") for r in resources[:5]],
    }


def test_search_api_events(client: GraphAPIClient, query: str, size: int = 25) -> Dict[str, Any]:
    payload = {
        "requests": [
            {
                "entityTypes": ["event"],
                "query": {"queryString": query},
                "from": 0,
                "size": size,
                "fields": [
                    "id",
                    "subject",
                    "start",
                    "end",
                    "bodyPreview",
                    "organizer",
                    "lastModifiedDateTime",
                ],
            }
        ]
    }

    resp = client.post("search/query", json=payload, timeout=120)
    container = (((resp.get("value") or [{}])[0]).get("hitsContainers") or [{}])[0]
    hits = container.get("hits") or []

    resources = []
    for hit in hits:
        if isinstance(hit, dict) and isinstance(hit.get("resource"), dict):
            resources.append(hit["resource"])

    return {
        "query": query,
        "count": len(resources),
        "sample_subjects": [str(r.get("subject") or "") for r in resources[:8]],
    }


def test_meeting_invite_messages(client: GraphAPIClient, top: int = 50) -> Dict[str, Any]:
    # Meeting invites are stored as mail messages with messageClass values such as IPM.Schedule.Meeting.Request.
    params = {
        "$top": top,
        "$select": "id,subject,receivedDateTime,messageClass,bodyPreview,from",
        "$filter": "messageClass eq 'IPM.Schedule.Meeting.Request'",
        "$orderby": "receivedDateTime desc",
    }

    try:
        resp = client.get("me/messages", params=params, timeout=90)
        values = resp.get("value") if isinstance(resp, dict) else []
        msgs = [v for v in values if isinstance(v, dict)] if isinstance(values, list) else []
        classes = Counter(str(m.get("messageClass") or "") for m in msgs)
        return {
            "count": len(msgs),
            "message_class_counts": dict(classes),
            "sample_subjects": [str(m.get("subject") or "") for m in msgs[:10]],
        }
    except Exception as exc:
        return {"count": 0, "error": str(exc)}


def test_calendar_event_bodies(client: GraphAPIClient, top: int = 80) -> Dict[str, Any]:
    params = {
        "$top": top,
        "$select": "id,subject,start,end,bodyPreview,lastModifiedDateTime,organizer,isCancelled",
        "$orderby": "lastModifiedDateTime desc",
    }

    resp = client.get("me/events", params=params, timeout=90)
    values = resp.get("value") if isinstance(resp, dict) else []
    events = [v for v in values if isinstance(v, dict)] if isinstance(values, list) else []
    with_body = [e for e in events if str(e.get("bodyPreview") or "").strip()]

    return {
        "count": len(events),
        "with_body_preview": len(with_body),
        "sample_subjects": [str(e.get("subject") or "") for e in events[:10]],
    }


def local_keyword_scan(
    client: GraphAPIClient,
    term_sets: List[List[str]],
    max_pages: int = 110,
    page_size: int = 250,
) -> Dict[str, Any]:
    path = "me/messages"
    params: Optional[Dict[str, Any]] = {
        "$select": "id,subject,receivedDateTime,sentDateTime,from,bodyPreview",
        "$orderby": "receivedDateTime desc",
        "$top": page_size,
    }

    matches: Dict[str, List[Dict[str, str]]] = {" ".join(ts): [] for ts in term_sets}
    pages = 0
    scanned = 0

    while path and pages < max_pages:
        resp = client.get(path, params=params, timeout=90)
        pages += 1
        values = resp.get("value") if isinstance(resp, dict) else []
        rows = [v for v in values if isinstance(v, dict)] if isinstance(values, list) else []
        scanned += len(rows)

        for row in rows:
            subject = str(row.get("subject") or "")
            preview = str(row.get("bodyPreview") or "")
            blob = f"{subject} {preview}".lower()
            when = str(row.get("receivedDateTime") or row.get("sentDateTime") or "")

            for ts in term_sets:
                key = " ".join(ts)
                if len(matches[key]) >= 5:
                    continue
                if all(t.lower() in blob for t in ts):
                    matches[key].append({"date": when, "subject": subject})

        path = _next_link(resp) or ""
        params = None

    summary = {
        "pages_scanned": pages,
        "messages_scanned": scanned,
        "queries": {k: {"count": len(v), "samples": v} for k, v in matches.items()},
    }
    return summary


def write_markdown(report: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Graph Search Diagnostics")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    hist = report["history"]
    lines.append("## Mailbox History Access")
    lines.append(f"- Pages fetched: {hist['pages_fetched']}")
    lines.append(f"- Messages fetched: {hist['messages_fetched']}")
    lines.append(f"- Newest message: {hist['newest_message_dt']}")
    lines.append(f"- Oldest message in sample window: {hist['oldest_message_dt']}")
    lines.append("")

    long_hist = report["long_history_probe"]
    lines.append("## Long-History Probe")
    lines.append(f"- Pages fetched: {long_hist['pages_fetched']}")
    lines.append(f"- Messages fetched: {long_hist['messages_fetched']}")
    lines.append(f"- Oldest message reached: {long_hist['oldest_message_dt']}")
    lines.append("")

    old_slice = report["older_date_slice"]
    lines.append("## Older Date Slice Retrieval")
    lines.append(f"- Filter: receivedDateTime < {old_slice['before_iso']}")
    lines.append(f"- Count: {old_slice['count']}")
    lines.append(f"- Sample: {', '.join(old_slice['sample_subjects'][:5])}")
    lines.append("")

    lines.append("## AQS Search ($search on messages)")
    for item in report["aqs_search_tests"]:
        lines.append(f"- Query: `{item['query']}` | folder={item['folder']} | count={item['count']} | unique_ids={item['unique_ids']}")
        if item.get("error"):
            lines.append(f"  - Error: {item['error']}")
        lines.append(f"  - Sample: {', '.join(item['sample_subjects'][:3])}")
    lines.append("")

    lines.append("## Graph Search API (/search/query) — Messages")
    for item in report["search_api_message_tests"]:
        lines.append(f"- Query: `{item['query']}` | count={item['count']}")
        lines.append(f"  - Sample: {', '.join(item['sample_subjects'][:3])}")
    lines.append("")

    lines.append("## Graph Search API (/search/query) — Events")
    for item in report["search_api_event_tests"]:
        lines.append(f"- Query: `{item['query']}` | count={item['count']}")
        lines.append(f"  - Sample: {', '.join(item['sample_subjects'][:3])}")
    lines.append("")

    lines.append("## Meeting Invite Bodies Access")
    mi = report["meeting_invite_messages"]
    if mi.get("error"):
        lines.append(f"- Error: {mi['error']}")
    else:
        lines.append(f"- Count: {mi['count']}")
        lines.append(f"- Classes: {mi.get('message_class_counts')}")
        lines.append(f"- Sample: {', '.join(mi.get('sample_subjects', [])[:5])}")
    lines.append("")

    ev = report["calendar_event_bodies"]
    lines.append("## Calendar Event Body Preview Access")
    lines.append(f"- Events fetched: {ev['count']}")
    lines.append(f"- Events with bodyPreview: {ev['with_body_preview']}")
    lines.append(f"- Sample: {', '.join(ev['sample_subjects'][:5])}")
    lines.append("")

    lks = report["local_keyword_scan"]
    lines.append("## Local Keyword Scan (Index-Independent)")
    lines.append(f"- Pages scanned: {lks['pages_scanned']}")
    lines.append(f"- Messages scanned: {lks['messages_scanned']}")
    for q, detail in lks["queries"].items():
        lines.append(f"- Query terms: `{q}` | matches={detail['count']}")
        sample_subjects = [s.get("subject", "") for s in detail.get("samples", [])]
        lines.append(f"  - Sample: {', '.join(sample_subjects[:3])}")
    lines.append("")

    EXPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    client = build_client(REPO_ROOT)

    report: Dict[str, Any] = {
        "history": sample_mailbox_history(client, max_pages=24, page_size=250),
        "long_history_probe": probe_long_history(client, max_pages=120, page_size=250),
        "older_date_slice": test_older_date_slice(client, before_iso="2024-01-01T00:00:00Z"),
        "aqs_search_tests": [
            test_aqs_search(client, '"Clarivate"', None, top=60),
            test_aqs_search(client, '"forvis"', None, top=60),
            test_aqs_search(client, '"Revenue AI Agent"', None, top=60),
            test_aqs_search(client, 'subject:"Revenue AI Agent"', None, top=60),
            test_aqs_search(client, '"Copilot"', "Inbox", top=60),
            test_aqs_search(client, '"Copilot"', "SentItems", top=60),
        ],
        "search_api_message_tests": [
            test_search_api_messages(client, "Clarivate", size=50),
            test_search_api_messages(client, "Revenue AI Agent", size=50),
            test_search_api_messages(client, "Forvis IRS", size=50),
        ],
        "search_api_event_tests": [
            test_search_api_events(client, "Clarivate", size=30),
            test_search_api_events(client, "Copilot", size=30),
            test_search_api_events(client, "Forvis", size=30),
        ],
        "meeting_invite_messages": test_meeting_invite_messages(client, top=75),
        "calendar_event_bodies": test_calendar_event_bodies(client, top=100),
        "local_keyword_scan": local_keyword_scan(
            client,
            term_sets=[
                ["revenue", "ai", "agent"],
                ["forvis"],
                ["irs", "audit"],
                ["clarivate"],
                ["copilot", "workshop"],
            ],
            max_pages=110,
            page_size=250,
        ),
    }

    EXPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report)
    print(f"Wrote {EXPORT_JSON}")
    print(f"Wrote {EXPORT_MD}")


if __name__ == "__main__":
    main()
