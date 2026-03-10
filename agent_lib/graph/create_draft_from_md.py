from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.drafts import create_draft_message, create_reply_draft, parse_markdown_email, resolve_email_candidates_from_mailbox
from agent_tools.graph.env import load_graph_env


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an Outlook draft email (Drafts) from a Markdown draft file.")
    parser.add_argument("--md", required=True, help="Path to markdown draft (must contain a 'Subject:' line).")
    parser.add_argument("--to", default="", help="Optional To email(s), comma-separated")
    parser.add_argument("--cc", default="", help="Optional Cc email(s), comma-separated")
    parser.add_argument(
        "--resolve-to-name",
        default="",
        help="If --to is empty, attempt to resolve a recipient address by searching mailbox for this display name.",
    )
    parser.add_argument(
        "--reply-to",
        default="",
        help="Message ID to reply to. If set, --to/--cc/--resolve-to-name are ignored (reply targets sender).",
    )
    args = parser.parse_args(argv)

    repo_root = _repo_root()
    env = load_graph_env(repo_root)
    authenticator = GraphAuthenticator(repo_root=repo_root, env=env)
    client = GraphAPIClient(
        authenticator=authenticator,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )

    md_path = Path(str(args.md)).expanduser().resolve()
    # If replying, we typically ignore the subject line in the draft (replies inherit "Re: Subject").
    # But parse_markdown_email requires it.
    subject, body_text = parse_markdown_email(md_path)

    if args.reply_to:
        print(f"Creating Reply draft to message {args.reply_to}...")
        # For replies, we encourage HTML in the body if possible, but body_text from markdown parser is text.
        # Ideally, we'd render markdown to HTML here, but for now we pass text (which creates wrapped text).
        result = create_reply_draft(client, message_id=args.reply_to, body=body_text, content_type="TEXT")
        print("Created REPLY draft message in Drafts.")
    else:
        to_list = [e.strip() for e in str(args.to).split(",") if e.strip()]
        cc_list = [e.strip() for e in str(args.cc).split(",") if e.strip()]

        if not to_list and args.resolve_to_name:
            candidates = resolve_email_candidates_from_mailbox(client, str(args.resolve_to_name))
            # Prefer unique exact match.
            if len(candidates) == 1:
                to_list = [candidates[0][1]]
            else:
                print("Could not uniquely resolve a To address from name search.")
                if candidates:
                    print("Candidates found (name <email>):")
                    for name, addr in candidates[:10]:
                        print(f"- {name} <{addr}>")
                print("Proceeding without a To recipient (draft will still be created).")

        result = create_draft_message(client, subject=subject, body_text=body_text, to=to_list, cc=cc_list)
        print("Created NEW draft message in Drafts.")
        print(f"Subject: {subject}")
        if to_list:
            print(f"To: {', '.join(to_list)}")
        if cc_list:
            print(f"Cc: {', '.join(cc_list)}")

    print(f"Message id: {result.id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
