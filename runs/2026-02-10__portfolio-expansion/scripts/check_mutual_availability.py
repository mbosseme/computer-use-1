#!/usr/bin/env python3
"""Check mutual calendar availability between Matt and Joe Bichler for Tue-Fri this week."""

import sys
from pathlib import Path
from datetime import datetime, timedelta
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

tz = ZoneInfo("America/New_York")

# This week: Tue Mar 3 through Fri Mar 6
tue = datetime(2026, 3, 3, 0, 0, tzinfo=tz)
sat = datetime(2026, 3, 7, 0, 0, tzinfo=tz)

me = client.me()
my_email = me.get("userPrincipalName") or me.get("mail")
joe_email = "Joe_Bichler@premierinc.com"

print(f"My email: {my_email}")
print(f"Joe email: {joe_email}")
print()

# Get schedules for both users
schedule = client.calendar_get_schedule(
    schedules=[my_email, joe_email],
    start_local=tue.replace(tzinfo=None).isoformat(),
    end_local=sat.replace(tzinfo=None).isoformat(),
    timezone_name="Eastern Standard Time",
    interval_minutes=30,
    timeout=60,
)

values = schedule.get("value", [])
print(f"Got {len(values)} schedule(s)")
print()

interval = timedelta(minutes=30)
business_start_h, business_start_m = 8, 30
business_end_h, business_end_m = 16, 30

for v in values:
    email = v.get("scheduleId", "unknown")
    view = v.get("availabilityView", "")
    print(f"  {email}: availabilityView length={len(view)}")

# Find mutual availability
views = {}
for v in values:
    email = v.get("scheduleId", "").lower()
    views[email] = v.get("availabilityView", "")

my_view = views.get(my_email.lower(), "")
joe_view = views.get(joe_email.lower(), "")

if not my_view or not joe_view:
    print("ERROR: Missing availability view")
    print(f"  my_view length: {len(my_view)}")
    print(f"  joe_view length: {len(joe_view)}")
    sys.exit(1)

print()
print("=== Mutual Availability (Tue-Fri, 8:30-16:30 ET) ===")

for day_offset in range(4):  # Tue(0) through Fri(3)
    day_start = tue + timedelta(days=day_offset)
    day_date = day_start.date()
    bh_start = datetime(day_date.year, day_date.month, day_date.day, business_start_h, business_start_m, tzinfo=tz)
    bh_end = datetime(day_date.year, day_date.month, day_date.day, business_end_h, business_end_m, tzinfo=tz)

    start_idx = int((bh_start - tue) / interval)
    end_idx = int((bh_end - tue) / interval)
    start_idx = max(0, start_idx)
    end_idx = min(min(len(my_view), len(joe_view)), end_idx)

    free_ranges = []
    run_start = None
    for idx in range(start_idx, end_idx):
        both_free = (my_view[idx] == "0") and (joe_view[idx] == "0")
        if both_free and run_start is None:
            run_start = idx
        if (not both_free) and run_start is not None:
            run_end = idx
            if run_end - run_start >= 1:  # at least 30 min
                free_ranges.append((
                    tue + interval * run_start,
                    tue + interval * run_end,
                ))
            run_start = None
    if run_start is not None:
        run_end = end_idx
        if run_end - run_start >= 1:
            free_ranges.append((
                tue + interval * run_start,
                tue + interval * run_end,
            ))

    formatted = []
    for rng_start, rng_end in free_ranges:
        s = rng_start.astimezone(tz)
        e = rng_end.astimezone(tz)
        if s < bh_start:
            s = bh_start
        if e > bh_end:
            e = bh_end
        if e - s >= interval:
            s_str = s.strftime("%H:%M")
            e_str = e.strftime("%H:%M")
            dur_min = int((e - s).total_seconds() / 60)
            formatted.append(f"{s_str}-{e_str} ({dur_min}m)")

    label = bh_start.strftime("%a %Y-%m-%d")
    if formatted:
        print(f"  {label}: {', '.join(formatted)}")
    else:
        print(f"  {label}: (no mutual 30-min availability)")
