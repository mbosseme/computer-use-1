"""Replace the standalone Sri email with a forward of the actual ABI thread.

1. Delete the existing standalone draft
2. Forward the original ABI thread message to Sri (preserves full context)
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env


def build_client() -> GraphAPIClient:
    env = load_graph_env(REPO_ROOT)
    auth = GraphAuthenticator(repo_root=REPO_ROOT, env=env)
    return GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(
            base_url=env.base_url,
            scopes=env.scopes,
            planner_timezone=env.planner_timezone,
        ),
    )


def main():
    client = build_client()

    # 1. Delete the existing standalone draft
    old_draft_id = (
        "AAMkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwBGAAAAAAAlR3BCNHUoR42P4-xIVEVa"
        "BwCtC60M6iwCT6oV7C2g6lbxAAAAQ-5AAAAmYvJHuYjqQbIghoy3jqM-AAoioR6fAAA="
    )
    print("Deleting old standalone draft...")
    try:
        client.request("DELETE", f"me/messages/{old_draft_id}")
        print("  Deleted.")
    except Exception as e:
        print(f"  Could not delete (may already be sent/deleted): {e}")

    # 2. Find the ABI thread message (Sri's Jan 28 forward)
    cid = "AAQkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwAQANdAsj-WkhdFgJHdMJx92R0="
    print("\nFinding ABI thread message...")
    payload = client.get(
        "me/messages",
        params={
            "$top": 10,
            "$select": "id,subject,from,receivedDateTime,hasAttachments",
            "$filter": f"conversationId eq '{cid}'",
        },
    )
    msgs = payload.get("value", [])
    if not msgs:
        raise RuntimeError("Could not find ABI thread message")

    abi_msg = msgs[0]
    abi_msg_id = abi_msg["id"]
    print(f"  Found: {abi_msg.get('subject', '?')}")
    print(f"  From: {((abi_msg.get('from') or {}).get('emailAddress') or {}).get('name', '?')}")
    print(f"  Date: {abi_msg.get('receivedDateTime', '?')}")

    # 3. Create forward of the ABI thread message
    body_text = (
        "Hey Sri,\n\n"
        "Quick check-in on this one. Were you able to get the FY2023 ABI experimentation "
        "artifacts submitted to the Forvis portal? I know the original ask from Zach had a "
        "2/2 deadline and a meeting proposed for 2/4\u20132/5 \u2014 just want to make sure this "
        "got handled and there\u2019s nothing still outstanding on our side.\n\n"
        "Let me know if there\u2019s anything I can help with.\n\n"
        "Thanks,\nMatt"
    )

    print("\nCreating forward draft to Sri...")
    fwd_resp = client.post(
        f"me/messages/{abi_msg_id}/createForward",
        json={},
        timeout=60,
    )
    draft_id = fwd_resp.get("id", "")
    if not draft_id:
        raise RuntimeError("createForward returned no draft id")

    # Patch in recipient + body above the forwarded content
    new_html = "<html><body>" + html.escape(body_text).replace("\n", "<br>") + "</body></html>"
    current = client.get(f"me/messages/{draft_id}", timeout=30)
    current_body = (current.get("body") or {}).get("content", "")
    separator = '<br><div class="BodyFragment"><hr></div>'
    full_body = f"{new_html}{separator}{current_body}"

    client.patch(
        f"me/messages/{draft_id}",
        json={
            "toRecipients": [
                {"emailAddress": {"address": "Srikanth_Ramayanam@PremierInc.com"}},
            ],
            "body": {"contentType": "HTML", "content": full_body},
        },
        timeout=30,
    )

    print(f"  CREATED — draft ID: {draft_id}")
    print("\n" + "=" * 60)
    print("FORWARD DRAFT TO SRI CREATED IN OUTLOOK DRAFTS FOLDER")
    print("Full ABI thread context is included below your message.")
    print("Review in Outlook before sending.")
    print("=" * 60)


if __name__ == "__main__":
    main()
