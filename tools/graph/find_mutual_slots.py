from __future__ import annotations

import argparse
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def _normalize_tz(tz_name: Optional[str]) -> str:
    windows_to_iana = {
        "Eastern Standard Time": "America/New_York",
        "Central Standard Time": "America/Chicago",
        "Mountain Standard Time": "America/Denver",
        "Pacific Standard Time": "America/Los_Angeles",
    }
    if not tz_name:
        return "America/New_York"
    return windows_to_iana.get(tz_name, tz_name)


def _graph_timezone(tz_name: Optional[str]) -> str:
    # Graph getSchedule is most reliable with Windows timezone names.
    return tz_name or "Eastern Standard Time"


def _round_to_interval(dt: datetime, minutes: int) -> datetime:
    dt = dt.replace(second=0, microsecond=0)
    rem = dt.minute % minutes
    if rem == 0:
        return dt
    return dt + timedelta(minutes=(minutes - rem))


def _is_within_window(slot_start: datetime, slot_end: datetime, day_start: time, day_end: time) -> bool:
    if slot_start.weekday() > 4:
        return False
    start_bound = slot_start.replace(hour=day_start.hour, minute=day_start.minute, second=0, microsecond=0)
    end_bound = slot_start.replace(hour=day_end.hour, minute=day_end.minute, second=0, microsecond=0)
    return slot_start >= start_bound and slot_end <= end_bound


def _all_bookable(codes: Sequence[str], allow_tentative: bool) -> bool:
    allowed = {"0"}
    if allow_tentative:
        allowed.add("1")
    return all(c in allowed for c in codes)


def _find_slots(
    client: GraphAPIClient,
    *,
    schedules: List[str],
    tz_name: str,
    start_dt: datetime,
    end_dt: datetime,
    interval_minutes: int,
    duration_minutes: int,
    allow_tentative: bool,
    day_start: time,
    day_end: time,
    max_results: int,
) -> List[Tuple[datetime, datetime]]:
    payload = client.calendar_get_schedule(
        schedules=schedules,
        start_local=start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        end_local=end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        timezone_name=tz_name,
        interval_minutes=interval_minutes,
        timeout=120,
    )

    schedule_info = payload.get("value") or []
    if len(schedule_info) != len(schedules):
        return []

    views = [str(item.get("availabilityView") or "") for item in schedule_info]
    if any(not v for v in views):
        return []

    min_len = min(len(v) for v in views)
    blocks = max(1, duration_minutes // interval_minutes)

    results: List[Tuple[datetime, datetime]] = []
    for i in range(0, min_len - blocks + 1):
        slot_start = start_dt + timedelta(minutes=interval_minutes * i)
        slot_end = slot_start + timedelta(minutes=duration_minutes)

        if not _is_within_window(slot_start, slot_end, day_start, day_end):
            continue

        ok = True
        for j in range(blocks):
            codes = [v[i + j] for v in views]
            if not _all_bookable(codes, allow_tentative=allow_tentative):
                ok = False
                break

        if ok:
            results.append((slot_start, slot_end))
            if len(results) >= max_results:
                break

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Find mutual Graph availability slots.")
    parser.add_argument("--emails", nargs="+", required=True, help="Email list to include in overlap calculation")
    parser.add_argument("--days", type=int, default=7, help="Search horizon in days (default: 7)")
    parser.add_argument("--duration", type=int, default=30, help="Meeting duration minutes (default: 30)")
    parser.add_argument("--interval", type=int, default=30, help="Availability interval minutes (default: 30)")
    parser.add_argument("--day-start", default="08:30", help="Daily start local time HH:MM (default: 08:30)")
    parser.add_argument("--day-end", default="16:30", help="Daily end local time HH:MM (default: 16:30)")
    parser.add_argument("--allow-tentative", action="store_true", help="Treat tentative as bookable")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum slots to print")
    args = parser.parse_args()

    env = load_graph_env(REPO_ROOT)
    graph_tz = _graph_timezone(env.planner_timezone)
    display_tz_name = _normalize_tz(env.planner_timezone)
    tz = ZoneInfo(display_tz_name) if ZoneInfo else None

    auth = GraphAuthenticator(repo_root=REPO_ROOT, env=env)
    client = GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=graph_tz),
    )

    now = datetime.now(tz)
    start_dt = _round_to_interval(now + timedelta(minutes=args.interval), args.interval)
    end_dt = start_dt + timedelta(days=args.days)

    ds_h, ds_m = [int(p) for p in args.day_start.split(":", 1)]
    de_h, de_m = [int(p) for p in args.day_end.split(":", 1)]

    slots = _find_slots(
        client,
        schedules=[e.strip().lower() for e in args.emails if e.strip()],
        tz_name=graph_tz,
        start_dt=start_dt,
        end_dt=end_dt,
        interval_minutes=args.interval,
        duration_minutes=args.duration,
        allow_tentative=bool(args.allow_tentative),
        day_start=time(ds_h, ds_m),
        day_end=time(de_h, de_m),
        max_results=args.max_results,
    )

    print("TIMEZONE_GRAPH:", graph_tz)
    print("TIMEZONE_DISPLAY:", display_tz_name)
    print("WINDOW:", start_dt.strftime("%Y-%m-%d %H:%M"), "to", end_dt.strftime("%Y-%m-%d %H:%M"))
    print("ATTENDEES:", "; ".join([e.strip().lower() for e in args.emails if e.strip()]))
    print("ALLOW_TENTATIVE:", "YES" if args.allow_tentative else "NO")

    if not slots:
        print("RESULT: NONE")
        return

    print("RESULT: FOUND")
    for s, e in slots:
        print("SLOT:", f"{s.strftime('%a %b %d, %I:%M %p')} - {e.strftime('%I:%M %p')}")


if __name__ == "__main__":
    main()
