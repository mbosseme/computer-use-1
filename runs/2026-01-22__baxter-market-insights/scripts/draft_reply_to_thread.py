import json
from pathlib import Path
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig

def main():
    repo_root = Path.cwd()
    env = load_graph_env(repo_root)
    auth = GraphAuthenticator(repo_root=repo_root, env=env)
    
    config = GraphClientConfig(
        base_url=env.base_url,
        scopes=env.scopes,
        planner_timezone=env.planner_timezone
    )
    client = GraphAPIClient(authenticator=auth, config=config)

    print("Locating thread...")
    # Find the message from Matthew Bossemeyer around Dec 17 with the specific subject
    # Subject: Re: [ EXTERNAL ] Re: Next Steps After Demand Planning Pilot
    resp = client.get(
        "me/messages",
        params={
            "$search": '"subject:Next Steps After Demand Planning Pilot"',
            "$select": "id,subject,receivedDateTime,from,bodyPreview",
            "$top": 20
        },
        headers={"ConsistencyLevel": "eventual"}
    )
    
    messages = resp.get("value", [])
    target_msg = None
    
    # Look for the last message in the relevant exchange (The one from Matthew to Caroline)
    for msg in messages:
        sender = msg.get("from", {}).get("emailAddress", {}).get("name", "")
        # Verify it's the right thread
        if "Bossemeyer" in sender and "2025-12-17" in msg.get("receivedDateTime", ""):
            print(f"Found target message: {msg['subject']} ({msg['id']})")
            target_msg = msg
            break
            
    if not target_msg:
        print("Could not find the target message to reply to.")
        return

    # Load the draft content
    md_path = repo_root / "runs/2026-01-22__baxter-market-insights/exports/caroline_followup_final.md"
    content = md_path.read_text(encoding="utf-8")
    
    # Parse out the body (skip Subject line)
    lines = content.splitlines()
    body_lines = []
    for line in lines:
        if line.lower().startswith("subject:"):
            continue
        body_lines.append(line)
        
    plain_body = "\n".join(body_lines).strip()
    
    # improved formatting: 
    # The 'comment' parameter in createReply creates a simple body.
    # To ensure good formatting, we will CreateReply (to get a draft) then Patch it.
    
    print("Creating draft reply...")
    # POST /me/messages/{id}/createReply
    # Use empty json to just generate the draft object with correct recipients/subject/parentage
    reply_resp = client.post(f"me/messages/{target_msg['id']}/createReply", json={})
    
    if not reply_resp or "id" not in reply_resp:
        # Sometimes createReply returns nothing (202 Accepted) if just checking? 
        # No, it returns the draft message.
        print("Draft reply creation didn't return an ID. Trying with a placeholder comment.")
        reply_resp = client.post(f"me/messages/{target_msg['id']}/createReply", json={"comment": "..."})
        
    draft_id = reply_resp.get("id")
    print(f"Draft created with ID: {draft_id}")
    
    # Now PATCH the body with our content
    # We want to preserve the thread history usually, but PATCHing 'body' might overwrite it 
    # unless we are careful.
    # Actually, when you createReply, the body of the new message is usually pre-populated with the history if you retrieve it?
    # No, Graph doesn't auto-append history in the 'body' property of the returned draft immediately in all cases 
    # or it does but if we overwrite 'body', we lose it.
    
    # However, the user asked to "draft it as a message in the latest thread".
    # Standard Graph API createReply adds the history to the draft it creates.
    # If we want to INSERT our text at the top, we should probably read the draft's current body, then prepend ours.
    
    # 1. Get the draft details (body)
    draft = client.get(f"me/messages/{draft_id}", params={"$select": "body"})
    current_body_content = draft.get("body", {}).get("content", "")
    
    # 2. Prepend our content
    # Convert our plain text to basic HTML div
    new_html = f"<div>{plain_body.replace(chr(10), '<br>')}</div><br><br>"
    
    combined_body = new_html + current_body_content
    
    # 3. Patch
    print("Updating draft body...")
    client.patch(
        f"me/messages/{draft_id}",
        json={
            "body": {
                "contentType": "html",
                "content": combined_body
            }
        }
    )
    
    print(f"Success! Reply draft updated in thread. Draft ID: {draft_id}")

if __name__ == "__main__":
    main()
