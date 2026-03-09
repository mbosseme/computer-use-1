from pathlib import Path
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphClientConfig, GraphAPIClient
import json
import base64
from bs4 import BeautifulSoup

def _repo_root() -> Path:
    return Path(__file__).resolve().parent

repo_root = _repo_root()
env = load_graph_env(repo_root)
auth = GraphAuthenticator(repo_root=repo_root, env=env)
client = GraphAPIClient(
    authenticator=auth,
    config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
)

msg_id = "AAMkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwBGAAAAAAAlR3BCNHUoR42P4-xIVEVaBwCtC60M6iwCT6oV7C2g6lbxAAAAQ-41AAAmYvJHuYjqQbIghoy3jqM-AAo_aAXHAAA="
attachments = client.get(f"me/messages/{msg_id}/attachments")

atts = attachments.get('value', [])
for i, a in enumerate(atts):
    if a.get('isInline') and a.get('contentType', '').startswith('image/'):
        img_data = base64.b64decode(a.get('contentBytes', ''))
        filename = f"inline_img_{i}.png"
        with open(filename, 'wb') as f:
            f.write(img_data)
        print(f"Saved inline image to {filename}")