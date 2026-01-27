from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def _repo_root() -> Path:
    # runs/<RUN_ID>/scripts/<this_file>
    return Path(__file__).resolve().parents[3]


_REPO_ROOT = _repo_root()
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator  # noqa: E402
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig  # noqa: E402
from agent_tools.graph.env import load_graph_env  # noqa: E402


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _strip_md_to_text(text: str) -> str:
    # Minimal markdown-to-plain-text cleanup (keep bullets/numbering).
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    text = text.replace("**", "")
    return text


def _iter_graph_paged(client: GraphAPIClient, path: str, *, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Iterable[Dict[str, Any]]:
    next_url: Optional[str] = path
    next_params: Optional[Dict[str, Any]] = params

    while next_url:
        resp = client.get(next_url, params=next_params, headers=headers, timeout=90)
        items = resp.get("value") if isinstance(resp, dict) else None
        if isinstance(items, list):
            for it in items:
                if isinstance(it, dict):
                    yield it

        next_link = resp.get("@odata.nextLink") if isinstance(resp, dict) else None
        next_url = str(next_link) if next_link else None
        next_params = None


def _parse_subject_and_body(md_path: Path) -> Tuple[str, str]:
    raw = md_path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    subject: Optional[str] = None
    body_lines: List[str] = []

    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("subject:"):
            subject = ln.split(":", 1)[1].strip()
            # body starts after the next blank line
            j = i + 1
            while j < len(lines) and lines[j].strip() != "":
                j += 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            body_lines = lines[j:]
            break

    if not subject:
        raise SystemExit(f"Could not find Subject: line in {md_path}")

    body_text = _strip_md_to_text("\n".join(body_lines)).strip() + "\n"
    return subject, body_text


def _emails_from_recipients(recipients: Any) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    if not isinstance(recipients, list):
        return out
    for r in recipients:
        if not isinstance(r, dict):
            continue
        ea = r.get("emailAddress")
        if not isinstance(ea, dict):
            continue
        name = str(ea.get("name") or "").strip()
        addr = str(ea.get("address") or "").strip()
        if addr:
            out.append((name, addr))
    return out


def _resolve_email_from_name(client: GraphAPIClient, display_name: str) -> List[Tuple[str, str]]:
    # Best-effort: search mailbox for the display name and extract any matching addresses.
    headers = {"ConsistencyLevel": "eventual"}
    query = f'"{display_name}"'

    seen: Dict[str, Tuple[str, str]] = {}
    for msg in _iter_graph_paged(
        client,
        "me/messages",
        params={
            "$search": query,
            "$top": 25,
            "$select": "from,toRecipients,ccRecipients",
        },
        headers=headers,
    ):
        # from
        f = (msg.get("from") or {}).get("emailAddress") if isinstance(msg.get("from"), dict) else None
        if isinstance(f, dict):
            name = str(f.get("name") or "").strip()
            addr = str(f.get("address") or "").strip()
            if addr:
                seen[addr.lower()] = (name, addr)

        for (name, addr) in _emails_from_recipients(msg.get("toRecipients")) + _emails_from_recipients(msg.get("ccRecipients")):
            seen[addr.lower()] = (name, addr)

    # Filter to entries that look like the name (token-based, order-insensitive)
    tokens = [t for t in re.split(r"[^a-z0-9]+", _norm(display_name)) if t]
    filtered: List[Tuple[str, str]] = []
    for name, addr in seen.values():
        name_norm = _norm(name)
        if tokens and all(t in name_norm for t in tokens):
            filtered.append((name, addr))

    # If nothing matches the name tokens, return everything (caller can decide).
    return filtered or list(seen.values())


def _make_recipients(emails: Sequence[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for e in emails:
        e = e.strip()
        if not e:
            continue
        out.append({"emailAddress": {"address": e}})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an Outlook draft email from a Markdown draft file.")
    parser.add_argument(
        "--md",
        default=str(_REPO_ROOT / "runs/2026-01-15__b-braun-pdf-synthesis/exports/email_to_melanie_proctor__fy27_sc_data_needs__draft.md"),
        help="Path to markdown draft (must contain a 'Subject:' line).",
    )
    parser.add_argument("--to", default="", help="Optional To email (comma-separated).")
    parser.add_argument("--cc", default="", help="Optional Cc email (comma-separated).")
    parser.add_argument(
        "--resolve-to-name",
        default="",
        help="If --to is empty, try to resolve an address by searching mailbox for this display name (best-effort).",
    )
    args = parser.parse_args()

    md_path = Path(str(args.md)).expanduser().resolve()
    subject, body_text = _parse_subject_and_body(md_path)

    env = load_graph_env(_REPO_ROOT)
    auth = GraphAuthenticator(repo_root=_REPO_ROOT, env=env)
    client = GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )

    to_list = [e.strip() for e in str(args.to).split(",") if e.strip()]
    cc_list = [e.strip() for e in str(args.cc).split(",") if e.strip()]

    if not to_list and args.resolve_to_name:
        candidates = _resolve_email_from_name(client, str(args.resolve_to_name))
        if len(candidates) == 1:
            to_list = [candidates[0][1]]
        else:
            print("Could not uniquely resolve a To address from name search.")
            if candidates:
                print("Candidates found (name <email>):")
                for name, addr in candidates[:10]:
                    print(f"- {name} <{addr}>")
            print("Proceeding without a To recipient (draft will still be created).")

    payload: Dict[str, Any] = {
        "subject": subject,
        "body": {"contentType": "text", "content": body_text},
    }
    if to_list:
        payload["toRecipients"] = _make_recipients(to_list)
    if cc_list:
        payload["ccRecipients"] = _make_recipients(cc_list)

    created = client.post("me/messages", json=payload, timeout=90)
    msg_id = created.get("id")

    print("Created draft message in Drafts.")
    print(f"Subject: {subject}")
    if to_list:
        print(f"To: {', '.join(to_list)}")
    print(f"Message id: {msg_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
