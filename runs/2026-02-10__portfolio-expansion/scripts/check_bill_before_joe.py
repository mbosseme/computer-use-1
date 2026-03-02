#!/usr/bin/env python3
"""Check mutual availability between Matt and Bill for Tue-Wed and Thu before 9:30."""

import sys
from pathlib import Path
from datetime import datetime, timedelta
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

# Tue Mar 3 through Thu Mar 5 (before Joe meeting at 9:30)
tue = datetime(2026, 3, 3, 0, 0, tzinfo=tz)
fri = datetime(2026, 3, 6, 0, 0, tzinfo=tz)

me = client.me()
my_email = me.get("userPrincipalName") or me.get("mail")
bill_email = "Bill_Marquardt@PremierInc.com"

schedule = client.calendar_get_schedule(
    schedules=[my_email, bill_email],
    start_local=tue.replace(tzinfo=None).isoformat(),
    end_local=fri.replace(tzinfo=None).isoformat(),
    timezone_name="Eastern Standard Time",
    interval_minutes=30,
    timeout=60,
)

values = schedule.get("value", [])
interval = timedelta(minutes=30)

views = {}
for v in values:
    email = v.get("scheduleId", "").lower()
    views[email] = v.get("availabilityView", "")
    print(f"  {v.get('scheduleId','')}: view length={len(views[email])}")

my_view = views.get(my_email.lower(), "")
bill_view = views.get(bill_email.lower(), "")

if not my_view or not bill_view:
    print("ERROR: Missing availability view")
    sys.exit(1)

print()
print("=== Mutual Availability (Tue-Thu, before Joe meeting) ===")

day_configs = [
    (0, "Tue 2026-03-03", 8, 30, 16, 30, ""),
    (1, "Wed 2026-03-04", 8, 30, 16, 30, ""),
    (2, "Thu 2026-03-05", 8, 30, 9, 30, " (before Joe @ 9:30)"),
]

for day_offset, label, sh, sm, eh, em, note in day_configs:
    day_start = tue + timedelta(days=day_offset)
    day_date = day_start.date()
    bh_start = datetime(day_date.year, day_date.month, day_date.day, sh, sm, tzinfo=tz)
    bh_end = datetime(day_date.year, day_date.month, day_date.day, eh, em, tzinfo=tz)

    start_idx = int((bh_start - tue) / interval)
    end_idx = int((bh_end - tue) / interval)
    start_idx = max(0, start_idx)
    end_idx = min(min(len(my_view), len(bill_view)), end_idx)

    free_ranges = []
    run_start = None
    for idx in range(start_idx, end_idx):
        both_free = (my_view[idx] == "0") and (bill_view[idx] == "0")
        if both_free and run_start is None:
            run_start = idx
        if (not both_free) and run_start is not None:
            run_end = idx
            if run_end - run_start >= 1:
                free_ranges.append((tue + interval * run_start, tue + interval * run_end))
            run_start = None
    if run_start is not None:
        run_end = end_idx
        if run_end - run_start >= 1:
            free_ranges.append((tue + interval * run_start, tue + interval * run_end))

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

    print(f"  {label}{note}: {', '.join(formatted) if formatted else '(no mutual 30-min availability)'}")

# Also still show Fri afternoon as fallback
print()
print("=== Fri fallback (after Joe) ===")
print("  Fri 2026-03-06: 14:30-15:00 (30m) — already confirmed available")
