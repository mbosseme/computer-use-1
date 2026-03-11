## Product requirements: Daily Meeting Notes Automation (Outlook → OneDrive-synced Word doc + Otter ZIP append)

### 1) Objective

Create a **daily runnable automation script** (executed on Mac, from VS Code) that:

1. **Pre-creates** a Word document for each meeting on a target day using Outlook calendar data (Microsoft Graph).
2. Ensures **no duplicates** for the same meeting, even if rerun multiple times.
3. Produces **highly searchable** meeting notes artifacts for **M365 Copilot retrieval** (by meeting title, date/time, key attendees).
4. Detects **manually exported Otter ZIP files** in a designated OneDrive-synced folder and **appends** transcript + comments to the **end** of the corresponding meeting Word document **without overwriting** any existing content (manual notes, pasted screenshots, etc.).

---

### 2) Scope and constraints

* **Primary UI**: none (CLI/script). Optional lightweight prompts in terminal for ambiguous matches.
* **Storage**: local folder structure that is synced to **OneDrive** (so it’s indexable by M365 Copilot).
* **Notes format**: **Word (.docx)** per meeting (initially). (Folder-per-meeting is optional; not required for v1.)
* **Transcript ingestion**: **manual Otter export** into a known folder as **ZIP** containing transcript + “comments/notes” (speaker tags).
* **Non-goals (v1)**:

  * Fully automating Otter recording or export.
  * Perfect speaker identification.
  * OneNote integration (optional future).
  * Editing previously appended transcript blocks (append-only behavior preferred).

---

### 3) Users and user stories

* As a user, I want a daily run to create meeting note docs so I can open the doc during the meeting and type notes/paste screenshots.
* As a user, I want reruns to be safe (no duplicates, no overwrites).
* As a user, I want M365 Copilot to answer: “Summarize my 1:1 yesterday with Jonathan” by finding the correct doc quickly.
* As a user, after I export an Otter ZIP, I want the script to find the right meeting doc and append the transcript/comments to the bottom.

---

### 4) Inputs and data sources

**Microsoft Graph (already authorized/scoped):**

* Calendar events for a day/time range (calendarView).
* Event fields: subject, start/end, organizer, attendees (and response status), location, online meeting join URL, body preview/body.

**File system (OneDrive-synced):**

* A root notes directory ('/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notetaking').
* An “Otter exports inbox” directory ('/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Otter Exports') where ZIPs land.

---

### 5) Output artifacts (file conventions)

#### 5.1 Directory structure (v1)

A simple date-based folder:

* `OneDriveRoot/Meeting Notes/YYYY/MM/DD/`

Otter inbox:

* `OneDriveRoot/Otter Exports Inbox/` (or wherever you choose)

Script metadata:

* `OneDriveRoot/Meeting Notes/_index/` for sidecars and logs

#### 5.2 One document per meeting (v1)

Create one `.docx` per meeting, stored under that date folder.

**Filename requirements (search-friendly, deterministic, not too long):**

* Must include:

  * Date (YYYY-MM-DD)
  * Start time (HHMM, local)
  * Meeting subject (sanitized)
  * 1–3 key attendee last names (or first names if last absent)
* Must also include an **internal unique key** so duplicates are impossible:

  * Prefer: short hash of Graph `event.id` (e.g., first 8 chars of SHA-1)
  * This key can be in filename suffix OR in a sidecar index (recommended: both if feasible)

**Example:**

* `2026-03-04 1000 - 1-1 Jonathan - Matt, Jonathan - eidA1B2C3D4.docx`

**Length rule:**

* Cap filename length (e.g., 160–180 chars). Truncate subject/attendees as needed but retain date/time and eid hash.

---

### 6) Document template (content requirements)

Each created doc should have a consistent structure and clearly separated “manual” vs “automation” areas to prevent overwrites.

**Top section (auto-populated):**

* Title line: `{Subject}`
* Meeting time: `{Start} – {End} (TZ)`
* Organizer
* Location / Join link
* Attendees grouped by response:

  * Accepted
  * Tentative
  * No response
  * Declined
* Meeting description / agenda:

  * event body (plain text) or bodyPreview
* “Context links” section:

  * Teams/Zoom link, meeting-related URLs detected from body (optional)
* **Hidden/low-visibility internal metadata** (must exist somewhere for robustness):

  * Graph event ID
  * iCalUId (if available)
  * Created timestamp (script)
  * Last updated timestamp (script)

**Manual notes section (user editable, never overwritten):**

* Heading: `Manual Notes`
* Subheadings:

  * `Decisions`
  * `Action Items`
  * `Open Questions`
  * `Key Takeaways`
* `Screenshots / Images` placeholder (user pastes images here)

**Auto-append section (append-only):**

* Heading: `Otter Transcript Imports (Append-Only)`
* For each import, append a block:

  * Import header: timestamp + ZIP filename + (optional) confidence score
  * `Transcript` content
  * `Otter Comments/Tags` content

**Critical rule:** the script may insert new content **only**:

* In the initial creation (template)
* Or appended under the `Otter Transcript Imports` section
* It must never modify/remove existing paragraphs elsewhere.

---

### 7) Duplicate prevention and idempotency

The script must be safe to run multiple times per day.

**7.1 Meeting doc de-dupe**

* Maintain an index file:

  * `Meeting Notes/_index/events-index.json`
  * Mapping: `eventId → docPath`, plus key fields (start/end, subject, attendees)
* On each run:

  * If `eventId` already exists in index and doc exists: do not create a new doc.
  * If index missing but a doc filename contains matching `eidHASH`: treat as existing and repair index.

**7.2 Transcript import de-dupe**

* Maintain a transcript import index:

  * `Meeting Notes/_index/transcripts-index.json`
  * Track processed ZIPs by:

    * ZIP filename + file size + modified timestamp
    * Optional: hash of ZIP bytes for robustness
* Additionally, stamp each appended import block with:

  * `Source ZIP: <filename>` so the script can scan the doc and confirm it’s already appended even if index is lost.

---

### 8) Otter ZIP handling requirements

**8.1 ZIP discovery**

* Scan Otter inbox folder for new `.zip` files.
* “New” means: not present in transcripts-index OR changed since last processed.

**8.2 ZIP extraction**

* Extract to a temp directory.
* Identify transcript file(s) and comments file(s).

  * Transcript could be `.docx`, `.txt`, `.md`, `.pdf` (support docx/txt required for v1; pdf optional).
  * Comments/tags could be `.txt`, `.csv`, `.json` (support txt/json required for v1).

**8.3 Content normalization**

* Convert transcript + comments to plain text for appending.
* Preserve basic formatting:

  * Speaker labels
  * Timestamps (if present)
  * Paragraph breaks

---

### 9) Matching logic: Which meeting doc should receive which ZIP?

Provide a deterministic scoring model that uses time and (optionally) text cues.

**9.1 Primary signal: time-window match**

* Use ZIP modified/created time (filesystem) as proxy for export time.
* Candidate meetings:

  * Meetings whose **end time** is within a configurable window before ZIP time (e.g., 0–6 hours).
  * Also consider meetings spanning the export time (in case export happens mid-meeting).

**9.2 Secondary signals (if available in transcript header)**
If the extracted transcript includes:

* A meeting title
* A date/time line
* Attendee names
  Use fuzzy matching against event subject and attendees.

**9.3 Scoring (example)**

* Time proximity score (0–70 points):

  * Highest if ZIP time is within 0–60 minutes after meeting end.
* Subject similarity (0–20 points)
* Attendee name overlap (0–10 points)

**Decision rules**

* If top candidate score ≥ threshold (e.g., 75): auto-append.
* If ambiguous (two close candidates or below threshold):

  * Default behavior: do not append; write to a “Needs Review” log.
  * Optional behavior (config flag): prompt user to pick 1 of N candidates in terminal.

---

### 10) Operational behavior

**10.1 Execution modes**

* `--date YYYY-MM-DD` (default: today)
* `--create-only` (no transcript handling)
* `--append-transcripts-only`
* `--dry-run` (prints actions, no writes)
* `--verbose`

**10.2 Logging**

* Write logs to:

  * `Meeting Notes/_index/logs/YYYY-MM-DD-run.log`
* Log every create/skip/append decision with:

  * eventId, docPath
  * zip filename
  * match score + reason

**10.3 Failure behavior**

* If Graph call fails: do not create partial docs; fail cleanly.
* If doc append fails (file locked, sync issue): leave ZIP unprocessed and retry next run.
* If ZIP extraction fails: log and skip.

---

### 11) Security and privacy

* Store tokens using existing secure method (e.g., MSAL token cache in keychain if already used).
* Do not write raw access tokens to disk.
* Content at rest is in OneDrive-synced storage; assume corporate compliance policies apply.

---

### 12) Acceptance criteria (definition of done)

1. Running the script twice on the same day creates **no duplicate meeting docs**.
2. Each created doc has:

   * Searchable filename with date/time/subject/key attendees
   * Auto-populated meeting metadata in the header
   * A manual notes section
   * An append-only Otter section
3. Dropping an Otter ZIP into the inbox and rerunning the script:

   * Appends transcript + comments to the correct meeting doc
   * Does not overwrite manual notes or images
   * Does not append the same ZIP twice
4. Ambiguous transcript matches:

   * Are logged for review (and optionally prompt if enabled)
5. All actions are logged, and the index files are updated reliably.

---

### 13) Implementation notes for the Copilot agent (non-binding guidance)

* Language: Python recommended (easy `.docx` editing via `python-docx`, ZIP handling, MSAL).
* Libraries:

  * `msal`, `requests` (Graph)
  * `python-docx` (create + append)
  * `zipfile`, `hashlib`
* Keep a small `config.yaml` for folder paths, time windows, filename rules, and thresholds.
* Write unit tests for:

  * filename generation/truncation
  * event de-dupe/index behavior
  * transcript matching scorer
  * “already appended” detection