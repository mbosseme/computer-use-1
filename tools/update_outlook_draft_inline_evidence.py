from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.inline_images import replace_inline_attachments, split_quoted_tail


def _escape_html(text: str) -> str:
    import html

    return html.escape(text)


def _img_block(*, title: str, cid: str, note: str | None = None) -> str:
    note_html = (
        f"<div style=\"margin: 6px 0 0 0; font-size: 10.5pt; color: #6b7280;\">{_escape_html(note)}</div>"
        if note
        else ""
    )
    return (
        "<div style=\"margin: 12px 0 18px 0;\">"
        f"<div style=\"font-weight: 700; margin: 0 0 8px 0;\">{_escape_html(title)}</div>"
        f"<img src=\"cid:{cid}\" style=\"display:block; width: 100%; max-width: 920px; height: auto; border: 1px solid #e5e7eb; border-radius: 6px;\"/>"
        f"{note_html}"
        "</div>"
    )


def _render_default_body_html() -> str:
    """Default template: evidence-led narrative with inline screenshots.

    Customize this in-run if needed; this script is intended as a reliable starting point.
    """

    intro = (
        "<div style=\"font-family: Calibri, sans-serif; font-size: 11pt; color: #111827;\">"
        "Hi,<br><br>"
        "We re-tested the specified dashboard views and captured the exact filter states we validated. "
        "Screenshots are placed inline immediately after the related explanation.<br><br>"
        "</div>"
    )

    sections = "".join(
        [
            "<hr style=\"border:none;border-top:1px solid #e5e7eb;margin:16px 0;\"/>",
            _img_block(title="Evidence 1", cid="evidence1", note="Validated state."),
            _img_block(title="Evidence 2", cid="evidence2", note="Validated state."),
            "<div style=\"margin-top: 8px;\">Best,<br>\n</div>",
        ]
    )

    return intro + sections


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for _ in range(25):
        if (p / "AGENTS.md").exists():
            return p
        if (p.parent / "AGENTS.md").exists():
            return p.parent
        p = p.parent
    raise RuntimeError("Could not locate repo root (AGENTS.md)")


def _read_pairs_json(path: Path) -> List[Tuple[str, str]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, list):
        raise ValueError("Expected a JSON list of {contentId,path} objects")
    out: List[Tuple[str, str]] = []
    for it in obj:
        if not isinstance(it, dict):
            continue
        cid = str(it.get("contentId") or it.get("cid") or "").strip()
        p = str(it.get("path") or "").strip()
        if cid and p:
            out.append((cid, p))
    if not out:
        raise ValueError("No valid {contentId,path} pairs found")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Update an existing Outlook draft with inline evidence images (NOT SENT).")
    ap.add_argument("--draft-id", required=True, help="Graph message id for the draft to update")
    ap.add_argument(
        "--images-json",
        required=True,
        help="JSON list of {contentId, path} entries for inline CID images.",
    )
    ap.add_argument(
        "--body-html",
        default="",
        help="Optional path to an HTML file to use as the new top-of-email body. If omitted, a small template is used.",
    )
    ap.add_argument(
        "--preserve-quoted",
        action="store_true",
        help="Preserve the existing quoted thread by appending it below the new body.",
    )
    ap.add_argument(
        "--out-json",
        default="",
        help="Optional path to write an update summary JSON.",
    )

    args = ap.parse_args()

    repo_root = _repo_root()
    env = load_graph_env(repo_root)
    auth = GraphAuthenticator(repo_root=repo_root, env=env)
    client = GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )

    msg = client.get(f"me/messages/{args.draft_id}", params={"$select": "subject,body"})
    body = msg.get("body") if isinstance(msg, dict) else None
    existing_html = ""
    if isinstance(body, dict) and str(body.get("contentType") or "").lower() == "html":
        existing_html = str(body.get("content") or "")

    quoted_tail = ""
    if args.preserve_quoted and existing_html:
        _, quoted_tail = split_quoted_tail(existing_html)

    if args.body_html:
        new_top = Path(args.body_html).read_text(encoding="utf-8")
    else:
        new_top = _render_default_body_html()

    combined = new_top + (quoted_tail if quoted_tail else "")

    client.patch(
        f"me/messages/{args.draft_id}",
        json={"body": {"contentType": "html", "content": combined}},
    )

    pairs = _read_pairs_json(Path(args.images_json))
    cid_to_path = [(cid, Path(p)) for cid, p in pairs]

    attach_summary = replace_inline_attachments(
        client,
        args.draft_id,
        cid_to_path=cid_to_path,
        delete_if_name_prefixes=("market-share-by-",),
    )

    out: Dict[str, Any] = {
        "note": "Updated existing draft body + inline images (NOT SENT).",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "draftMessageId": args.draft_id,
        "subject": msg.get("subject"),
        "attachments": attach_summary,
    }

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("Updated draft (NOT SENT).")
    print("draft_id:", args.draft_id)


if __name__ == "__main__":
    main()
