#!/usr/bin/env python3
"""Pull "My Day" tasks from Microsoft To Do via Graph API.

Usage:
    python -m runs.2026-03-02__orchestrator.scripts.pull_my_day_tasks [--output FILE]

Outputs a JSON array of tasks that are flagged for "My Day" (via linkedResources
or the myDay property), enriched with task body/notes content for orchestrator
context.

Requires: GRAPH_API_SCOPES to include Tasks.ReadWrite (default in this repo).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# ── repo bootstrap ──────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[3]  # up from scripts/ → run/ → runs/ → repo
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def _build_client() -> GraphAPIClient:
    env = load_graph_env(REPO_ROOT)
    authenticator = GraphAuthenticator(repo_root=REPO_ROOT, env=env)
    config = GraphClientConfig(
        base_url=env.base_url,
        scopes=env.scopes,
        planner_timezone=env.planner_timezone,
    )
    return GraphAPIClient(authenticator=authenticator, config=config)


def _get_all_tasks(client: GraphAPIClient, list_id: str) -> List[Dict[str, Any]]:
    """Page through all tasks in a To Do list."""
    tasks: List[Dict[str, Any]] = []
    url = f"me/todo/lists/{list_id}/tasks?$top=100"

    while url:
        resp = client.get(url)
        tasks.extend(resp.get("value", []))
        url = resp.get("@odata.nextLink")

    return tasks


def _is_my_day(task: Dict[str, Any]) -> bool:
    """Check if a task is flagged for My Day.

    Microsoft Graph exposes this via the linkedResources collection
    (applicationName = 'myDay') or, on newer API versions, a direct
    'isReminderOn' / myDay property. We check multiple signals.
    """
    # Direct myDay property (beta/newer v1.0 behavior)
    if task.get("isReminderOn"):
        pass  # Not reliable for My Day; just a reminder flag

    # The most reliable check: linkedResources with myDay
    linked = task.get("linkedResources", [])
    for lr in linked:
        if lr.get("applicationName", "").lower() == "myday":
            return True

    return False


def _simplify_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the fields the orchestrator needs."""
    body = task.get("body", {})
    body_text = body.get("content", "") if isinstance(body, dict) else ""

    # Parse dates
    due = task.get("dueDateTime")
    due_str = None
    if due and isinstance(due, dict):
        due_str = due.get("dateTime", "")[:10]  # YYYY-MM-DD

    created = task.get("createdDateTime", "")
    modified = task.get("lastModifiedDateTime", "")

    return {
        "id": task.get("id"),
        "title": task.get("title", ""),
        "status": task.get("status", ""),
        "importance": task.get("importance", "normal"),
        "due_date": due_str,
        "body_preview": body_text[:500] if body_text else None,
        "body_full": body_text if body_text else None,
        "created": created,
        "modified": modified,
        "categories": task.get("categories", []),
        "has_attachments": task.get("hasAttachments", False),
    }


def pull_my_day_tasks(client: GraphAPIClient) -> List[Dict[str, Any]]:
    """Pull all incomplete tasks across all To Do lists, keeping only My Day or
    all incomplete tasks (since My Day detection via Graph is unreliable).

    Returns tasks sorted by importance (high first) then due date.
    """
    lists_resp = client.todo_lists()
    all_lists = lists_resp.get("value", [])

    all_tasks: List[Dict[str, Any]] = []

    for tl in all_lists:
        list_id = tl["id"]
        list_name = tl.get("displayName", "")

        # Skip well-known system lists that aren't task lists
        if list_name.lower() in ("flagged emails",):
            continue

        tasks = _get_all_tasks(client, list_id)

        for t in tasks:
            # Only include incomplete tasks
            if t.get("status") == "completed":
                continue

            simplified = _simplify_task(t)
            simplified["list_name"] = list_name
            simplified["is_my_day"] = _is_my_day(t)
            all_tasks.append(simplified)

    # Sort: My Day first, then by importance (high > normal > low), then by due date
    importance_order = {"high": 0, "normal": 1, "low": 2}
    all_tasks.sort(key=lambda t: (
        0 if t["is_my_day"] else 1,
        importance_order.get(t.get("importance", "normal"), 1),
        t.get("due_date") or "9999-99-99",
    ))

    return all_tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull My Day tasks from Microsoft To Do")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output file path (default: stdout)")
    parser.add_argument("--all", action="store_true",
                        help="Include all incomplete tasks, not just My Day")
    args = parser.parse_args()

    client = _build_client()
    tasks = pull_my_day_tasks(client)

    if not args.all:
        my_day_tasks = [t for t in tasks if t["is_my_day"]]
        # If My Day detection found nothing, fall back to all incomplete
        if my_day_tasks:
            tasks = my_day_tasks
        else:
            print("⚠ My Day detection via Graph found 0 tasks. "
                  "Returning all incomplete tasks (Graph My Day detection is unreliable).",
                  file=sys.stderr)

    output = json.dumps(tasks, indent=2, default=str)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote {len(tasks)} tasks to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
