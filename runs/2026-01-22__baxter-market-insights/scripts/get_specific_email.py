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

    print("Fetching specific email from Matthew Bossemeyer to Caroline Gullion...")
    
    # We found a very likely candidate in the previous search
    resp = client.get(
        "me/messages",
        params={
            "$search": '"subject:Next Steps After Demand Planning Pilot"',
            "$select": "subject,receivedDateTime,from,body,toRecipients",
            "$top": 10
        },
        headers={"ConsistencyLevel": "eventual"}
    )
    
    messages = resp.get("value", [])
    print(f"Found {len(messages)} messages.")
    
    target_msg = None
    for msg in messages:
        sender_name = msg.get("from", {}).get("emailAddress", {}).get("name", "")
        print(f"Checking message from: {sender_name} | Date: {msg.get('receivedDateTime')}")
        
        # We are looking for the one from Bossemeyer, Matthew around 2025-12-17
        if "Bossemeyer" in sender_name and "2025-12-17" in msg.get("receivedDateTime", ""):
            target_msg = msg
            break
            
    if target_msg:
        print("\n=== EMAIL FOUND ===")
        print(f"Subject: {target_msg['subject']}")
        print(f"Date: {target_msg['receivedDateTime']}")
        print(f"From: {target_msg.get('from', {}).get('emailAddress', {}).get('name')}")
        
        # Extract plain text or just print body content
        content = target_msg['body']['content']
        print("\n--- BODY CONTENT ---")
        # Simple HTML tag stripping for readability if needed, or just dump it
        import re
        text = re.sub('<[^<]+?>', '', content)
        print(text[:3000])
    else:
        print("Could not find the specific email from Matthew Bossemeyer.")

if __name__ == "__main__":
    main()
