#!/usr/bin/env python3
"""
Create a draft reply to Jen's email thread.

This script:
1. Searches for the email thread "Re: Confirmed-BBraun MI Demo - virtual"
2. Finds the latest message from Jen in that thread
3. Creates a reply draft with the IV Solutions sample data email content
"""

from pathlib import Path
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env

REPO_ROOT = Path(__file__).resolve().parents[3]
EXPORTS_DIR = REPO_ROOT / "runs/2026-01-27__fy27-email-handoff/exports"

# Email body content (plain text)
EMAIL_BODY = """Hi Jen,

I wanted to follow up with the sample data extract based on the IV Solutions product list you provided. We've pulled together a comprehensive dataset covering 24 months of purchasing activity (January 2024 through December 2025) for the 71 NDCs you identified.

WHAT WE FOUND

We were able to locate spend for the vast majority of the products on your list:

• Total Spend: $42.7 million across 48,621 transaction records
• Unique Facilities: 3,489 healthcare providers
• Geographic Coverage: All 50 states represented
• Product Coverage: 69 of the 71 products you sent had transactional purchasing activity over the past two years

The spend breaks down as follows:
• ERP (Provider Direct): $39.5M (92.5%) — purchasing data reported directly by healthcare providers
• Wholesaler: $3.2M (7.5%) — distributor/wholesaler reported sales

Only 2 of the 71 NDCs from your original list had no purchasing activity in our database for this time period, which likely indicates those are either newer products or lower-volume items.

ABOUT THE SAMPLE REPRESENTATIVENESS

The underlying sample of hospitals and non-acute care facilities in Premier's database represents approximately 25% of the US acute and non-acute care market. The data includes a diverse mix of facility types, sizes, and geographic locations that is broadly representative of the total US population of healthcare providers.

As a rough guide, you can extrapolate from these sample figures to estimate total US purchasing volume by dividing by 0.25 (or equivalently, multiplying by 4). For example, the $42.7M in this sample would suggest approximately $170M in total US healthcare provider purchasing for these products over the 24-month period.

ATTACHED FILES

I'm attaching two files:

1. iv_solutions__external_sample_enriched.csv — The main data extract containing all transaction-level records. Each row represents a facility/month/product combination with spend amounts and product attributes.

2. iv_solutions__external_sample_enriched_dictionary.md — A data dictionary explaining each column in the extract, including notes on data sources and de-identification.

Key notes on the data:
• Facility identifiers are blinded — We've replaced actual facility IDs with anonymous identifiers (FAC_00001, etc.) and removed facility names, addresses, and IDN affiliations.
• Geographic data retained — State and 3-digit ZIP are included to support regional analysis.
• Product metadata — All product attributes (brand name, description, manufacturer, etc.) are sourced from Premier's Primary Item Master for consistency across data sources.
• Dual data sources — The "source" column indicates whether each row came from ERP (provider direct) or Wholesaler data.

Let me know if you have any questions about the data or need any adjustments to the extract. Happy to discuss the findings or pull additional cuts if helpful for the B. Braun analysis.

Best,
Matt
"""


def main():
    # Initialize Graph client
    env = load_graph_env(REPO_ROOT)
    authenticator = GraphAuthenticator(repo_root=REPO_ROOT, env=env)
    client = GraphAPIClient(
        authenticator=authenticator,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )
    
    # Search for the email thread
    print("Searching for email thread...")
    search_query = '"Confirmed-BBraun MI Demo"'
    
    resp = client.get(
        "me/messages",
        params={
            "$search": search_query,
            "$top": 20,
            "$select": "id,subject,from,receivedDateTime,conversationId",
        },
        headers={"ConsistencyLevel": "eventual"},
    )
    
    messages = resp.get("value", [])
    print(f"Found {len(messages)} messages")
    
    # Find messages from Jen (look for "Jen" in sender name)
    jen_messages = []
    for msg in messages:
        from_info = msg.get("from", {}).get("emailAddress", {})
        sender_name = from_info.get("name", "")
        sender_email = from_info.get("address", "")
        subject = msg.get("subject", "")
        received = msg.get("receivedDateTime", "")
        
        print(f"  - {sender_name} <{sender_email}>: {subject[:50]}... ({received[:10]})")
        
        if "jen" in sender_name.lower() or "jen" in sender_email.lower():
            jen_messages.append(msg)
    
    if not jen_messages:
        print("\nNo messages from Jen found. Listing all senders to help identify:")
        return 1
    
    # Use the most recent message from Jen
    latest_jen = jen_messages[0]
    msg_id = latest_jen["id"]
    conv_id = latest_jen.get("conversationId", "")
    from_info = latest_jen.get("from", {}).get("emailAddress", {})
    jen_email = from_info.get("address", "")
    jen_name = from_info.get("name", "")
    
    print(f"\nReplying to message from: {jen_name} <{jen_email}>")
    print(f"Message ID: {msg_id[:50]}...")
    print(f"Conversation ID: {conv_id[:50]}...")
    
    # Create a reply draft
    # Use POST /me/messages/{id}/createReply to create a reply draft
    print("\nCreating reply draft...")
    reply_resp = client.post(f"me/messages/{msg_id}/createReply", json={}, timeout=60)
    
    draft_id = reply_resp.get("id")
    if not draft_id:
        print("Failed to create reply draft")
        print(reply_resp)
        return 1
    
    print(f"Created reply draft: {draft_id[:50]}...")
    
    # Update the draft with our content
    print("Updating draft content...")
    update_payload = {
        "body": {
            "contentType": "text",
            "content": EMAIL_BODY,
        }
    }
    
    client.request("PATCH", f"me/messages/{draft_id}", json=update_payload, timeout=60)
    
    print("\n" + "="*60)
    print("SUCCESS: Draft reply created in your Outlook Drafts folder")
    print("="*60)
    print(f"To: {jen_email}")
    print(f"Subject: Re: {latest_jen.get('subject', 'Confirmed-BBraun MI Demo - virtual')}")
    print("\nNote: You'll need to manually attach the following files:")
    print(f"  1. {EXPORTS_DIR / 'iv_solutions__external_sample_enriched.csv'}")
    print(f"  2. {EXPORTS_DIR / 'iv_solutions__external_sample_enriched_dictionary.md'}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
