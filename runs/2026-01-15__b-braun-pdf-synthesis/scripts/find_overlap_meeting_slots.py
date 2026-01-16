from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


def _repo_root() -> Path:
    # runs/<RUN_ID>/scripts/<this_file>
    return Path(__file__).resolve().parents[3]


# Ensure imports work even if cwd is not repo root.
_REPO_ROOT = _repo_root()
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator  # noqa: E402
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig  # noqa: E402
from agent_tools.graph.env import load_graph_env  # noqa: E402


def _now_in_tz(tz_name: Optional[str]) -> datetime:
    if not tz_name or ZoneInfo is None:
        return datetime.now(timezone.utc)
    try:
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now(timezone.utc)


def _floor_to_date(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _next_weekday_start(dt: datetime, weekday: int) -> datetime:
    # weekday: Monday=0 ... Sunday=6
    if weekday < 0 or weekday > 6:
        raise ValueError("weekday must be in [0, 6]")
    days_ahead = (weekday - dt.weekday()) % 7
    candidate = _floor_to_date(dt + timedelta(days=days_ahead))
    # If today is the target weekday and it's already past it, still choose today.
    return candidate


def _parse_hhmm(value: str) -> Tuple[int, int]:
    raw = (value or "").strip()
    parts = raw.split(":")
    if len(parts) != 2:
        raise ValueError("time must be HH:MM")
    return int(parts[0]), int(parts[1])


def _as_local_dt_str(dt: datetime) -> str:
    # Graph getSchedule accepts local dateTime string.
    return dt.replace(microsecond=0).isoformat()


@dataclass
class Slot:
    start: datetime
    end: datetime


def _availability_view(schedule_item: Dict[str, Any]) -> str:
    v = schedule_item.get("availabilityView")
    return v if isinstance(v, str) else ""


def _get_schedule_items(resp: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = resp.get("value") if isinstance(resp, dict) else None
    return items if isinstance(items, list) else []


def _pick_item(items: List[Dict[str, Any]], schedule_id: str) -> Optional[Dict[str, Any]]:
    for it in items:
        if not isinstance(it, dict):
            continue
        if str(it.get("scheduleId") or "").strip().lower() == schedule_id.strip().lower():
            return it
    return None


def _find_overlap_slots(
    client: GraphAPIClient,
    *,
    me_email: str,
    other_email: str,
    outlook_tz: str,
    display_tz: Optional[str],
    business_start: str,
    business_end: str,
    interval_minutes: int,
    timeout_s: int,
) -> List[Slot]:
    # Compute next Monday–Friday in display tz if possible; else UTC.
    now = _now_in_tz(display_tz)

    # If we're already in the weekend, next Monday. If we're mid-week, still propose next week (Mon–Fri upcoming).
    next_monday = _next_weekday_start(now, weekday=0)
    if next_monday.date() <= now.date():
        # Force next week's Monday.
        next_monday = next_monday + timedelta(days=7)

    start_hour, start_min = _parse_hhmm(business_start)
    end_hour, end_min = _parse_hhmm(business_end)

    tzinfo = None
    if display_tz and ZoneInfo is not None:
        try:
            tzinfo = ZoneInfo(display_tz)
        except Exception:
            tzinfo = None

    all_slots: List[Slot] = []

    for day_offset in range(5):
        day = next_monday + timedelta(days=day_offset)
        if tzinfo is not None:
            day = day.replace(tzinfo=tzinfo)

        window_start = day.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
        window_end = day.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)

        resp = client.calendar_get_schedule(
            schedules=[me_email, other_email],
            start_local=_as_local_dt_str(window_start),
            end_local=_as_local_dt_str(window_end),
            timezone_name=outlook_tz,
            interval_minutes=interval_minutes,
            timeout=timeout_s,
        )

        items = _get_schedule_items(resp)
        me_item = _pick_item(items, me_email)
        other_item = _pick_item(items, other_email)
        if not me_item or not other_item:
            continue

        me_view = _availability_view(me_item)
        other_view = _availability_view(other_item)
        if not me_view or not other_view:
            continue

        # Find indices where both are free ('0').
        n = min(len(me_view), len(other_view))
        step = timedelta(minutes=interval_minutes)
        for idx in range(n):
            if me_view[idx] == "0" and other_view[idx] == "0":
                slot_start = window_start + (idx * step)
                slot_end = slot_start + step
                all_slots.append(Slot(start=slot_start, end=slot_end))

    return all_slots


def _format_slot(slot: Slot, display_tz: Optional[str]) -> str:
    tzinfo = None
    if display_tz and ZoneInfo is not None:
        try:
            tzinfo = ZoneInfo(display_tz)
        except Exception:
            tzinfo = None

    s = slot.start
    e = slot.end
    if tzinfo is not None:
        if s.tzinfo is None:
            s = s.replace(tzinfo=tzinfo)
        else:
            s = s.astimezone(tzinfo)
        if e.tzinfo is None:
            e = e.replace(tzinfo=tzinfo)
        else:
            e = e.astimezone(tzinfo)

    tz_abbrev = s.strftime("%Z") if s.tzinfo else ""
    return f"{s.strftime('%a %b %d')} {s.strftime('%-I:%M %p')}–{e.strftime('%-I:%M %p')} {tz_abbrev}".strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Find overlapping free 30-min meeting slots next week for you + another attendee.")
    parser.add_argument("--other-email", required=True, help="Other attendee email (e.g., sachin@...)\n")
    parser.add_argument("--business-start", default="09:00", help="Business hours start (HH:MM) in display timezone")
    parser.add_argument("--business-end", default="16:30", help="Business hours end (HH:MM) in display timezone")
    parser.add_argument("--interval-minutes", type=int, default=30, help="Slot size (default: 30)")
    parser.add_argument("--limit", type=int, default=10, help="Max slots to print (default: 10)")
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout seconds (default: 90)")
    parser.add_argument(
        "--display-timezone",
        default="America/New_York",
        help="IANA timezone for printing (default: America/New_York)",
    )
    args = parser.parse_args()

    env = load_graph_env(_REPO_ROOT)
    authenticator = GraphAuthenticator(repo_root=_REPO_ROOT, env=env)
    client = GraphAPIClient(
        authenticator=authenticator,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )

    me = client.me()
    me_email = str(me.get("mail") or me.get("userPrincipalName") or "").strip()
    if not me_email:
        raise SystemExit("Could not determine /me email")

    if not env.planner_timezone:
        raise SystemExit("Missing PLANNER_TIMEZONE in env (Windows timezone name required for getSchedule)")

    slots = _find_overlap_slots(
        client,
        me_email=me_email,
        other_email=str(args.other_email),
        outlook_tz=env.planner_timezone,
        display_tz=str(args.display_timezone) if args.display_timezone else None,
        business_start=str(args.business_start),
        business_end=str(args.business_end),
        interval_minutes=int(args.interval_minutes),
        timeout_s=int(args.timeout),
    )

    # De-dupe (Graph can return repeats across windows); sort ascending.
    uniq: Dict[str, Slot] = {}
    for s in slots:
        k = f"{s.start.isoformat()}|{s.end.isoformat()}"
        uniq[k] = s

    ordered = sorted(uniq.values(), key=lambda x: x.start)
    if not ordered:
        print("No overlap slots found in next-week business hours.")
        return 0

    print("Suggested overlap slots (you + other):")
    for slot in ordered[: int(args.limit)]:
        print(f"- {_format_slot(slot, str(args.display_timezone))}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
