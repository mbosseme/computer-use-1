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

    # Search for emails involving "Caroline" and "January" or "check back"
    # MS Graph $search syntax is powerful.
    # We'll look for "Caroline" in participants and keywords in body/subject.
    
    # Strategy 1: Search for "Caroline" and "January" in the same query
    # Minimal quoting for KQL.
    query = 'Caroline AND January'
    print(f"Searching for: {query}")
    
    # We need to search specifically in messages
    
    resp = client.get(
        "me/messages",
        params={
            "$search": f'"{query}"', # Enclose the whole KQL phrase in quotes for the param value
            "$select": "subject,receivedDateTime,from,toRecipients,bodyPreview,conversationId",
            "$top": 20
        },
        headers={"ConsistencyLevel": "eventual"}
    )
    
    messages = resp.get("value", [])
    print(f"Found {len(messages)} messages matching '{query}'.\n")
    
    for msg in messages:
        subject = msg.get("subject", "No Subject")
        date = msg.get("receivedDateTime", "")
        sender = msg.get("from", {}).get("emailAddress", {}).get("name", "Unknown")
        preview = msg.get("bodyPreview", "").replace("\n", " ")
        print(f"Date: {date}")
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Preview: {preview[:200]}...")
        print("-" * 50)

    # Strategy 2: If the above is too broad or empty, specific text search
    if not messages:
        print("Broad search empty. Trying specific phrase 'check back'...")
        query = '"Caroline" AND "check back"'
        resp = client.get(
            "me/messages",
            params={
                "$search": f'"{query}"',
                "$top": 20
            }
        )
        messages = resp.get("value", [])
        for msg in messages:
            print(f"Subject: {msg.get('subject')} | From: {msg.get('from', {}).get('emailAddress', {}).get('name')}")

if __name__ == "__main__":
    main()
