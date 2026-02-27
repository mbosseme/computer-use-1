"""File attachment operations for Microsoft Graph messages.

Handles attaching local files to draft messages and downloading attachments
from existing messages. For inline (CID) image attachments, see inline_images.py.

Typical usage (agent context)::

    from agent_tools.graph.attachments import attach_file, download_attachments

    # Attach a PDF to an existing draft
    info = attach_file(client, draft_id, Path("report.pdf"))

    # Download all attachments from a received message
    paths = download_attachments(client, message_id, Path("tmp/downloads"))
"""

from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from agent_tools.graph.client import GraphAPIClient

# Re-export from inline_images for convenience — callers can import from either module.
from agent_tools.graph.inline_images import AttachmentInfo, list_attachments  # noqa: F401


@dataclass(frozen=True)
class DownloadedAttachment:
    """Result of downloading a single attachment."""

    name: str
    path: Path
    size: int
    content_type: str


def attach_file(
    client: GraphAPIClient,
    message_id: str,
    file_path: Path,
    *,
    content_type: Optional[str] = None,
    skip_if_exists: bool = True,
    timeout_s: int = 90,
) -> AttachmentInfo:
    """Attach a local file to a Graph message (draft).

    Uses the small-file upload path (< 3 MB base64-encoded).  For larger files
    Graph requires the upload-session API which is not yet implemented here.

    Args:
        client: Authenticated GraphAPIClient.
        message_id: The Graph message ID (typically a draft).
        file_path: Path to the local file.
        content_type: MIME type override.  Auto-detected from extension if None.
        skip_if_exists: If True, skip attaching when a same-named attachment
            already exists on the message.  Prevents duplicate attachments on
            retries.
        timeout_s: HTTP request timeout in seconds.

    Returns:
        AttachmentInfo for the newly created (or already-existing) attachment.

    Raises:
        FileNotFoundError: If *file_path* does not exist.
    """
    file_path = Path(file_path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(str(file_path))

    # Idempotency: check existing attachments.
    if skip_if_exists:
        existing = list_attachments(client, message_id)
        for att in existing:
            if att.name == file_path.name:
                return att

    if content_type is None:
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = "application/octet-stream"

    payload: Dict[str, Any] = {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": file_path.name,
        "contentType": content_type,
        "isInline": False,
        "contentBytes": base64.b64encode(file_path.read_bytes()).decode("ascii"),
    }

    resp = client.post(
        f"me/messages/{message_id}/attachments",
        json=payload,
        timeout=timeout_s,
    )

    return AttachmentInfo(
        id=str(resp.get("id") or "").strip(),
        name=file_path.name,
        is_inline=False,
        content_id="",
    )


def download_attachment(
    client: GraphAPIClient,
    message_id: str,
    attachment_id: str,
    out_dir: Path,
    *,
    timeout_s: int = 90,
) -> DownloadedAttachment:
    """Download a single attachment by ID.

    Args:
        client: Authenticated GraphAPIClient.
        message_id: The Graph message ID.
        attachment_id: The attachment ID to download.
        out_dir: Directory to write the file into.  Created if absent.
        timeout_s: HTTP request timeout in seconds.

    Returns:
        DownloadedAttachment with local path and metadata.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    resp = client.get(
        f"me/messages/{message_id}/attachments/{attachment_id}",
        timeout=timeout_s,
    )

    name = str(resp.get("name") or "attachment").strip()
    content_bytes_b64 = resp.get("contentBytes") or ""
    content_type = str(resp.get("contentType") or "application/octet-stream").strip()
    size = int(resp.get("size") or 0)

    dest = out_dir / name
    dest.write_bytes(base64.b64decode(content_bytes_b64))

    return DownloadedAttachment(
        name=name,
        path=dest,
        size=size,
        content_type=content_type,
    )


def download_attachments(
    client: GraphAPIClient,
    message_id: str,
    out_dir: Path,
    *,
    filter_fn: Optional[Callable[[AttachmentInfo], bool]] = None,
    include_inline: bool = False,
    timeout_s: int = 90,
) -> List[DownloadedAttachment]:
    """Download all (or filtered) attachments from a message.

    This makes one call to list attachments, then one call per attachment to
    fetch content bytes.

    Args:
        client: Authenticated GraphAPIClient.
        message_id: The source message ID.
        out_dir: Directory to write files into.  Created if absent.
        filter_fn: Optional predicate on AttachmentInfo.  Only matching
            attachments are downloaded.
        include_inline: If False (default), skip inline (CID) attachments.
        timeout_s: HTTP request timeout per individual download.

    Returns:
        List of DownloadedAttachment for each file written to disk.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_attachments = list_attachments(client, message_id)

    results: List[DownloadedAttachment] = []
    for att in all_attachments:
        if not include_inline and att.is_inline:
            continue
        if filter_fn is not None and not filter_fn(att):
            continue
        if not att.id:
            continue

        dl = download_attachment(
            client,
            message_id,
            att.id,
            out_dir,
            timeout_s=timeout_s,
        )
        results.append(dl)

    return results
