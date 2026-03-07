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

folders = client.get("me/mailFolders", params={"$top": 100})
for f in folders.get("value", []):
    print(f"Folder: {f.get('displayName')}, ID: {f.get('id')}")
    # also try to get child folders
    child_folders = client.get(f"me/mailFolders/{f.get('id')}/childFolders", params={"$top": 100})
    for cf in child_folders.get("value", []):
        print(f"  Child Folder: {cf.get('displayName')}, ID: {cf.get('id')}")

