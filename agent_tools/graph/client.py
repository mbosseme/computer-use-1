from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from agent_tools.graph.auth import GraphAuthenticator


@dataclass
class GraphClientConfig:
    base_url: str
    scopes: list[str]
    planner_timezone: Optional[str] = None


class GraphAPIClient:
    def __init__(self, *, authenticator: GraphAuthenticator, config: GraphClientConfig):
        self._authenticator = authenticator
        self._config = config
        self._token: Optional[str] = None

    def _headers(self) -> Dict[str, str]:
        if not self._token:
            token_result = self._authenticator.acquire_access_token(scopes=self._config.scopes)
            self._token = token_result.access_token

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self._config.planner_timezone:
            # Helps normalize times returned by Outlook calendar endpoints.
            headers["Prefer"] = f'outlook.timezone="{self._config.planner_timezone}"'

        return headers

    def request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self._config.base_url.rstrip('/')}/{path.lstrip('/')}"

        for attempt in (1, 2):
            resp = requests.request(method, url, headers=self._headers(), timeout=30, **kwargs)
            if resp.status_code == 401 and attempt == 1:
                # Retry once with a fresh token.
                self._token = None
                continue
            if resp.status_code >= 400:
                raise RuntimeError(f"Graph {method} {path} failed: {resp.status_code} {resp.text}")
            return resp.json() if resp.content else {}

        return {}

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.request("GET", path, params=params)

    def post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        return self.request("POST", path, json=json)

    def patch(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        return self.request("PATCH", path, json=json)

    # Convenience wrappers for common resources

    def me(self) -> Dict[str, Any]:
        return self.get("me")

    def todo_lists(self) -> Dict[str, Any]:
        return self.get("me/todo/lists")

    def calendar_view(self, *, start_iso: str, end_iso: str) -> Dict[str, Any]:
        return self.get(
            "me/calendarView",
            params={
                "startDateTime": start_iso,
                "endDateTime": end_iso,
                "$select": "subject,start,end,isAllDay,showAs,attendees,bodyPreview",
                "$top": 1000,
            },
        )

    def calendar_get_schedule(
        self,
        *,
        schedules: list[str],
        start_local: str,
        end_local: str,
        timezone_name: str,
        interval_minutes: int = 30,
    ) -> Dict[str, Any]:
        # POST /me/calendar/getSchedule
        # https://learn.microsoft.com/graph/api/calendar-getschedule
        return self.post(
            "me/calendar/getSchedule",
            json={
                "schedules": schedules,
                "startTime": {"dateTime": start_local, "timeZone": timezone_name},
                "endTime": {"dateTime": end_local, "timeZone": timezone_name},
                "availabilityViewInterval": interval_minutes,
            },
        )

    def create_todo_task(self, *, list_id: str, title: str) -> Dict[str, Any]:
        return self.post(f"me/todo/lists/{list_id}/tasks", json={"title": title})

    def patch_todo_task(self, *, list_id: str, task_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        return self.patch(f"me/todo/lists/{list_id}/tasks/{task_id}", json=patch)
