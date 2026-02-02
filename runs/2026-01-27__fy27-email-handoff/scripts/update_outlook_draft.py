import sys
import os
from pathlib import Path

# Add the root directory to path so we can import agent_tools
REPO_ROOT = Path("/Users/matt_bossemeyer/Projects/wt-2026-01-15__b-braun-pdf-synthesis")
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env

def get_graph_client():
    env = load_graph_env(REPO_ROOT)
    authenticator = GraphAuthenticator(repo_root=REPO_ROOT, env=env)
    client = GraphAPIClient(
        authenticator=authenticator,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )
    return client


def find_draft_by_subject(client, subject_query):
    # Search in Drafts folder
    # Note: 'messages' endpoint creates drafts in Drafts folder by default if not specified? 
    # Or typically drafts are in 'me/mailFolders/drafts/messages'
    
    # Let's try listing messages in the Drafts folder
    # We can filter by subject
    
    params = {
        "$filter": f"contains(subject, '{subject_query}')",
        "$top": 10,
        "$select": "id,subject,bodyPreview"
    }
    
    print(f"Searching for drafts with subject containing: '{subject_query}'")
    
    # Endpoint for drafts
    path = "me/mailFolders/drafts/messages"
    
    response = client.get(path, params=params)
    
    messages = response.get('value', [])
    return messages

def update_draft(client, message_id, new_body):
    path = f"me/messages/{message_id}"
    
    payload = {
        "body": {
            "contentType": "text", 
            "content": new_body
        }
    }
    
    print(f"Updating draft {message_id}...")
    client.patch(path, json=payload)
    print("Draft updated successfully.")

def main():
    try:
        client = get_graph_client()
    except Exception as e:
        print(f"Failed to get graph client: {e}")
        return

    subject_query = "Re: Confirmed-BBraun MI Demo - virtual"
    drafts = find_draft_by_subject(client, subject_query)
    
    if not drafts:
        print("No matching drafts found.")
        # Fallback: list all drafts to see what's there
        print("Listing all drafts to debug...")
        all_drafts = client.get("me/mailFolders/drafts/messages", params={"$top": 10, "$select": "id,subject"}).get('value', [])
        for d in all_drafts:
            print(f" - {d['subject']} (ID: {d['id']})")
        return

    target_draft = drafts[0]
    print(f"Found draft: {target_draft['subject']} (ID: {target_draft['id']})")
    
    # Read the new content
    email_md_path = "runs/2026-01-27__fy27-email-handoff/exports/email_draft_to_jen.md"
    try:
        with open(email_md_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Could not find email draft file: {email_md_path}")
        return

    # Parse the markdown to get body (we ignore subject from file as we are updating an existing thread)
    # The file has headers, we should strip them or parse them.
    # Let's use the parse_markdown_email from drafts.py if possible, or just parse manually here
    # since we want to be safe.
    
    # The file content starts with:
    # # Email to Jen ...
    # **To:** ...
    # **Subject:** ...
    # ---
    # Hi Jen, ...
    
    # We want everything after "Hi Jen," roughly. Or rather, the whole body.
    # Let's clean it up to be plain text suitable for email body.
    
    # Simple parsing:
    lines = content.split('\n')
    body_start_index = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            body_start_index = i + 1
            break
    
    body_text = "\n".join(lines[body_start_index:]).strip()
    
    # Convert markdown to something resembling text/plain or simplistic usage
    # The existing tool uses strip_markdown_to_text. Let's do similar or just pass it 
    # If we pass "contentType": "text", it treats it as plain text. Outlook might render markdown poorly if we don't converting headers etc.
    # The user asked to "make the updates to the real draft".
    # I'll try to do a light cleaning to remove the markdown headers (#)
    
    import re
    # Remove #, ##
    body_text = re.sub(r'^#+\s*', '', body_text, flags=re.MULTILINE)
    # Remove ** around Subject/To if they persisted, but we skipped them.
    # Bold markers **text** -> text
    body_text = body_text.replace("**", "")
    
    update_draft(client, target_draft['id'], body_text)

if __name__ == "__main__":
    main()
