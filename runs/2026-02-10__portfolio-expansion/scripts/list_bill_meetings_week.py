#!/usr/bin/env python3
"""List all meetings with Bill Marquardt this week (Mon-Fri)."""

import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

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

tz = ZoneInfo("America/New_York")
mon = datetime(2026, 3, 2, 0, 0, tzinfo=tz)
sat = datetime(2026, 3, 7, 0, 0, tzinfo=tz)

cal = client.calendar_view(start_iso=mon.isoformat(), end_iso=sat.isoformat())
items = cal.get("value", [])

print("=== All meetings with Bill this week (Mon-Fri) ===")
found = False
for ev in sorted(items, key=lambda e: e.get("start", {}).get("dateTime", "")):
    attendees = ev.get("attendees", [])
    for att in attendees:
        addr = (att.get("emailAddress", {}).get("address", "") or "").lower()
        if "bill_marquardt" in addr:
            subj = ev.get("subject", "(no subject)")
            s = ev.get("start", {}).get("dateTime", "")
            e_time = ev.get("end", {}).get("dateTime", "")
            show = ev.get("showAs", "")
            print(f"  {s} - {e_time} | {subj} | showAs={show}")
            found = True
            break

if not found:
    print("  (no meetings found with Bill this week)")
