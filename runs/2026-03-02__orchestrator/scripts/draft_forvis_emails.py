"""Create three Outlook draft emails for the Forvis/IRS follow-up actions.

1. Reply-all to Trevor's Feb 27 email (acknowledge + 1-week ETA)
2. Forward Trevor's email to Bethany (scoped ask + keep Trevor's attachment)
3. New email to Sri (FY23 ABI experimentation status check)

Drafts are created but NOT sent.
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


def find_trevor_feb27_message(client: GraphAPIClient) -> dict:
    """Find Trevor Musgrave's Feb 27 reply in the FY25 R&D thread."""
    cid = "AAQkADBjZWQ3N2FjLWNmNWMtNGYzOC05MmM4LWVmNTIxNmE0MDhiMwAQAMS1j4MVE0r4ojtXuSuNewU="
    payload = client.get(
        "me/messages",
        params={
            "$top": 50,
            "$select": "id,subject,from,receivedDateTime,hasAttachments",
            "$filter": f"conversationId eq '{cid}'",
        },
    )
    msgs = payload.get("value", [])
    # Find Trevor's Feb 27 message
    for m in msgs:
        frm = ((m.get("from") or {}).get("emailAddress") or {})
        addr = (frm.get("address") or "").lower()
        dt = m.get("receivedDateTime") or ""
        if "trevor" in addr and dt.startswith("2026-02-27"):
            return m
    raise RuntimeError("Could not find Trevor's Feb 27 message in thread")


def draft_reply_to_trevor(client: GraphAPIClient, message_id: str) -> str:
    """Draft 1: Reply-all to Trevor — acknowledge + 1-week ETA."""

    body_text = (
        "Trevor,\n\n"
        "Thank you for the quick review and feedback — glad to hear the Epics and features "
        "documentation is on the right track.\n\n"
        "We'll pull together a sample of the supporting development artifacts "
        "(ADO exports, commit history, etc.) per your guidance and the example Beth Rutter "
        "provided. Plan to have these over to you by end of day Monday, March 9.\n\n"
        "Please don't hesitate to reach out if anything else comes up in the meantime.\n\n"
        "Best,\nMatt"
    )

    # 1. createReplyAll to preserve all To/Cc
    reply_resp = client.post(
        f"me/messages/{message_id}/createReplyAll",
        json={},
        timeout=60,
    )
    draft_id = reply_resp.get("id", "")
    if not draft_id:
        raise RuntimeError("createReplyAll returned no draft id")

    # 2. Get current quoted body
    current = client.get(f"me/messages/{draft_id}", timeout=30)
    current_body = (current.get("body") or {}).get("content", "")

    # 3. Prepend new content
    new_html = "<html><body>" + html.escape(body_text).replace("\n", "<br>") + "</body></html>"
    separator = '<br><div class="BodyFragment"><hr></div>'
    full_body = f"{new_html}{separator}{current_body}"

    client.patch(
        f"me/messages/{draft_id}",
        json={"body": {"contentType": "HTML", "content": full_body}},
        timeout=30,
    )

    return draft_id


def draft_forward_to_bethany(client: GraphAPIClient, message_id: str) -> str:
    """Draft 2: Forward Trevor's email to Bethany with scoped ask.

    Uses createForward which preserves attachments from the original message.
    """

    body_text = (
        "Hey Bethany,\n\n"
        "Forwarding Trevor's latest reply below. The good news: our Epics/features documentation "
        "was exactly what they needed. The next ask is a sample of supporting development artifacts "
        "for FY25 — things like ADO exports, pull request history, spike descriptions, or screenshots "
        "from Azure DevOps.\n\n"
        "Trevor attached an example export that Beth Rutter previously provided for a different project "
        "(should be attached to this forward) — that's the level/format of detail they're looking for.\n\n"
        "This does NOT need to be exhaustive. A representative sample tied to the Epics we already "
        "submitted is sufficient. If someone on your team (or you) could pull a few relevant ADO exports "
        "or screenshots together, that would be perfect. Happy to discuss if it's easier to walk through "
        "what they're after.\n\n"
        "Targeting end of day Monday, March 9 to get this back to Forvis.\n\n"
        "Thanks!\nMatt"
    )

    # createForward preserves original attachments
    fwd_resp = client.post(
        f"me/messages/{message_id}/createForward",
        json={},
        timeout=60,
    )
    draft_id = fwd_resp.get("id", "")
    if not draft_id:
        raise RuntimeError("createForward returned no draft id")

    # Patch in recipients + body
    new_html = "<html><body>" + html.escape(body_text).replace("\n", "<br>") + "</body></html>"

    current = client.get(f"me/messages/{draft_id}", timeout=30)
    current_body = (current.get("body") or {}).get("content", "")
    separator = '<br><div class="BodyFragment"><hr></div>'
    full_body = f"{new_html}{separator}{current_body}"

    client.patch(
        f"me/messages/{draft_id}",
        json={
            "toRecipients": [
                {"emailAddress": {"address": "Bethany_Downs@PremierInc.com"}},
            ],
            "ccRecipients": [
                {"emailAddress": {"address": "Scott_McCleary@PremierInc.com"}},
            ],
            "body": {"contentType": "HTML", "content": full_body},
        },
        timeout=30,
    )

    return draft_id


def draft_email_to_sri(client: GraphAPIClient) -> str:
    """Draft 3: New email to Sri checking on FY23 ABI experimentation artifacts."""

    body_text = (
        "Hey Sri,\n\n"
        "Quick check-in on the ABI Platform experimentation artifact request that Zach Nutter "
        "(Forvis) sent over back on January 28 — the FY2023 (7/1/2022–6/30/2023) IRS audit "
        "documentation.\n\n"
        "Were you able to get the requested materials submitted to the Forvis portal? "
        "I know the original deadline was 2/2 and there was a meeting proposed for 2/4–2/5 — just want "
        "to make sure this got handled and there's nothing still outstanding on our side.\n\n"
        "Let me know if there's anything I can help with.\n\n"
        "Thanks,\nMatt"
    )

    payload = {
        "subject": "FY23 ABI Experimentation Artifacts — Status Check (IRS Audit / Forvis)",
        "body": {"contentType": "text", "content": body_text},
        "toRecipients": [
            {"emailAddress": {"address": "Srikanth_Ramayanam@PremierInc.com"}},
        ],
    }

    created = client.post("me/messages", json=payload, timeout=60)
    draft_id = created.get("id", "")
    if not draft_id:
        raise RuntimeError("Graph returned no draft id for new message")

    return draft_id


def main():
    client = build_client()

    # Step 1: Find Trevor's Feb 27 message
    print("Finding Trevor's Feb 27 message...")
    trevor_msg = find_trevor_feb27_message(client)
    trevor_id = trevor_msg["id"]
    has_att = trevor_msg.get("hasAttachments", False)
    print(f"  Found: {trevor_msg.get('subject', '?')}")
    print(f"  ID: {trevor_id}")
    print(f"  hasAttachments: {has_att}")

    # Step 2: Draft reply-all to Trevor
    print("\nDraft 1: Reply-all to Trevor (acknowledge + 1-week ETA)...")
    reply_id = draft_reply_to_trevor(client, trevor_id)
    print(f"  CREATED — draft ID: {reply_id}")

    # Step 3: Draft forward to Bethany
    print("\nDraft 2: Forward to Bethany (scoped ask + attachment)...")
    fwd_id = draft_forward_to_bethany(client, trevor_id)
    print(f"  CREATED — draft ID: {fwd_id}")

    # Step 4: Draft email to Sri
    print("\nDraft 3: New email to Sri (FY23 ABI status check)...")
    sri_id = draft_email_to_sri(client)
    print(f"  CREATED — draft ID: {sri_id}")

    print("\n" + "=" * 60)
    print("ALL THREE DRAFTS CREATED IN OUTLOOK DRAFTS FOLDER")
    print("Review in Outlook before sending.")
    print("=" * 60)


if __name__ == "__main__":
    main()
