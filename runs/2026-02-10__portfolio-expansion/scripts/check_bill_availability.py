#!/usr/bin/env python3
"""Check mutual calendar availability between Matt and Bill Marquardt for Thu-Fri this week."""

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

# Thu Mar 5 (after Joe meeting at 10:00) through Fri Mar 6
thu = datetime(2026, 3, 5, 0, 0, tzinfo=tz)
sat = datetime(2026, 3, 7, 0, 0, tzinfo=tz)

me = client.me()
my_email = me.get("userPrincipalName") or me.get("mail")
bill_email = "Bill_Marquardt@PremierInc.com"

print(f"My email: {my_email}")
print(f"Bill email: {bill_email}")
print()

# Get schedules for both users
schedule = client.calendar_get_schedule(
    schedules=[my_email, bill_email],
    start_local=thu.replace(tzinfo=None).isoformat(),
    end_local=sat.replace(tzinfo=None).isoformat(),
    timezone_name="Eastern Standard Time",
    interval_minutes=30,
    timeout=60,
)

values = schedule.get("value", [])
print(f"Got {len(values)} schedule(s)")
print()

interval = timedelta(minutes=30)

for v in values:
    email = v.get("scheduleId", "unknown")
    view = v.get("availabilityView", "")
    print(f"  {email}: availabilityView length={len(view)}")

views = {}
for v in values:
    email = v.get("scheduleId", "").lower()
    views[email] = v.get("availabilityView", "")

my_view = views.get(my_email.lower(), "")
bill_view = views.get(bill_email.lower(), "")

if not my_view or not bill_view:
    print("ERROR: Missing availability view")
    print(f"  my_view length: {len(my_view)}")
    print(f"  bill_view length: {len(bill_view)}")
    sys.exit(1)

print()

# Check Thu afternoon (after Joe meeting ends at 10:00) and all of Fri
for day_offset in range(2):  # Thu(0), Fri(1)
    day_start = thu + timedelta(days=day_offset)
    day_date = day_start.date()

    if day_offset == 0:
        # Thursday: only after 10:00 (Joe meeting ends at 10:00)
        bh_start = datetime(day_date.year, day_date.month, day_date.day, 10, 0, tzinfo=tz)
        label_note = " (after Joe meeting)"
    else:
        bh_start = datetime(day_date.year, day_date.month, day_date.day, 8, 30, tzinfo=tz)
        label_note = ""

    bh_end = datetime(day_date.year, day_date.month, day_date.day, 16, 30, tzinfo=tz)

    start_idx = int((bh_start - thu) / interval)
    end_idx = int((bh_end - thu) / interval)
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
                free_ranges.append((thu + interval * run_start, thu + interval * run_end))
            run_start = None
    if run_start is not None:
        run_end = end_idx
        if run_end - run_start >= 1:
            free_ranges.append((thu + interval * run_start, thu + interval * run_end))

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

    label = bh_start.strftime(f"%a %Y-%m-%d")
    print(f"  {label}{label_note}: {', '.join(formatted) if formatted else '(no mutual 30-min availability)'}")

# Also check if there's any existing 1:1 with Bill already on calendar
print()
print("=== Existing meetings with Bill on Thu-Fri ===")
cal = client.calendar_view(
    start_iso=thu.isoformat(),
    end_iso=sat.isoformat(),
)
cal_items = cal.get("value", [])
for ev in cal_items:
    attendees = ev.get("attendees", [])
    for att in attendees:
        addr = (att.get("emailAddress", {}).get("address", "") or "").lower()
        if "marquardt" in addr or "bill_marquardt" in addr:
            subj = ev.get("subject", "(no subject)")
            start_obj = ev.get("start", {})
            end_obj = ev.get("end", {})
            print(f"  {start_obj.get('dateTime','')} - {end_obj.get('dateTime','')} | {subj}")
            break
