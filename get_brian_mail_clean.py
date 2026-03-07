from pathlib import Path
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphClientConfig, GraphAPIClient
from agent_tools.graph.mail_search import search_messages

def _repo_root() -> Path:
    return Path(__file__).resolve().parent

repo_root = _repo_root()
env = load_graph_env(repo_root)
auth = GraphAuthenticator(repo_root=repo_root, env=env)
client = GraphAPIClient(
    authenticator=auth,
    config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
)

print("Checking 'take action' folder...")
folders = client.get("me/mailFolders", params={"$top": 100})
take_action_id = None
for f in folders.get("value", []):
    if "take action" in f.get("displayName", "").lower():
        take_action_id = f.get("id")
        print(f"Found 'take action' folder, id: {take_action_id}")
        break
        
print("\nRecent emails from Brian Hall:")
msgs = search_messages(client, query='from:"Brian Hall"', top=5)
for m in msgs:
    if take_action_id and m.get('parentFolderId') != take_action_id:
        continue
    print(f"Subject: {m.get('subject')}")
    print(f"Folder: {m.get('parentFolderId')} (take action? {m.get('parentFolderId') == take_action_id})")
    content = m.get('body', {}).get('content', '')[:1500]
    preview = m.get('bodyPreview', '')
    print(f"Body: {content}")
    print("---")
