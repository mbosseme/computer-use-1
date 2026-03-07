from agent_tools.graph.client import GraphAPIClient
from agent_tools.graph.mail_search import search_messages, export_thread_markdown
from pathlib import Path

client = GraphAPIClient()
msgs = search_messages(client, query='from:"Brian Hall"', top=5)
for m in msgs:
    print(f"Subject: {m.get('subject')}")
    print(f"Folder: {m.get('parentFolderId')} (need to figure out name)")
    print(m.get('bodyPreview'))
    print("---")
    
