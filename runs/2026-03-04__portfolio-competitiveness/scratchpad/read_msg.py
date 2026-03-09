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

msg = client.get(f"me/messages/{msg_id}", params={"$select": "subject,body,sender,from,toRecipients,ccRecipients"})

# Also fetch attachments (which includes inline images)
attachments = client.get(f"me/messages/{msg_id}/attachments")

print(f"Subject: {msg.get('subject')}")
print(f"From: {msg.get('sender', {}).get('emailAddress', {}).get('name')}")
print("---")
html_content = msg.get('body', {}).get('content', '')

# clean up html
soup = BeautifulSoup(html_content, "html.parser")
print(soup.get_text()[:1500])
print("...")

atts = attachments.get('value', [])
print(f"--- Attachments/Inline Images ({len(atts)}) ---")
has_img = False
for a in atts:
    print(f"Name: {a.get('name')} | Content-Type: {a.get('contentType')} | IsInline: {a.get('isInline')}")
    if a.get('isInline') and a.get('contentType', '').startswith('image/'):
        has_img = True
        img_data = base64.b64decode(a.get('contentBytes', ''))
        with open('inline_img.png', 'wb') as f:
            f.write(img_data)
        print("Saved inline image to inline_img.png")

if not has_img:
    print("WARNING: No inline image found in this specific message. Let's look at the previous one.")