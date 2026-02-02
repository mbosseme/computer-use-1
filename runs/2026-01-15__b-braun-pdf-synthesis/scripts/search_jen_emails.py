#!/usr/bin/env python3
"""Search Outlook for Jennifer Gotto emails with product/NDC information."""

from pathlib import Path
import json

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main():
    # Load environment and create client
    repo_root = _repo_root()
    env = load_graph_env(repo_root)
    authenticator = GraphAuthenticator(repo_root=repo_root, env=env)
    config = GraphClientConfig(
        base_url=env.base_url,
        scopes=env.scopes,
    )
    client = GraphAPIClient(authenticator=authenticator, config=config)

    # Search for emails from Jennifer Gotto
    print("Searching for emails from Jennifer Gotto...")
    try:
        data = client.get(
            'me/messages',
            params={
                '$search': '"jennifer.gotto@bbraunusa.com"',
                '$top': 25,
                '$select': 'id,subject,receivedDateTime,from,body'
            },
            headers={'ConsistencyLevel': 'eventual'}
        )
        
        messages = data.get('value', [])
        print(f'Found {len(messages)} messages')
        
        # Find the Jan 23 email with SKU list
        for msg in messages:
            subj = msg.get('subject', '')
            date_str = msg.get('receivedDateTime', '')
            if '2026-01-23' in date_str and 'Confirmed-BBraun' in subj:
                sender = msg.get('from', {}).get('emailAddress', {}).get('address', 'unknown')
                if 'bbraunusa' in sender:
                    print("=" * 80)
                    print(f"Date: {date_str}")
                    print(f"Subject: {subj}")
                    print(f"From: {sender}")
                    print("=" * 80)
                    body = msg.get('body', {}).get('content', '')
                    print(body)
                    print("=" * 80)
                    
                    # Save the body to a file
                    out_path = Path(__file__).parent.parent / 'tmp' / 'jen_email_sku_list.html'
                    out_path.write_text(body, encoding='utf-8')
                    print(f"\nSaved email body to: {out_path}")
                    break
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
