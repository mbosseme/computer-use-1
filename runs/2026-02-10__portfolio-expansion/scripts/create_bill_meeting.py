#!/usr/bin/env python3
"""Create a draft 30-minute meeting invite for Matt and Bill Marquardt on Fri Mar 6, 2:30-3:00 PM ET."""

import sys
import json
import re
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

SUBJECT = "Quick Sync — ABI Alignment across PE, Admin Fee & BT Expansion"

BODY_HTML = """\
<p>Bill,</p>

<p>A few things have converged that I'd like your read on:</p>

<ol>
<li><b>How should ABI engage across PE and Admin Fee?</b> — We've built a shared upstream \
data layer for Portfolio Expansion (supplier mappings, service-line attribution, volume \
measurement) that overlaps heavily with what Joe's scoping for Admin Fee. I'm meeting \
with Joe separately to understand his data needs, but I want your directional guidance \
on how proactively to offer what we have and how you'd like me to coordinate across \
Pam's and Justin's teams.</li>

<li><b>Caitlin / Growth governance</b> — Caitlin has established a coordination cadence \
on Justin's side. Given the data overlap with what Brian and Joe need, what's the right \
way for ABI to plug in without creating competing workstreams?</li>

<li><b>BT expansion proof point</b> — The PE + Admin Fee situation is a concrete example \
of the problem the Business Technologist model solves: one shared enriched data layer, \
multiple business teams building final analytics on top. Happy to walk through how this \
maps to what Matt S. is pulling together if the timing works.</li>

<li><b>Jonathan Pruitt</b> — Brief initial impressions if we've connected by then.</li>
</ol>

<p>If we only need 15 minutes, happy to give you the time back.</p>

<p>Matt</p>
"""

event_payload = {
    "subject": SUBJECT,
    "body": {
        "contentType": "HTML",
        "content": BODY_HTML,
    },
    "start": {
        "dateTime": "2026-03-06T14:30:00",
        "timeZone": "Eastern Standard Time",
    },
    "end": {
        "dateTime": "2026-03-06T15:00:00",
        "timeZone": "Eastern Standard Time",
    },
    "isOnlineMeeting": True,
    "onlineMeetingProvider": "teamsForBusiness",
}

# --- Preview ---
print("=" * 60)
print("MEETING INVITE PREVIEW")
print("=" * 60)
print(f"Subject: {SUBJECT}")
print(f"When:    Fri Mar 6, 2026  2:30–3:00 PM ET (adjust if earlier slot opens)")
print(f"To:      (draft — add Bill Marquardt before sending)")
print(f"Teams:   Yes")
print()
print("--- Body ---")
plain = re.sub(r"<[^>]+>", "", BODY_HTML).strip()
plain = re.sub(r"\n{3,}", "\n\n", plain)
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
print("Event created successfully!")
print(f"  Event ID: {event_id}")
if web_link:
    print(f"  Web link: {web_link}")
