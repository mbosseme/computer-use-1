from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from agent_tools.graph.client import GraphAPIClient


def strip_markdown_to_text(text: str) -> str:
    """Best-effort Markdown → plain text.

    Keeps list structure and numbering. Intended for email body text.
    """

    # Remove markdown headings
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    # Remove bold markers
    text = text.replace("**", "")
    return text


def parse_markdown_email(md_path: Path) -> Tuple[str, str]:
    """Parse a markdown email draft that includes a `Subject:` line.

    Returns (subject, body_text).

    Expected structure:
    - A line starting with `Subject:`
    - Body starts after the first blank line following the Subject line
    """

    raw = md_path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    subject: Optional[str] = None
    body_lines: List[str] = []

    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("subject:"):
            subject = ln.split(":", 1)[1].strip()
            j = i + 1
            # Skip non-empty lines (if any) until blank
            while j < len(lines) and lines[j].strip() != "":
                j += 1
            # Skip blank lines
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            body_lines = lines[j:]
            break

    if not subject:
        raise ValueError(f"Could not find Subject: line in {md_path}")

    body_text = strip_markdown_to_text("\n".join(body_lines)).strip() + "\n"
    return subject, body_text


def make_recipients(emails: Sequence[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for email in emails:
        email = (email or "").strip()
        if not email:
            continue
        out.append({"emailAddress": {"address": email}})
    return out


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


def iter_graph_paged(
    client: GraphAPIClient,
    path: str,
    *,
    params: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout_s: int = 90,
) -> Iterable[Dict[str, Any]]:
    next_url: Optional[str] = path
    next_params: Optional[Dict[str, Any]] = params

    while next_url:
        resp = client.get(next_url, params=next_params, headers=headers, timeout=timeout_s)
        items = resp.get("value") if isinstance(resp, dict) else None
        if isinstance(items, list):
            for it in items:
                if isinstance(it, dict):
                    yield it

        next_link = resp.get("@odata.nextLink") if isinstance(resp, dict) else None
        next_url = str(next_link) if next_link else None
        next_params = None


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def resolve_email_candidates_from_mailbox(
    client: GraphAPIClient,
    display_name: str,
    *,
    top: int = 25,
) -> List[Tuple[str, str]]:
    """Best-effort: find candidate (name, email) pairs by searching mailbox.

    Useful when the caller only has a human name and wants to populate To/Cc.

    Note: This is heuristic; it may return multiple candidates.
    """

    headers = {"ConsistencyLevel": "eventual"}
    query = f'"{display_name}"'

    seen: Dict[str, Tuple[str, str]] = {}

    for msg in iter_graph_paged(
        client,
        "me/messages",
        params={
            "$search": query,
            "$top": int(top),
            "$select": "from,toRecipients,ccRecipients",
        },
        headers=headers,
    ):
        f = (msg.get("from") or {}).get("emailAddress") if isinstance(msg.get("from"), dict) else None
        if isinstance(f, dict):
            name = str(f.get("name") or "").strip()
            addr = str(f.get("address") or "").strip()
            if addr:
                seen[addr.lower()] = (name, addr)

        for (name, addr) in _emails_from_recipients(msg.get("toRecipients")) + _emails_from_recipients(msg.get("ccRecipients")):
            seen[addr.lower()] = (name, addr)

    # Token-based, order-insensitive name match: "Melanie Proctor" matches "Proctor, Melanie".
    tokens = [t for t in re.split(r"[^a-z0-9]+", _norm(display_name)) if t]
    filtered: List[Tuple[str, str]] = []
    for name, addr in seen.values():
        name_norm = _norm(name)
        if tokens and all(t in name_norm for t in tokens):
            filtered.append((name, addr))

    return filtered or list(seen.values())


@dataclass
class DraftCreateResult:
    id: str


def create_draft_message(
    client: GraphAPIClient,
    *,
    subject: str,
    body_text: str,
    to: Sequence[str] = (),
    cc: Sequence[str] = (),
    timeout_s: int = 90,
) -> DraftCreateResult:
    """Create an Outlook draft (in Drafts) via Graph.

    POST /me/messages creates a draft by default.
    """

    payload: Dict[str, Any] = {
        "subject": subject,
        "body": {"contentType": "text", "content": body_text},
    }
    if to:
        payload["toRecipients"] = make_recipients(to)
    if cc:
        payload["ccRecipients"] = make_recipients(cc)

    created = client.post("me/messages", json=payload, timeout=timeout_s)
    msg_id = str(created.get("id") or "").strip()
    if not msg_id:
        raise RuntimeError("Graph created a draft but returned no message id")

    return DraftCreateResult(id=msg_id)


def create_reply_draft(
    client: GraphAPIClient,
    *,
    message_id: str,
    body: str,
    content_type: str = "HTML",
    timeout_s: int = 90,
) -> DraftCreateResult:
    """Create a reply draft to an existing message.

    This uses POST /createReply to generate the draft with history,
    then PATCH to insert the new body *above* the history.
    """
    # 1. Create Reply Draft (creates item in Drafts w/ quoted history)
    reply_resp = client.post(f"me/messages/{message_id}/createReply", json={}, timeout=timeout_s)
    draft_id = str(reply_resp.get("id") or "").strip()
    if not draft_id:
        raise RuntimeError("Graph createReply returned no draft id")

    # 2. Get current body (the history)
    current_draft = client.get(f"me/messages/{draft_id}", timeout=timeout_s)
    current_body = (current_draft.get("body") or {}).get("content", "")

    # 3. Combine new content + history
    # Standard Outlook HTML separator
    separator = "<br><div class='BodyFragment'><hr></div>" if "div" in current_body else "<br><hr>"
    if content_type.upper() == "TEXT":
        # If user passed text, wrap in standard HTML wrapper
        new_content = f"<html><body>{html.escape(body)}</body></html>"
        full_body = f"{new_content}{separator}{current_body}"
    else:
        # User passed HTML
        full_body = f"{body}{separator}{current_body}"

    # 4. Patch the draft
    payload = {
        "body": {
            "contentType": "HTML",
            "content": full_body
        }
    }
    client.patch(f"me/messages/{draft_id}", json=payload, timeout=timeout_s)

    return DraftCreateResult(id=draft_id)


def create_reply_all_draft(
    client: GraphAPIClient,
    *,
    message_id: str,
    body: str = "",
    content_type: str = "HTML",
    to: Sequence[str] = (),
    cc: Sequence[str] = (),
    timeout_s: int = 90,
) -> DraftCreateResult:
    """Create a reply-all draft to an existing message.

    Uses POST /createReplyAll, then optionally patches in new body content
    prepended above the quoted history, and/or overrides To/Cc.

    Args:
        client: Authenticated GraphAPIClient.
        message_id: The Graph message ID to reply-all to.
        body: New body content (HTML or plain text depending on *content_type*).
            If empty, the draft is created with only the quoted history.
        content_type: ``"HTML"`` or ``"TEXT"``.
        to: Optional override for To recipients (email addresses).
        cc: Optional override for Cc recipients (email addresses).
        timeout_s: HTTP request timeout in seconds.

    Returns:
        DraftCreateResult with the new draft's message ID.
    """
    # 1. Create reply-all draft (inherits recipients + quoted history)
    reply_resp = client.post(
        f"me/messages/{message_id}/createReplyAll",
        json={},
        timeout=timeout_s,
    )
    draft_id = str(reply_resp.get("id") or "").strip()
    if not draft_id:
        raise RuntimeError("Graph createReplyAll returned no draft id")

    # 2. If caller supplied body or recipient overrides, patch the draft.
    needs_patch = bool(body) or bool(to) or bool(cc)
    if needs_patch:
        patch_payload: Dict[str, Any] = {}

        if body:
            # Get existing body (quoted history) so we can prepend new content.
            current_draft = client.get(f"me/messages/{draft_id}", timeout=timeout_s)
            current_body = (current_draft.get("body") or {}).get("content", "")

            separator = "<br><div class='BodyFragment'><hr></div>" if "div" in current_body else "<br><hr>"
            if content_type.upper() == "TEXT":
                new_content = f"<html><body>{html.escape(body)}</body></html>"
            else:
                new_content = body
            full_body = f"{new_content}{separator}{current_body}"

            patch_payload["body"] = {
                "contentType": "HTML",
                "content": full_body,
            }

        if to:
            patch_payload["toRecipients"] = make_recipients(to)
        if cc:
            patch_payload["ccRecipients"] = make_recipients(cc)

        client.patch(f"me/messages/{draft_id}", json=patch_payload, timeout=timeout_s)

    return DraftCreateResult(id=draft_id)


def update_draft_body(
    client: GraphAPIClient,
    draft_id: str,
    body_html: str,
    *,
    preserve_quoted: bool = False,
    timeout_s: int = 90,
) -> None:
    """Update (PATCH) the body of an existing draft message.

    Args:
        client: Authenticated GraphAPIClient.
        draft_id: The Graph message ID (must be a draft).
        body_html: The new HTML body content.
        preserve_quoted: If True, fetch the current body and append the
            quoted tail (everything from the first ``From:`` block onward)
            after the new content.  Useful for reply drafts where you want
            to replace only the top portion.
        timeout_s: HTTP request timeout in seconds.
    """
    if preserve_quoted:
        # Lazy import to avoid circular dependency.
        from agent_tools.graph.inline_images import split_quoted_tail

        current = client.get(f"me/messages/{draft_id}", timeout=timeout_s)
        current_html = (current.get("body") or {}).get("content", "")
        _, quoted = split_quoted_tail(current_html)
        if quoted:
            body_html = f"{body_html}{quoted}"

    payload = {
        "body": {
            "contentType": "HTML",
            "content": body_html,
        },
    }
    client.patch(f"me/messages/{draft_id}", json=payload, timeout=timeout_s)


def find_draft_by_subject(
    client: GraphAPIClient,
    subject: str,
    *,
    top: int = 200,
    timeout_s: int = 90,
) -> Optional[Dict[str, Any]]:
    """Find the most-recently-modified draft matching *subject* (case-insensitive).

    Searches the Drafts mail folder client side.  Returns the full message
    metadata dict (id, subject, lastModifiedDateTime, hasAttachments,
    toRecipients) or None if no match.

    Args:
        client: Authenticated GraphAPIClient.
        subject: Substring to match against draft subjects (case-insensitive).
        top: Maximum number of drafts to scan.
        timeout_s: HTTP request timeout in seconds.

    Returns:
        Message dict for the best match, or None.
    """
    params: Dict[str, Any] = {
        "$top": int(top),
        "$select": "id,subject,lastModifiedDateTime,hasAttachments,toRecipients,ccRecipients",
        "$orderby": "lastModifiedDateTime desc",
    }

    resp = client.get("me/mailFolders/drafts/messages", params=params, timeout=timeout_s)
    messages = resp.get("value") if isinstance(resp, dict) else None
    if not isinstance(messages, list):
        return None

    needle = (subject or "").strip().lower()
    for msg in messages:
        msg_subject = str(msg.get("subject") or "").strip().lower()
        if needle in msg_subject:
            return msg

    return None


@dataclass
class DraftVerifyResult:
    """Result of verifying a draft against expected phrases."""

    draft_id: str
    subject: str
    to: List[str]
    cc: List[str]
    attachment_names: List[str]
    body_html: str
    phrase_results: Dict[str, bool] = field(default_factory=dict)

    @property
    def all_passed(self) -> bool:
        return bool(self.phrase_results) and all(self.phrase_results.values())

    @property
    def passed_count(self) -> int:
        return sum(1 for v in self.phrase_results.values() if v)

    @property
    def total_count(self) -> int:
        return len(self.phrase_results)


def verify_draft(
    client: GraphAPIClient,
    draft_id: str,
    expected_phrases: Sequence[str] = (),
    *,
    timeout_s: int = 90,
) -> DraftVerifyResult:
    """Fetch a draft and verify that expected phrases appear in the body.

    Useful as a post-creation sanity check to ensure the draft body contains
    all required content before the user reviews it in Outlook.

    Args:
        client: Authenticated GraphAPIClient.
        draft_id: The Graph message ID.
        expected_phrases: Strings to search for in the HTML body
            (case-insensitive substring match).
        timeout_s: HTTP request timeout in seconds.

    Returns:
        DraftVerifyResult with metadata and per-phrase pass/fail.
    """
    msg = client.get(
        f"me/messages/{draft_id}",
        params={"$select": "id,subject,body,toRecipients,ccRecipients"},
        timeout=timeout_s,
    )

    subject = str(msg.get("subject") or "").strip()
    body_html = ((msg.get("body") or {}).get("content") or "")
    to_addrs = [addr for _, addr in _emails_from_recipients(msg.get("toRecipients"))]
    cc_addrs = [addr for _, addr in _emails_from_recipients(msg.get("ccRecipients"))]

    # Fetch attachments.
    att_resp = client.get(
        f"me/messages/{draft_id}/attachments",
        params={"$top": 200, "$select": "name,size,contentType"},
        timeout=timeout_s,
    )
    att_names: List[str] = []
    if isinstance(att_resp, dict) and isinstance(att_resp.get("value"), list):
        att_names = [str(a.get("name") or "") for a in att_resp["value"] if isinstance(a, dict)]

    # Phrase checks.
    phrase_results: Dict[str, bool] = {}
    body_lower = body_html.lower()
    for phrase in expected_phrases:
        phrase_results[phrase] = phrase.lower() in body_lower

    return DraftVerifyResult(
        draft_id=draft_id,
        subject=subject,
        to=to_addrs,
        cc=cc_addrs,
        attachment_names=att_names,
        body_html=body_html,
        phrase_results=phrase_results,
    )
