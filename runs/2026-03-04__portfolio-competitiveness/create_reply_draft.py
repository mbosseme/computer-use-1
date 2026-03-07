"""Create a reply-all draft to Brian's latest message in the HCIQ thread."""
from __future__ import annotations
import sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.drafts import create_reply_all_draft, parse_markdown_email

env = load_graph_env(ROOT)
auth = GraphAuthenticator(repo_root=ROOT, env=env)
client = GraphAPIClient(
    authenticator=auth,
    config=GraphClientConfig(
        base_url=env.base_url,
        scopes=env.scopes,
        planner_timezone=env.planner_timezone,
    ),
)

# Brian's latest reply in the thread (from find_thread.py output)
BRIAN_MSG_ID = "AAMkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwBGAAAAAAAlR3BCNHUoR42P4-xIVEVaBwAmYvJHuYjqQbIghoy3jqM-AAejyLKGAAAmYvJHuYjqQbIghoy3jqM-AAosmKP7AAA="

# Delete the errant draft that replied to the wrong thread
ERRANT_DRAFT_ID = "AAMkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwBGAAAAAAAlR3BCNHUoR42P4-xIVEVaBwCtC60M6iwCT6oV7C2g6lbxAAAAQ-5AAAAmYvJHuYjqQbIghoy3jqM-AAo2mxtFAAA="
try:
    client.request("DELETE", f"me/messages/{ERRANT_DRAFT_ID}", timeout=30)
    print("Deleted errant draft from wrong thread.")
except Exception as e:
    print(f"Could not delete errant draft (may already be gone): {e}")

# Read and convert the markdown draft to HTML 
md_path = ROOT / "runs" / "2026-03-04__portfolio-competitiveness" / "draft_email_to_brian.md"
_, body_text = parse_markdown_email(md_path)

# Convert markdown body to HTML for nicer formatting
try:
    from markdown_it import MarkdownIt
    md_source = md_path.read_text()
    # Strip subject line
    lines = md_source.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("subject:"):
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            md_body = "\n".join(lines[j:])
            break
    else:
        md_body = md_source

    md_parser = MarkdownIt("commonmark", {"html": True}).enable("table")
    body_html = md_parser.render(md_body)
except Exception:
    # fallback: wrap plain text in pre tags
    import html as html_mod
    body_html = f"<pre style='font-family: Calibri, sans-serif; white-space: pre-wrap;'>{html_mod.escape(body_text)}</pre>"

# 3. Create reply-all draft
print("\nCreating reply-all draft to Brian's message...")
result = create_reply_all_draft(
    client,
    message_id=BRIAN_MSG_ID,
    body=body_html,
    content_type="HTML",
)
print(f"Draft created successfully!")
print(f"Draft message ID: {result.id}")
print("Check your Drafts folder in Outlook.")
