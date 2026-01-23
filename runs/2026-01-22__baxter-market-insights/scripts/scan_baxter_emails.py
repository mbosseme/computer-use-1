import collections
from pathlib import Path
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env

def main():
    print("Initializing Graph client...")
    repo_root = Path.cwd()
    env = load_graph_env(repo_root)
    
    auth = GraphAuthenticator(
        repo_root=repo_root, 
        env=env
    )
    
    config = GraphClientConfig(
        base_url=env.base_url,
        scopes=env.scopes,
        planner_timezone="Eastern Standard Time"
    )
    
    client = GraphAPIClient(authenticator=auth, config=config)
    
    # Updated search strategy
    print("Searching for messages with subject 'Baxter'...")
    
    sender_counts = collections.Counter()
    recipient_counts = collections.Counter()
    external_domains = collections.Counter()
    
    url = "me/messages"
    params = {
        "$top": 50,
        "$select": "from,toRecipients,ccRecipients,subject,receivedDateTime",
        "$search": '"subject:Baxter"' 
    }
    
    messages_processed = 0
    max_messages = 100
    
    while url and messages_processed < max_messages:
        result = client.get(url, params=params if "me/messages" in url else None)
        messages = result.get("value", [])
        
        if not messages:
            break
            
        for msg in messages:
            messages_processed += 1
            
            # Helper to process an email address
            def process_addr(addr_obj, count_dict):
                name = addr_obj.get("name", "Unknown")
                email = addr_obj.get("address", "").lower()
                
                # Skip Premier internal emails (heuristic)
                if "premier" in email or "inc.com" in email: 
                    return

                # Record meaningful external contacts
                count_dict[f"{name} ({email})"] += 1
                
                # Record domain
                if "@" in email:
                    domain = email.split("@")[-1]
                    external_domains[domain] += 1

            # Analyze Sender
            sender = msg.get("from", {}).get("emailAddress", {})
            process_addr(sender, sender_counts)
                
            # Analyze Recipients
            for role in ["toRecipients", "ccRecipients"]:
                for r in msg.get(role, []):
                    process_addr(r.get("emailAddress", {}), recipient_counts)

        url = result.get("@odata.nextLink")
        params = None

    print(f"\nAnalyzed {messages_processed} messages.\n")
    
    print("Top External Senders (People emailing us on 'Baxter' threads):")
    for person, count in sender_counts.most_common(10):
        print(f"  {count}x: {person}")
        
    print("\nTop External Recipients (People we are emailing on 'Baxter' threads):")
    for person, count in recipient_counts.most_common(10):
        print(f"  {count}x: {person}")
        
    print("\nTop External Domains found:")
    for domain, count in external_domains.most_common(10):
        print(f"  {count}x: {domain}")


if __name__ == "__main__":
    main()
