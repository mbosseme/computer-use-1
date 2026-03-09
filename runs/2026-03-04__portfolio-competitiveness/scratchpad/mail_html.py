from pathlib import Path
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphClientConfig, GraphAPIClient
from bs4 import BeautifulSoup

repo_root = Path(__file__).resolve().parent
env = load_graph_env(repo_root)
auth = GraphAuthenticator(repo_root=repo_root, env=env)
client = GraphAPIClient(
    authenticator=auth,
    config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
)

msg_id = "AAMkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwBGAAAAAAAlR3BCNHUoR42P4-xIVEVaBwCtC60M6iwCT6oV7C2g6lbxAAAAQ-41AAAmYvJHuYjqQbIghoy3jqM-AAo_aAXHAAA="
msg = client.get(f"me/messages/{msg_id}", params={"$select": "subject,body"})
html_content = msg.get("body", {}).get("content", "")

soup = BeautifulSoup(html_content, "html.parser")
for i, img in enumerate(soup.find_all("img")):
    print(f"\n--- Image {i} ---")
    alt = img.get("alt")
    if alt: print(f"Alt text: {alt}")
    title = img.get("title")
    if title: print(f"Title: {title}")
    
    # Try finding wrapping text
    parent = img.parent
    if parent:
        print(f"Parent tag: {parent.name}")
        parent_text = parent.get_text(strip=True)
        if parent_text: print(f"Parent text: {parent_text}")
    
    prev = img.find_previous_sibling()
    if prev:
        prev_text = prev.get_text(strip=True)
        if prev_text: print(f"Previous inline text: {prev_text}")
