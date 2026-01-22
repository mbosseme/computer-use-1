---
name: "Microsoft Graph Email Search"
description: "Patterns for finding and exporting mail via Microsoft Graph (delegated auth), with safe defaults and paging/retry guidance."
tools:
  - terminal
---

## When to use
- The user asks to **find**, **export**, or **summarize** emails (sent or received) using Microsoft Graph.

## Preconditions
- Delegated auth is configured (see [docs/GRAPH_AUTH_REPLICATION_GUIDE.md](../../../docs/GRAPH_AUTH_REPLICATION_GUIDE.md)).
- App permissions include Mail scopes:
  - Minimal read-only: `Mail.Read`
  - If you also need move/label/update: `Mail.ReadWrite`

## Recommended approach (safe + repeatable)
- Prefer **read-only** endpoints first.
- Write exports to a run-local or ignored location:
  - Repo-root temp: `tmp/...` (ignored)
  - Run-local: `runs/<RUN_ID>/exports/...`
- Use the repo utility:
  - `python -m agent_tools.graph.export_sent_mail --to <RECIPIENT_EMAIL> --include-cc --out-dir tmp/mail_exports_<slug>`

## Query strategy
### Sent mail to a recipient
- Start with SentItems:
  - `GET /me/mailFolders/SentItems/messages`

### Received mail (Inbox) — beware subfolders
- Do **not** assume mail lives in the top-level Inbox. Many mailboxes have rules that move messages into **Inbox subfolders** (e.g., “Addressed”).
- If a sender/message is visible in Outlook but your Inbox query returns empty, use one of these patterns:
  - **Mailbox-wide search (fast path):**
    - `GET /me/messages?$search="from:<sender@domain.com>"&$top=25`
    - Add header: `ConsistencyLevel: eventual`
    - Note: Graph typically disallows combining `$search` with `$orderby`; fetch a small set and **sort locally** by `receivedDateTime`.
  - **Inbox subtree scan (reliable fallback):**
    - Enumerate Inbox children (and grandchildren) via `GET /me/mailFolders/inbox/childFolders` and recurse via each folder’s `childFolders`.
    - Then query messages within candidate folders: `GET /me/mailFolders/<folderId>/messages?$top=25`.
    - Practical heuristic: if the user names a folder (e.g., “Addressed”), do a breadth-first search by `displayName` to find its folderId, then query it directly.

### Filtering vs search
- **Try `$filter` first** (deterministic), but be ready for tenant-specific limitations.
- If Graph returns filter errors (e.g., `ErrorInvalidUrlQueryFilter`), **fall back to `$search`**:
  - Include header: `ConsistencyLevel: eventual`
  - Example: `$search="recipients:<email>"`

## Creating draft emails (Drafts)
- To create a draft (without sending), use:
  - `POST /me/messages`
  - This creates a message in **Drafts** by default.
- Keep **HITL** for sending: do not send mail without explicit user confirmation.
- Recommended helper (repo utility):
  - `python -m agent_tools.graph.create_draft_from_md --md <path/to/draft.md> --resolve-to-name "First Last"`
  - If name resolution is ambiguous, the tool will list candidates and still create a draft with no recipient.

### Pagination
- Respect `@odata.nextLink` until exhausted.
- NextLink is typically an **absolute URL**; your HTTP client should accept absolute URLs directly.

## Output hygiene
- The exported document may contain sensitive content.
- Do not commit exports to git.
- Avoid pasting large email bodies into chat unless explicitly requested.

## Troubleshooting
- 401: token expired → retry once with a fresh token.
- 403: missing Mail scopes or missing admin consent.
- Empty results: confirm you’re searching SentItems vs Inbox and whether you included Cc.
