"""Mail search and thread export for Microsoft Graph.

Provides a public API for searching messages across the mailbox and exporting
conversation threads to Markdown.

Typical usage (agent context)::

    from agent_tools.graph.mail_search import search_messages, export_thread_markdown

    # Find recent messages from a sender
    msgs = search_messages(client, query='"from:sender@example.com"', top=10)

    # Export an entire thread matching a subject to Markdown
    export_thread_markdown(client, subject="Q4 Review", out_path=Path("tmp/thread.md"))
"""

from __future__ import annotations

import re
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from agent_tools.graph.client import GraphAPIClient
from agent_tools.graph.drafts import _emails_from_recipients, iter_graph_paged


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def html_to_text(html_str: str) -> str:
    """Convert HTML to plain text (best-effort).

    Handles ``<br>``, ``</p>``, ``</div>`` → newlines, strips remaining tags,
    and un-escapes HTML entities.
    """
    if not html_str:
        return ""

    text = html_str
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*div\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Message search
# ---------------------------------------------------------------------------

_DEFAULT_SELECT = (
    "id,subject,from,sender,toRecipients,ccRecipients,"
    "sentDateTime,receivedDateTime,conversationId,"
    "hasAttachments,bodyPreview,body,internetMessageId"
)


def search_messages(
    client: GraphAPIClient,
    *,
    query: str,
    folder: Optional[str] = None,
    top: int = 50,
    select: Optional[str] = None,
    max_messages: int = 500,
    timeout_s: int = 90,
) -> List[Dict[str, Any]]:
    """Search messages using the Graph ``$search`` operator.

    Results are sorted locally by ``receivedDateTime`` descending (newest
    first) because Graph does not allow ``$orderby`` with ``$search``.

    Args:
        client: Authenticated GraphAPIClient.
        query: OData ``$search`` expression.  Wrap phrases in double-quotes
            inside the string, e.g. ``'"McKinsey" AND "sample"'``.
        folder: Optional mail folder ID or well-known name (e.g.
            ``"SentItems"``, ``"Inbox"``).  If None, searches the entire
            mailbox (``me/messages``).
        top: Page size per request.
        select: OData ``$select`` fields.  Uses a sensible default if None.
        max_messages: Safety cap on total messages returned.
        timeout_s: HTTP timeout per request.

    Returns:
        List of message dicts sorted by receivedDateTime descending.
    """
    if folder:
        path = f"me/mailFolders/{folder}/messages"
    else:
        path = "me/messages"

    params: Dict[str, Any] = {
        "$search": query,
        "$top": int(top),
        "$select": select or _DEFAULT_SELECT,
    }
    headers = {"ConsistencyLevel": "eventual"}

    messages: List[Dict[str, Any]] = []
    for msg in iter_graph_paged(client, path, params=params, headers=headers, timeout_s=timeout_s):
        messages.append(msg)
        if len(messages) >= max_messages:
            break

    # Sort locally (Graph forbids $orderby with $search).
    messages.sort(
        key=lambda m: str(m.get("receivedDateTime") or m.get("sentDateTime") or ""),
        reverse=True,
    )
    return messages


def search_sent_messages(
    client: GraphAPIClient,
    *,
    query: str,
    top: int = 50,
    max_messages: int = 500,
    timeout_s: int = 90,
) -> List[Dict[str, Any]]:
    """Convenience: search the SentItems folder.

    See :func:`search_messages` for parameter docs.
    """
    return search_messages(
        client,
        query=query,
        folder="SentItems",
        top=top,
        max_messages=max_messages,
        timeout_s=timeout_s,
    )


def find_latest_from_sender(
    client: GraphAPIClient,
    sender_query: str,
    *,
    with_attachments: bool = False,
    top: int = 50,
    timeout_s: int = 90,
) -> Optional[Dict[str, Any]]:
    """Find the most recent message from a sender (or matching a sender query).

    Args:
        client: Authenticated GraphAPIClient.
        sender_query: Search string for the sender, e.g. ``'"Itani"'`` or
            ``'"itani@mckinsey.com"'``.
        with_attachments: If True, only consider messages with attachments.
        top: Number of candidates to fetch.
        timeout_s: HTTP timeout per request.

    Returns:
        The most-recent matching message dict, or None.
    """
    msgs = search_messages(
        client,
        query=sender_query,
        top=top,
        timeout_s=timeout_s,
    )

    for msg in msgs:  # already sorted newest-first
        if with_attachments and not msg.get("hasAttachments"):
            continue
        # Validate sender text matches query keywords.
        sender_obj = msg.get("from") or {}
        if isinstance(sender_obj, dict):
            ea = sender_obj.get("emailAddress") or {}
            sender_text = f"{ea.get('name', '')} {ea.get('address', '')}".lower()
        else:
            sender_text = ""

        # Relax: if query tokens appear in sender text, accept.
        tokens = [t.strip('"').lower() for t in re.split(r"[\s\"]+", sender_query) if t.strip('"')]
        tokens = [t for t in tokens if t not in ("and", "or")]
        if tokens and all(t in sender_text for t in tokens):
            return msg

    # Fallback: return newest if any exist.
    return msgs[0] if msgs else None


# ---------------------------------------------------------------------------
# Thread export
# ---------------------------------------------------------------------------


def _format_dt(iso_str: str, tz_name: Optional[str] = None) -> str:
    """Format an ISO datetime string for display."""
    if not iso_str:
        return ""
    s = iso_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        return iso_str

    if tz_name and ZoneInfo is not None:
        try:
            dt = dt.astimezone(ZoneInfo(tz_name))
        except Exception:
            pass

    tz_abbrev = dt.strftime("%Z") if dt.tzinfo else ""
    return f"{dt.strftime('%a %Y-%m-%d %I:%M %p')} {tz_abbrev}".replace(" 0", " ").rstrip()


def _format_recipients(recipients: Any) -> str:
    """Format a list of Graph emailAddress recipients for Markdown."""
    pairs = _emails_from_recipients(recipients)
    parts: List[str] = []
    for name, addr in pairs:
        if name and name != addr:
            parts.append(f"{name} <{addr}>")
        else:
            parts.append(addr)
    return ", ".join(parts)


def export_thread_markdown(
    client: GraphAPIClient,
    subject: str,
    out_path: Path,
    *,
    max_messages: int = 200,
    tz_name: Optional[str] = None,
    timeout_s: int = 90,
) -> Path:
    """Search for messages matching *subject* and export the thread as Markdown.

    Messages are sorted chronologically (oldest first) and written to
    *out_path*.  The thread includes From/To/Cc headers, date, and body
    text (HTML → plain text).

    Args:
        client: Authenticated GraphAPIClient.
        subject: Subject substring to search for (wrapped in ``$search``).
        out_path: Destination Markdown file.  Parent directories are created.
        max_messages: Maximum messages to include.
        tz_name: Optional timezone name for date formatting (e.g.
            ``"America/New_York"``).
        timeout_s: HTTP timeout per request.

    Returns:
        The resolved *out_path*.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Search with quoted subject.
    query = f'"{subject}"'
    msgs = search_messages(
        client,
        query=query,
        max_messages=max_messages * 2,  # over-fetch for filtering
        timeout_s=timeout_s,
    )

    # Client-side filter: subject must contain the search term.
    needle = subject.strip().lower()
    filtered: List[Dict[str, Any]] = []
    for msg in msgs:
        msg_subj = str(msg.get("subject") or "").strip().lower()
        if needle in msg_subj:
            filtered.append(msg)
            if len(filtered) >= max_messages:
                break

    # Sort chronologically (oldest first) for reading order.
    filtered.sort(key=lambda m: str(m.get("sentDateTime") or m.get("receivedDateTime") or ""))

    lines: List[str] = [
        f"# Thread: {subject}",
        f"_Exported {len(filtered)} message(s)_",
        "",
    ]

    for i, msg in enumerate(filtered, 1):
        from_ea = (msg.get("from") or {}).get("emailAddress") or {} if isinstance(msg.get("from"), dict) else {}
        from_name = from_ea.get("name", "")
        from_addr = from_ea.get("address", "")
        from_display = f"{from_name} <{from_addr}>" if from_name else from_addr

        sent = _format_dt(str(msg.get("sentDateTime") or ""), tz_name)
        to_str = _format_recipients(msg.get("toRecipients"))
        cc_str = _format_recipients(msg.get("ccRecipients"))
        subj = str(msg.get("subject") or "")

        body_html = ((msg.get("body") or {}).get("content") or "")
        body_text = html_to_text(body_html)

        lines.append(f"---")
        lines.append(f"## Message {i}")
        lines.append(f"**From:** {from_display}  ")
        lines.append(f"**Date:** {sent}  ")
        lines.append(f"**Subject:** {subj}  ")
        lines.append(f"**To:** {to_str}  ")
        if cc_str:
            lines.append(f"**Cc:** {cc_str}  ")
        lines.append("")
        lines.append(body_text)
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
