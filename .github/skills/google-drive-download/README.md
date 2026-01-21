# Skill: Google Drive File Download

## Description
This skill allows the agent to download files from Google Drive, including exporting Google Sheets to Excel. It handles OAuth 2.0 authentication via a local server flow (Human-in-the-Loop) and supports persistent token storage to minimize login prompts.

## Prerequisites
1.  **Google Cloud Project**: A project with the Google Drive API enabled.
    *   **Configuration**: To ensure tokens expire automatically after 7 days (security best practice), set the **OAuth Consent Screen** > **Publishing Status** to **Testing**.
2.  **Credentials**: An OAuth 2.0 Client ID `credentials.json` file.
    *   Download from Google Cloud Console -> APIs & Services -> Credentials -> Create Credentials -> OAuth Client ID (Desktop App).
    *   Place this file in `runs/<RUN_ID>/inputs/credentials.json` (or a configured location).
3.  **Git Security (CRITICAL)**:
    *   You MUST add `**/token.json` and `**/credentials.json` to your `.gitignore`.
    *   These files contain sensitive access keys and should **never** be committed to the repository, even during run logging.
4.  **Dependencies**:
    *   `google-api-python-client`
    *   `google-auth-oauthlib`
    *   `google-auth-httplib2`

## Usage (Python Tool)
The tool is located in `agent_tools.google_drive.GoogleDriveClient`.

```python
from agent_tools.google_drive import GoogleDriveClient

# Configuration
CREDENTIALS_PATH = 'runs/CURRENT_RUN/inputs/credentials.json'
TOKEN_PATH = 'runs/CURRENT_RUN/tmp/token.json'
FILE_ID = 'your-file-id-here'
OUTPUT_PATH = 'runs/CURRENT_RUN/downloads/MyFile.xlsx'

# Initialize
client = GoogleDriveClient(CREDENTIALS_PATH, TOKEN_PATH)

# Download Google Sheet as Excel
# MimeType for Excel: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
client.download_file(
    file_id=FILE_ID, 
    output_path=OUTPUT_PATH, 
    mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# Download Binary File (PDF, Image, etc.) - Omit mime_type
# client.download_file(file_id='binary-file-id', output_path='path/to/save.pdf')
```

## Authentication Flow (Detail)
1.  **First Run**:
    *   The tool checks for a valid `token.json` at `TOKEN_PATH`.
    *   If missing/invalid, it launches a local web server (using `InstalledAppFlow`).
    *   It prints "Initiating OAuth 2.0 flow..." (or similar) to stdout.
    *   The agent should inform the user to check their browser or use the `open_simple_browser` tool if a URL is provided (though typically it opens the system browser automatically).
    *   **User Action**: The user must log in to their Google account and authorize the app.
    *   Once authorized, the token is saved to `TOKEN_PATH`.
2.  **Subsequent Runs**:
    *   The tool loads credentials from `TOKEN_PATH`.
    *   It refreshes the token automatically if expired.
    *   No user interaction is required unless the refresh token is revoked or expired.

## Common MIME Types
- **Google Sheets**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (Excel)
- **Google Docs**: `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (Word)
- **Google Slides**: `application/vnd.openxmlformats-officedocument.presentationml.presentation` (PowerPoint)
- **PDF**: `application/pdf`

## Recovery Rules
- **Error: "Credentials file not found"**: Verify `credentials.json` is at the expected path. Ask the user to provide it if missing.
- **Error: Auth Failure / Token Error**: Delete the `token.json` file and re-run to trigger a fresh login flow.
- **Error: "File not found"**: Verify the `FILE_ID` is correct and the user account has permission to view it.
