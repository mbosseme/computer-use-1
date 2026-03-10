from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now_in_tz(tz_name: Optional[str]) -> datetime:
    if not tz_name:
        return datetime.now(timezone.utc)
    if ZoneInfo is None:
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
    return _floor_to_date(dt + timedelta(days=days_ahead))


def _format_event_time(dt_str: str, tz_name: Optional[str]) -> str:
    # Graph often returns strings like: 2026-01-12T07:00:00.0000000 (7 fractional digits)
    # and may omit an offset when a Prefer outlook.timezone header is used.
    s = (dt_str or "").strip()
    if not s:
        return ""

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    if "." in s:
        head, tail = s.split(".", 1)
        frac = ""
        rest = ""
        for idx, ch in enumerate(tail):
            if ch.isdigit():
                frac += ch
            else:
                rest = tail[idx:]
                break

        # Python supports up to 6 microsecond digits.
        if len(frac) > 6:
            frac = frac[:6]
        if frac:
            s = f"{head}.{frac}{rest}"
        else:
            s = f"{head}{rest}"

    try:
        parsed = datetime.fromisoformat(s)
    except Exception:
        return dt_str

    if tz_name and ZoneInfo is not None:
        try:
            tz = ZoneInfo(tz_name)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=tz)
            else:
                parsed = parsed.astimezone(tz)
        except Exception:
            pass

    parsed = parsed.replace(second=0, microsecond=0)
    tz_abbrev = parsed.strftime("%Z") if parsed.tzinfo else ""
    # Example: Mon 2026-01-12 07:00 ET
    return f"{parsed.strftime('%a %Y-%m-%d %H:%M')} {tz_abbrev}".rstrip()


def _parse_hhmm(value: str) -> tuple[int, int]:
    raw = (value or "").strip()
    if not raw:
        raise ValueError("time must be non-empty")
    parts = raw.split(":")
    if len(parts) != 2:
        raise ValueError("time must be HH:MM")
    hour = int(parts[0])
    minute = int(parts[1])
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("time must be a valid HH:MM")
    return hour, minute


def _format_range(start_dt: datetime, end_dt: datetime) -> str:
    tz_abbrev = start_dt.strftime("%Z") if start_dt.tzinfo else ""
    return f"{start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')} {tz_abbrev}".rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Microsoft Graph delegated auth + access")
    parser.add_argument(
        "--days",
        type=int,
        default=14,
        help="How many days ahead to query calendarView (default: 14)",
    )
    parser.add_argument(
        "--next-workweek",
        action="store_true",
        help="Query the next Monday through Friday (inclusive) instead of using --days.",
    )
    parser.add_argument(
        "--list-events",
        action="store_true",
        help="Print calendar events returned by calendarView.",
    )
    parser.add_argument(
        "--availability",
        action="store_true",
        help=(
            "Compute available 30-minute meeting windows using Graph getSchedule (free/busy) "
            "for the next Monday–Friday workweek."
        ),
    )
    parser.add_argument(
        "--business-start",
        default="08:30",
        help="Business-hours start time (HH:MM) in display timezone (default: 08:30)",
    )
    parser.add_argument(
        "--business-end",
        default="16:30",
        help="Business-hours end time (HH:MM) in display timezone (default: 16:30)",
    )
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=30,
        help="Meeting interval minutes for availability computation (default: 30)",
    )
    parser.add_argument(
        "--outlook-timezone",
        help=(
            "Outlook timezone for the Prefer header (Windows TZ name, e.g. 'Eastern Standard Time'). "
            "If omitted, uses PLANNER_TIMEZONE from env if set."
        ),
    )
    parser.add_argument(
        "--display-timezone",
        help=(
            "Timezone used to format printed event times (IANA name, e.g. 'America/New_York'). "
            "If omitted, uses PLANNER_TIMEZONE from env if set."
        ),
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Optionally create+patch a test To Do task (makes changes in your account)",
    )
    parser.add_argument(
        "--todo-list-id",
        help="To Do list ID to use for --write. If omitted, uses the first list returned.",
    )
    parser.add_argument(
        "--task-title",
        default="Graph API validation task (created by computer-use agent)",
        help="Title for the created test task when using --write",
    )
    args = parser.parse_args()

    repo_root = _repo_root()
    env = load_graph_env(repo_root)

    print("Graph env loaded:")
    print(f"  tenant_id: {env.tenant_id}")
    print(f"  client_id: {env.client_id}")
    print(f"  authority: {env.authority_url}")
    print(f"  scopes (filtered): {', '.join(env.scopes)}")
    print(f"  token_cache_file: {env.token_cache_file}")
    print(f"  base_url: {env.base_url}")

    authenticator = GraphAuthenticator(repo_root=repo_root, env=env)

    token_result = authenticator.acquire_access_token(scopes=env.scopes)
    print("Token acquired.")
    if token_result.scp:
        print(f"  scp: {token_result.scp}")

    client = GraphAPIClient(
        authenticator=authenticator,
        config=GraphClientConfig(
            base_url=env.base_url,
            scopes=env.scopes,
            planner_timezone=(args.outlook_timezone or env.planner_timezone),
        ),
    )

    me = client.me()
    upn = me.get("userPrincipalName") or me.get("mail") or me.get("displayName")
    print(f"/me OK: {upn}")

    todo_lists = client.todo_lists()
    lists = todo_lists.get("value", []) if isinstance(todo_lists, dict) else []
    print(f"/me/todo/lists OK: {len(lists)} lists")

    display_tz = args.display_timezone or env.planner_timezone

    now = _now_in_tz(display_tz).replace(microsecond=0)

    if args.next_workweek:
        # Interpret "next Monday" relative to "now" in the display timezone.
        start = _next_weekday_start(now, weekday=0)
        end = _next_weekday_start(start, weekday=4) + timedelta(days=1)
        # end is exclusive: start of Saturday.
        start_iso = start.isoformat()
        end_iso = end.isoformat()
    else:
        end = now + timedelta(days=int(args.days))

        # Graph calendarView accepts offsets; use ISO with timezone.
        start_iso = now.isoformat()
        end_iso = end.isoformat()

    cal = client.calendar_view(start_iso=start_iso, end_iso=end_iso)
    items = cal.get("value", []) if isinstance(cal, dict) else []
    if args.next_workweek:
        print(f"/me/calendarView OK: {len(items)} events (next Mon–Fri)")
    else:
        print(f"/me/calendarView OK: {len(items)} events ({args.days} days)")

    if args.list_events:
        # Sort by start time (best-effort).
        def _start_key(ev: dict) -> str:
            start_obj = ev.get("start") or {}
            return str(start_obj.get("dateTime") or "")

        for ev in sorted(items, key=_start_key):
            subject = ev.get("subject") or "(no subject)"
            is_all_day = bool(ev.get("isAllDay"))
            start_obj = ev.get("start") or {}
            end_obj = ev.get("end") or {}
            start_dt = str(start_obj.get("dateTime") or "")
            end_dt = str(end_obj.get("dateTime") or "")

            if is_all_day:
                start_fmt = _format_event_time(start_dt, display_tz)
                end_fmt = _format_event_time(end_dt, display_tz)
                # All-day events are typically midnight-to-midnight; show span for clarity.
                print(f"- {start_fmt} → {end_fmt} (all-day) — {subject}")
            else:
                start_fmt = _format_event_time(start_dt, display_tz)
                end_fmt = _format_event_time(end_dt, display_tz)
                print(f"- {start_fmt} → {end_fmt} — {subject}")

    if args.availability:
        if not args.next_workweek:
            raise RuntimeError("--availability requires --next-workweek")

        if ZoneInfo is None:
            raise RuntimeError("zoneinfo is required for --availability")

        tz_for_display = ZoneInfo(display_tz) if display_tz else timezone.utc
        outlook_tz = args.outlook_timezone or env.planner_timezone
        if not outlook_tz:
            raise RuntimeError(
                "Missing outlook timezone. Provide --outlook-timezone 'Eastern Standard Time' "
                "or set PLANNER_TIMEZONE in .env"
            )

        start_week = datetime.fromisoformat(start_iso)
        end_week = datetime.fromisoformat(end_iso)

        # Normalize to display tz so day slicing is consistent.
        if start_week.tzinfo is None:
            start_week = start_week.replace(tzinfo=tz_for_display)
        else:
            start_week = start_week.astimezone(tz_for_display)
        if end_week.tzinfo is None:
            end_week = end_week.replace(tzinfo=tz_for_display)
        else:
            end_week = end_week.astimezone(tz_for_display)

        # Use getSchedule over the whole week (Mon 00:00 -> Sat 00:00) so results are a single availabilityView.
        schedule_email = str(me.get("userPrincipalName") or me.get("mail") or "").strip()
        if not schedule_email:
            raise RuntimeError("Could not determine schedule email from /me")

        schedule = client.calendar_get_schedule(
            schedules=[schedule_email],
            start_local=start_week.replace(tzinfo=None).isoformat(),
            end_local=end_week.replace(tzinfo=None).isoformat(),
            timezone_name=str(outlook_tz),
            interval_minutes=int(args.interval_minutes),
        )

        values = schedule.get("value", []) if isinstance(schedule, dict) else []
        if not values:
            raise RuntimeError(f"getSchedule returned no value: {schedule}")

        view = values[0].get("availabilityView") or ""
        if not isinstance(view, str) or not view:
            raise RuntimeError(f"getSchedule missing availabilityView: {values[0]}")

        interval = timedelta(minutes=int(args.interval_minutes))
        business_start_h, business_start_m = _parse_hhmm(args.business_start)
        business_end_h, business_end_m = _parse_hhmm(args.business_end)

        print("Verified availability (any 30-min start inside these windows):")

        for day_offset in range(5):
            day_start = (start_week + timedelta(days=day_offset)).astimezone(tz_for_display)
            day_date = day_start.date()
            bh_start = datetime(
                day_date.year,
                day_date.month,
                day_date.day,
                business_start_h,
                business_start_m,
                tzinfo=tz_for_display,
            )
            bh_end = datetime(
                day_date.year,
                day_date.month,
                day_date.day,
                business_end_h,
                business_end_m,
                tzinfo=tz_for_display,
            )

            # Compute index range into availabilityView for this day's business hours.
            start_idx = int((bh_start - start_week) / interval)
            end_idx = int((bh_end - start_week) / interval)
            start_idx = max(0, start_idx)
            end_idx = min(len(view), end_idx)

            free_ranges: list[tuple[datetime, datetime]] = []
            run_start: Optional[int] = None
            for idx in range(start_idx, end_idx):
                is_free = view[idx] == "0"
                if is_free and run_start is None:
                    run_start = idx
                if (not is_free) and run_start is not None:
                    run_end = idx
                    if run_end - run_start >= 1:
                        free_ranges.append(
                            (
                                start_week + interval * run_start,
                                start_week + interval * run_end,
                            )
                        )
                    run_start = None

            if run_start is not None:
                run_end = end_idx
                if run_end - run_start >= 1:
                    free_ranges.append(
                        (
                            start_week + interval * run_start,
                            start_week + interval * run_end,
                        )
                    )

            # Clip to business hours and format.
            formatted: list[str] = []
            for rng_start, rng_end in free_ranges:
                s = rng_start.astimezone(tz_for_display)
                e = rng_end.astimezone(tz_for_display)
                if s < bh_start:
                    s = bh_start
                if e > bh_end:
                    e = bh_end
                if e - s >= interval:
                    formatted.append(_format_range(s, e))

            label = bh_start.strftime("%a %Y-%m-%d")
            if formatted:
                print(f"- {label}: " + ", ".join(formatted))
            else:
                print(f"- {label}: (no 30-min availability between {args.business_start}–{args.business_end})")

    if args.write:
        if not lists:
            raise RuntimeError("No To Do lists returned; cannot --write")

        list_id = args.todo_list_id or lists[0].get("id")
        if not list_id:
            raise RuntimeError("Could not determine list_id for --write")

        created = client.create_todo_task(list_id=str(list_id), title=args.task_title)
        task_id = created.get("id")
        if not task_id:
            raise RuntimeError(f"Task created but no id returned: {created}")

        client.patch_todo_task(
            list_id=str(list_id),
            task_id=str(task_id),
            patch={"status": "completed"},
        )
        print(f"Created+completed a test task in list {list_id}: {task_id}")

    print("Validation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
