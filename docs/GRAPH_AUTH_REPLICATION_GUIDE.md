# Microsoft Graph Auth Replication Guide (macOS, Delegated, Interactive)

This document is intended to be copied into another repo to help an automated coding agent replicate the working authentication + Graph interaction pattern used in this repo for Microsoft Office resources (Calendar + Microsoft To Do; optionally Mail).

## Goal

Implement **delegated** Microsoft Graph access on macOS using **MSAL Public Client + interactive Authorization Code + PKCE loopback**. This avoids Conditional Access issues that often break device-code flow (e.g., requiring device compliance / PRT claims).

Key outcomes:
- Silent auth on subsequent runs via a local token cache
- Interactive system-browser auth when silent auth fails
- Reliable delegated access to:
  - Calendar (read calendarView, create events)
  - Microsoft To Do tasks (read/update/create tasks)
  - (Optional) Mail (read/move messages if consented)

---

## 1) Azure AD App Registration (Entra ID)

Create a **Public client / Mobile & desktop** app registration.

### Redirect URI (critical)
- Add redirect URI: `http://localhost`
  - MSAL uses a loopback redirect on localhost (often with a dynamic port). Registering `http://localhost` enables this.

### API permissions (delegated)
Configure delegated permissions in the app registration:
- `User.Read`
- `Tasks.ReadWrite`
- `Calendars.ReadWrite`
- (Optional) `Mail.Read` (use `Mail.ReadWrite` only if you need to modify mail)

If your tenant blocks user consent, an admin must grant consent.

---

## 2) Local Configuration (.env)

Create a `.env` file at repo root:

```bash
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_AUTHORITY_URL=https://login.microsoftonline.com/${AZURE_TENANT_ID}

# Comma-separated list; runtime filters reserved scopes.
GRAPH_API_SCOPES=Calendars.ReadWrite,Mail.Read,offline_access,Tasks.ReadWrite,User.Read

# Local token cache for silent auth on subsequent runs
TOKEN_CACHE_FILE=.token_cache.json

# Optional override
GRAPH_API_BASE_URL=https://graph.microsoft.com/v1.0

# Optional: timezone for calendar event creation
# Optional: timezone hints
# - Outlook calendar endpoints use a Windows timezone name for normalization via the Prefer header
#   (example: Eastern Standard Time)
# - For printing/formatting locally, use an IANA timezone name
#   (example: America/New_York)
PLANNER_TIMEZONE=Eastern Standard Time
```

Notes:
- This pattern is **public client** delegated auth; a client secret is not required.
- Leave `offline_access` in the env if you want; the runtime should **filter it out** of the MSAL request to avoid “reserved scope” errors.
- If you add/remove scopes, delete `.token_cache.json` and re-authenticate.

---

## 3) Python Dependencies

Minimal dependencies:

```bash
pip install msal python-dotenv requests
```

If you need timezone support for calendar event creation:

```bash
pip install pytz
```

---

## 4) Reference Implementation (Auth + Graph Client)

> **IMPORTANT: USING THE EXISTING LIBRARY**
> If you are working inside this repo (or one with `agent_tools`), **use the existing library** instead of re-implementing auth.
>
> **Correct Pattern (using `agent_tools.graph`):**
> ```python
> from pathlib import Path
> from agent_tools.graph.env import load_graph_env
> from agent_tools.graph.auth import GraphAuthenticator
> 
> # load_graph_env ensures scopes match .env exactly
> repo_root = Path.cwd()  # or Path(__file__).parents[...]
> env = load_graph_env(repo_root)
> auth = GraphAuthenticator(repo_root=repo_root, env=env)
> ```
> **Anti-Pattern:** Do NOT try to instantiate `GraphAuthenticator` with manual `client_id` arguments. The library class requires `env`.

### 4.1 Reference Class (for manual implementation)

If you are replicating this in a **new** repo without `agent_tools`, use this reference implementation:

### 4.1.1 GraphAuthenticator (MSAL public client)

Key requirements:
- Use `PublicClientApplication`
- Use `SerializableTokenCache` persisted to a local JSON file
- Attempt `acquire_token_silent` first
- Fall back to `acquire_token_interactive` (system browser)
- Filter reserved scopes before calling MSAL

Example:

```python
import os
from typing import Optional
from msal import PublicClientApplication, SerializableTokenCache
from dotenv import load_dotenv

load_dotenv()

_RESERVED = {"offline_access", "openid", "profile"}


class GraphAuthenticator:
    def __init__(self):
        self.client_id = os.environ["AZURE_CLIENT_ID"].strip().lower()
        self.authority = os.environ["AZURE_AUTHORITY_URL"].strip()
        raw_scopes = os.getenv(
            "GRAPH_API_SCOPES",
            "Calendars.ReadWrite,Mail.Read,offline_access,Tasks.ReadWrite,User.Read",
        )
        self.scopes = [s.strip() for s in raw_scopes.replace(" ", ",").split(",") if s.strip()]
        self.cache_path = os.getenv("TOKEN_CACHE_FILE", ".token_cache.json")

        self.cache = SerializableTokenCache()
        if os.path.exists(self.cache_path):
            self.cache.deserialize(open(self.cache_path, "r", encoding="utf-8").read())

        self.app = PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=self.cache,
        )

    def _save_cache(self) -> None:
        if self.cache.has_state_changed:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                f.write(self.cache.serialize())

    def get_access_token(self) -> Optional[str]:
        effective_scopes = [s for s in self.scopes if s not in _RESERVED]

        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(effective_scopes, account=accounts[0])
            if result and "access_token" in result:
                return result["access_token"]

        # Interactive fallback (system browser + loopback)
        result = self.app.acquire_token_interactive(
            scopes=effective_scopes,
            prompt="select_account",
            timeout=600,
        )
        if result and "access_token" in result:
            self._save_cache()
            return result["access_token"]

        return None
```

### 4.2 GraphAPIClient (requests wrapper)

Requirements:
- Add `Authorization: Bearer <token>` header
- Add a one-time retry on 401 by clearing cached token
- Log errors with Graph response body where possible

Example:

```python
import os
import requests
from typing import Any, Dict, Optional


class GraphAPIClient:
    def __init__(self, authenticator):
        self.base_url = os.getenv("GRAPH_API_BASE_URL", "https://graph.microsoft.com/v1.0")
        self.authenticator = authenticator
        self._token = None

    def _headers(self) -> Dict[str, str]:
        if not self._token:
            self._token = self.authenticator.get_access_token()
            if not self._token:
                raise RuntimeError("Failed to obtain Graph access token")
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        for attempt in (1, 2):
            resp = requests.request(method, url, headers=self._headers(), timeout=30, **kwargs)
            if resp.status_code == 401 and attempt == 1:
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
```

---

## 5) Resource Patterns (Calendar + To Do)

### 5.1 Calendar read (calendarView)

Read upcoming events:

- Endpoint: `GET /me/calendarView?startDateTime=...&endDateTime=...`
- Common params:
  - `$select=subject,start,end,isAllDay,showAs,attendees,body`
  - `$top=1000`

Example:

```python
from datetime import datetime, timedelta

now_utc = datetime.utcnow().replace(microsecond=0)
end_utc = now_utc + timedelta(days=14)
start_iso = now_utc.isoformat() + "Z"
end_iso = end_utc.isoformat() + "Z"

resp = client.get(
    f"me/calendarView?startDateTime={start_iso}&endDateTime={end_iso}",
    params={"$select": "subject,start,end,isAllDay,showAs,attendees,body", "$top": 1000},
)
items = resp.get("value", [])
```

### 5.1b Verified availability (free/busy)

If you need to compute meeting availability windows (instead of inferring from event subjects), use:

- Endpoint: `POST /me/calendar/getSchedule`
- Set `availabilityViewInterval` (e.g., 30) and decode `availabilityView` (`0` = free)

This is the most reliable way to produce and *verify* “available 30-minute slots” for a date range.

### 5.2 Calendar write (create event)

Create an event:

- Endpoint: `POST /me/events`
- Payload includes `subject`, `body`, `start`, `end`, `timeZone`

Example:

```python
payload = {
  "subject": "Task: Example",
  "body": {"contentType": "Text", "content": "Notes..."},
  "start": {"dateTime": "2026-01-10T14:00:00", "timeZone": "America/New_York"},
  "end": {"dateTime": "2026-01-10T14:30:00", "timeZone": "America/New_York"},
  "showAs": "busy",
  "isAllDay": False,
}
created = client.post("me/events", json=payload)
```

### 5.3 Microsoft To Do tasks

List To Do lists:
- `GET /me/todo/lists`

List tasks in a list:
- `GET /me/todo/lists/{listId}/tasks`

Get a single task:
- `GET /me/todo/lists/{listId}/tasks/{taskId}`

Create a task:
- `POST /me/todo/lists/{listId}/tasks`

Update a task:
- `PATCH /me/todo/lists/{listId}/tasks/{taskId}`

Due date format:
- Graph expects:

```json
"dueDateTime": {"dateTime": "YYYY-MM-DDT00:00:00", "timeZone": "UTC"}
```

### 5.4 Mail search / export (SentItems)

If you need a deterministic way to find and export sent messages (e.g., “all emails I sent to `<RECIPIENT_EMAIL>`”), use SentItems:

- Endpoint: `GET /me/mailFolders/SentItems/messages`
- Minimal delegated permission: `Mail.Read` (use `Mail.ReadWrite` only if you need to modify mail)

Filtering vs search:
- Prefer `$filter` first (deterministic), but some tenants reject recipient filters with errors like `ErrorInvalidUrlQueryFilter`.
- If that happens, fall back to `$search`:
    - Add header `ConsistencyLevel: eventual`
    - Example query: `$search="recipients:<recipient_email>"`

Pagination:
- Respect `@odata.nextLink` until exhausted.
- `@odata.nextLink` is commonly an absolute URL; your client should be able to request absolute URLs directly.

Output hygiene:
- Treat exported mail content as sensitive and keep it out of git.
- Write exports to an ignored folder (e.g., repo-root `tmp/`) or a run-local folder under `runs/<RUN_ID>/exports/`.

---

## 6) Diagnostics + Troubleshooting

### Token scope visibility
Log the `scp` claim from the JWT (best-effort) so you can confirm granted scopes match expectations.

Common issue:
- You request `Mail.ReadWrite` but token does not include it → mail move operations should be skipped.

### Conditional Access (device compliance)
If device-code flow fails with tenant policies (example error class: `AADSTS530033`), switch to **interactive loopback** only.

### Admin consent
If users cannot consent, have an admin grant tenant-wide consent. A typical admin-consent entry point is:

```
https://login.microsoftonline.com/<tenant_id>/v2.0/adminconsent?client_id=<application_id>&redirect_uri=http://localhost
```

(Consent applies to delegated permissions configured on the app registration.)

### Cache pitfalls
If you change scopes:
- Delete the token cache file (e.g., `.token_cache.json`)
- Run interactive auth again

---

## 7) Minimal Validation Script

Create a quick `tests/test_graph_setup.py` equivalent in the new repo:
- Verify env vars are present
- Acquire token
- `GET /me` to validate connectivity
- (Optional) `GET /me/todo/lists` and `GET /me/calendarView` to validate resource access

Example commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tests/test_graph_setup.py
```

---

## 8) Security Notes

- Keep `.env` and token cache out of git (`.gitignore`).
- This is delegated access on a developer machine; do not treat it as a headless server auth solution.
- If you ever need headless automation, the model changes substantially (application permissions, daemon app, different security posture).
