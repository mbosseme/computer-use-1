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
- Reusable structured-draft utility (for multi-section request emails):
  - `python tools/graph/draft_structured_email.py --input <spec.json> [--fallbacks <fallbacks.json>]`
  - Use this when a request has repeated sections, placeholders, and standardized asks.
  - Use `create_draft_from_md` for freeform one-off messages; use `draft_structured_email.py` for consistent, templated updates across runs.

## Evidence-led drafts with inline images (CID)
When the user wants a draft that “reads like a clear explanation supported by images”, prefer **inline CID images placed immediately after the relevant paragraph**, not a lumped “Evidence” section.

### Structure (recommended)
- 1–3 sentence summary up top (scope + what was validated)
- For each claim:
  - 1–2 sentences explaining what the screenshot demonstrates
  - The screenshot directly beneath (inline `<img src="cid:<contentId>">`)
- Preserve the quoted thread below (reply-all drafts typically include it)

### Implementation pattern (Graph)
- Create (or locate) the draft message.
- Fetch the current HTML body and split out the quoted thread tail (keep everything from the first `From:` block onward).
- Replace the top-of-email body with your narrative + inline images, then append the quoted tail.
- Attach images as inline file attachments with stable `contentId` values.
  - Keep the `contentId` stable even if you swap the image file (so the HTML `<img src="cid:...">` continues to work).

### Repo tool (starter)
- Update an existing draft with inline images (NOT SENT):
  - `python scripts/update_outlook_draft_inline_evidence.py --draft-id <DRAFT_MESSAGE_ID> --images-json <PATH> --preserve-quoted --body-html <OPTIONAL_HTML>`

### Common pitfalls
- If images don’t render:
  - Confirm the HTML uses `cid:<contentId>` (no filename suffix).
  - Confirm the attachment is `isInline: true` and `contentId` exactly matches.
- If the quoted thread disappears:
  - Make sure you append the preserved tail when patching the draft body.
- If whitespace-heavy screenshots make the email hard to read:
  - Crop to `_clean.png` first (see the browser automation skill’s screenshot trimming section).

### Pagination
- Respect `@odata.nextLink` until exhausted.
- NextLink is typically an **absolute URL**; your HTTP client should accept absolute URLs directly.

## Attachment operations (file + inline)
Two modules handle attachments — use the right one for the job:

| Module | Use Case |
|--------|----------|
| `agent_tools.graph.attachments` | Regular file attachments (PDF, XLSX, etc.) — attach, download, list |
| `agent_tools.graph.inline_images` | CID inline images in HTML body — add, replace, delete |

Both re-export `AttachmentInfo` and `list_attachments`, so you can import from either.

### Attaching a file to a draft
```python
from agent_tools.graph.attachments import attach_file
info = attach_file(client, draft_id, Path("report.pdf"), skip_if_exists=True)
```
- Uses the small-file upload path (< 3 MB base64).
- `skip_if_exists=True` (default) prevents duplicate attachments on retries.

### Downloading attachments from a message
```python
from agent_tools.graph.attachments import download_attachments
paths = download_attachments(client, message_id, Path("tmp/downloads"))
```
- By default skips inline (CID) attachments; pass `include_inline=True` to get everything.
- Optional `filter_fn` predicate for selective download (e.g., only `.xlsx` files).

### Listing attachments
```python
from agent_tools.graph.attachments import list_attachments, AttachmentInfo
atts = list_attachments(client, message_id)
```

## Reply-all drafts
When the original message has multiple recipients and you need to keep everyone on the thread:
```python
from agent_tools.graph.drafts import create_reply_all_draft
result = create_reply_all_draft(client, message_id=msg_id, body="<p>New content</p>")
```
- Uses `POST /me/messages/{id}/createReplyAll` (empty body), then PATCHes new content above the quoted history.
- Optionally override `to` / `cc` lists while keeping the reply-all structure.
- For reply to sender only, use `create_reply_draft` instead.

## Draft management (find, update, verify)

### Finding an existing draft by subject
```python
from agent_tools.graph.drafts import find_draft_by_subject
draft = find_draft_by_subject(client, subject="Q4 spending review")
if draft:
    draft_id = draft["id"]
```
- Scans `me/mailFolders/drafts/messages` with case-insensitive substring match.
- Returns the most-recently-modified match, or None.

### Updating a draft's body
```python
from agent_tools.graph.drafts import update_draft_body
update_draft_body(client, draft_id, "<p>New HTML content</p>", preserve_quoted=True)
```
- `preserve_quoted=True` keeps the existing quoted reply tail and only replaces the top portion.

### Verifying a draft against expected content
```python
from agent_tools.graph.drafts import verify_draft
result = verify_draft(client, draft_id, expected_phrases=["spend analysis", "facility breakdown"])
print(f"{result.passed_count}/{result.total_count} checks passed")
assert result.all_passed
```
- Fetches draft body + metadata + attachment list.
- Runs case-insensitive substring checks on body HTML for each phrase.
- Returns `DraftVerifyResult` with `all_passed`, `phrase_results`, `attachment_names`, etc.

## Thread export to Markdown
Export an entire conversation thread (by subject) to a chronologically-ordered Markdown file:
```python
from agent_tools.graph.mail_search import export_thread_markdown
export_thread_markdown(client, subject="McKinsey product codes", out_path=Path("tmp/thread.md"))
```
- Searches mailbox-wide via `$search`, filters client-side by subject substring.
- Converts HTML bodies to plain text.
- Sorts oldest-first for reading order.

## Finding the latest message from a sender
```python
from agent_tools.graph.mail_search import find_latest_from_sender
msg = find_latest_from_sender(client, '"Itani"', with_attachments=True)
if msg:
    print(msg["subject"], msg["receivedDateTime"])
```
- Searches mailbox, sorts by date, validates sender tokens match.
- Useful for "find the most recent email with attachments from X" pattern.

## General-purpose mail search
```python
from agent_tools.graph.mail_search import search_messages
msgs = search_messages(client, query='"McKinsey" AND "sample"', folder="Inbox", top=25)
```
- Wraps `$search` + `ConsistencyLevel: eventual` + local sort by date.
- Optional `folder` param (well-known name like `"SentItems"` or folder ID).
- Handles pagination via `@odata.nextLink` automatically.

## Output hygiene
- The exported document may contain sensitive content.
- Do not commit exports to git.
- Avoid pasting large email bodies into chat unless explicitly requested.

## Troubleshooting
- 401: token expired → retry once with a fresh token.
- 403: missing Mail scopes or missing admin consent.
- Empty results: confirm you’re searching SentItems vs Inbox and whether you included Cc.
