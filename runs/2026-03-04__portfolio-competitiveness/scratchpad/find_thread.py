from pathlib import Path
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphClientConfig, GraphAPIClient
import json

def _repo_root() -> Path:
    return Path(__file__).resolve().parent

repo_root = _repo_root()
env = load_graph_env(repo_root)
auth = GraphAuthenticator(repo_root=repo_root, env=env)
client = GraphAPIClient(
    authenticator=auth,
    config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
)

search_phrase = "Healthcare IQ Benchmark Analysis - Beta Workbook"

print(f"Searching for: '{search_phrase}'")
msgs = client.get("me/messages", params={"$search": f'"{search_phrase}"', "$top": 10, "$select": "subject,receivedDateTime,sender,id,hasAttachments", })

if not msgs.get('value'):
    print("Not found via $search, trying $filter...")
    msgs = client.get("me/messages", params={"$filter": f"contains(subject, '{search_phrase}')", "$top": 10, "$select": "subject,receivedDateTime,sender,id,hasAttachments", })

for i, m in enumerate(msgs.get("value", [])):
    sender = m.get('sender', {}).get('emailAddress', {}).get('name', 'Unknown')
    print(f"[{i}] {m.get('subject')} | {sender} | {m.get('receivedDateTime')} | Attachments: {m.get('hasAttachments')} | ID: {m.get('id')}")
