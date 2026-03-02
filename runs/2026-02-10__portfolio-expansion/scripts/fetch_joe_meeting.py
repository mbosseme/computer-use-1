#!/usr/bin/env python3
"""Fetch the Joe Bichler meeting invite that was sent, to see the final body + attachments."""

import sys
import json
from pathlib import Path

repo = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env

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

# Find the event by subject — search calendar for Thu Mar 5
events = client.get(
    "me/calendarView",
    params={
        "startDateTime": "2026-03-05T00:00:00",
        "endDateTime": "2026-03-05T23:59:59",
        "$select": "id,subject,start,end,body,attendees,hasAttachments,onlineMeeting,isOnlineMeeting",
        "$top": 50,
    },
)

items = events.get("value", [])
print(f"Found {len(items)} events on Thu Mar 5")
print()

for ev in items:
    subj = ev.get("subject", "")
    if "joe" in subj.lower() or "upstream" in subj.lower() or "sourcing" in subj.lower() or "bichler" in subj.lower() or "quick sync" in subj.lower():
        print(f"=== MATCH: {subj} ===")
        print(f"Start: {ev['start']}")
        print(f"End: {ev['end']}")
        print(f"Has Attachments: {ev.get('hasAttachments')}")
        print()

        attendees = ev.get("attendees", [])
        for att in attendees:
            ea = att.get("emailAddress", {})
            print(f"  Attendee: {ea.get('name', '')} <{ea.get('address', '')}>  type={att.get('type')}")
        print()

        body = ev.get("body", {})
        print(f"Body type: {body.get('contentType')}")
        print("--- Body Content ---")
        content = body.get("content", "")
        # Strip HTML for readability
        import re
        plain = re.sub(r"<[^>]+>", "", content)
        plain = re.sub(r"\n{3,}", "\n\n", plain).strip()
        print(plain)
        print("--- End Body ---")
        print()

        # Fetch attachments if any
        if ev.get("hasAttachments"):
            event_id = ev["id"]
            attachments = client.get(f"me/events/{event_id}/attachments")
            att_items = attachments.get("value", [])
            print(f"Attachments ({len(att_items)}):")
            for a in att_items:
                print(f"  - {a.get('name', 'unnamed')} ({a.get('contentType', '?')}, {a.get('size', '?')} bytes)")
        print()
        print("=" * 60)
        print()
