#!/usr/bin/env python3
"""Create a 30-minute meeting invite for Matt and Joe Bichler on Thu Mar 5, 9:30-10:00 AM ET."""

import sys
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# Add repo root to path
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

SUBJECT = "Upstream Data & Sourcing Analytics — Quick Sync"

BODY_HTML = """\
<p>Hi Joe,</p>

<p>I wanted to reach out directly — my team (ABI) has been building upstream data models \
that I think overlap significantly with some of the data needs you're working through \
on the sourcing side, and I'd like to make sure we're not duplicating effort.</p>

<p>Specifically, we've built supplier parent/child mappings, category-to-service-line \
attribution, and clinical &amp; non-clinical volume measurement as part of our data \
enrichment work. I'd love to spend a few minutes understanding what you're pulling \
together and where there might be a fit.</p>

<p>I'd also like to tee up a follow-on conversation around some leading‑indicator work \
we've been doing on contract and program health — early signals on performance trends \
that could be useful for your analysis down the road.</p>

<p>Looking forward to connecting.</p>

<p>Matt</p>
"""

# Draft mode: create WITHOUT attendees so no invite is sent.
# Open the event in Outlook, add Joe as attendee, and hit Send when ready.
event_payload = {
    "subject": SUBJECT,
    "body": {
        "contentType": "HTML",
        "content": BODY_HTML,
    },
    "start": {
        "dateTime": "2026-03-05T09:30:00",
        "timeZone": "Eastern Standard Time",
    },
    "end": {
        "dateTime": "2026-03-05T10:00:00",
        "timeZone": "Eastern Standard Time",
    },
    "isOnlineMeeting": True,
    "onlineMeetingProvider": "teamsForBusiness",
}

# --- Safety gate: print the invite for review before sending ---
print("=" * 60)
print("MEETING INVITE PREVIEW")
print("=" * 60)
print(f"Subject: {SUBJECT}")
print(f"When:    Thu Mar 5, 2026  9:30–10:00 AM ET")
print(f"To:      (draft — add Joe Bichler before sending)")
print(f"Teams:   Yes (online meeting link will be generated)")
print()
print("--- Body ---")
# Print a plain-text version for readability
import re
plain = re.sub(r"<[^>]+>", "", BODY_HTML).strip()
print(plain)
print("--- End Body ---")
print()

if "--create" not in sys.argv:
    print("DRY RUN — pass --create to create the draft event on your calendar.")
    print()
    print("Payload:")
    print(json.dumps(event_payload, indent=2))
    sys.exit(0)

print("Creating draft event (no invite sent)...")
result = client.post("me/events", json=event_payload)
event_id = result.get("id", "")
web_link = result.get("webLink", "")
print(f"Event created successfully!")
print(f"  Event ID: {event_id}")
if web_link:
    print(f"  Web link: {web_link}")
print()
print(json.dumps(result, indent=2, default=str))
