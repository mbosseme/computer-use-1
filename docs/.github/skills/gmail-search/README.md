# Skill: Gmail Search

## Description
This skill allows the agent to search for and read emails from the user's Gmail account using the Gmail API. It handles OAuth 2.0 authentication via a local server flow (Human-in-the-Loop) and supports persistent token storage to minimize login prompts.

## Prerequisites
1.  **Google Cloud Project**: A project with the **Gmail API** enabled.
    *   **Configuration**: To ensure tokens expire automatically after 7 days (security best practice), set the **OAuth Consent Screen** > **Publishing Status** to **Testing**.
2.  **Credentials**: An OAuth 2.0 Client ID `credentials.json` file.
    *   Download from Google Cloud Console -> APIs & Services -> Credentials -> Create Credentials -> OAuth Client ID (Desktop App).
    *   Place this file in `runs/<RUN_ID>/inputs/credentials.json` (or a configured location).
3.  **Git Security (CRITICAL)**:
    *   You MUST add `**/token.json` and `**/credentials.json` to your `.gitignore` (or specific token filenames if different).
    *   These files contain sensitive access keys and should **never** be committed to the repository.
4.  **Dependencies**:
    *   `google-api-python-client`
    *   `google-auth-oauthlib`
    *   `google-auth-httplib2`

## Usage (Python Tool)
The tool is located in `agent_tools.gmail.GmailClient`.

```python
from agent_tools.gmail import GmailClient

# Configuration
CREDENTIALS_PATH = 'runs/CURRENT_RUN/inputs/credentials.json'
TOKEN_PATH = 'runs/CURRENT_RUN/tmp/token.json'  # Can share token file if scopes match, but separate is safer for clear scope management
# Or use specific name:
# TOKEN_PATH = 'runs/CURRENT_RUN/tmp/gmail_token.json'

# Initialize
client = GmailClient(credentials_path=CREDENTIALS_PATH, token_path=TOKEN_PATH)

# Search
query = "from:person@example.com subject:Important"
messages = client.search_messages(query=query, max_results=5)

# Read details
for msg in messages:
    details = client.get_message_details(msg['id'])
    subject = client.extract_header(details, 'Subject')
    body = client.extract_body_text(details)
    print(f"Subject: {subject}\nBody: {body[:200]}...")
```

## Authentication Flow
1.  **First Run**:
    *   The tool checks for a valid `token.json` at `TOKEN_PATH`.
    *   If missing/invalid, it launches a local web server (using `InstalledAppFlow`).
    *   User logs in via browser and grants `gmail.readonly` permission.
2.  **Subsequent Runs**:
    *   The tool uses the stored refresh token to get new access tokens automatically.
    *   If the app is in "Testing" mode, the refresh token expires in 7 days, forcing re-authentication (desired security feature).
