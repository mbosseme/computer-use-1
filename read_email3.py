from pathlib import Path
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphClientConfig, GraphAPIClient

def _repo_root() -> Path:
    return Path(__file__).resolve().parent

repo_root = _repo_root()
env = load_graph_env(repo_root)
auth = GraphAuthenticator(repo_root=repo_root, env=env)
client = GraphAPIClient(
    authenticator=auth,
    config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
)

take_action_id = "AAMkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwAuAAAAAAAlR3BCNHUoR42P4-xIVEVaAQAmYvJHuYjqQbIghoy3jqM-AAejyLKGAAA="

print(f"\nRecent emails in 'take action' folder:")
msgs = client.get(f"me/mailFolders/{take_action_id}/messages", params={"$top": 10, "$orderby": "receivedDateTime desc", "Prefer": 'outlook.body-content-type="text"'}, headers={"Prefer": 'outlook.body-content-type="text"'})
for m in msgs.get("value", []):
    if "Healthcare IQ Benchmark Analysis" in m.get('subject', ''):
        print(f"Subject: {m.get('subject')}")
        content = m.get('body', {}).get('content', '')
        print(f"Body: {content}")
        print("---")
