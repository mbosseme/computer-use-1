from pathlib import Path
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphClientConfig, GraphAPIClient
import json

repo_root = Path(__file__).resolve().parent
env = load_graph_env(repo_root)
auth = GraphAuthenticator(repo_root=repo_root, env=env)
client = GraphAPIClient(
    authenticator=auth,
    config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
)

msgs = client.get("me/messages", params={"$top": 10, "$search": '"Joe"'})
for m in msgs.get("value", []):
    print(m.get('subject'))
    print(m.get('bodyPreview'))
    print("--- BODY ---")
    print(m.get('body', {}).get('content', '')[:2000])
    print("====================")
