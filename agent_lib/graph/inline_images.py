from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from agent_tools.graph.client import GraphAPIClient


@dataclass(frozen=True)
class AttachmentInfo:
    id: str
    name: str
    is_inline: bool
    content_id: str


def list_attachments(client: GraphAPIClient, draft_id: str, *, top: int = 200) -> List[AttachmentInfo]:
    resp = client.get(f"me/messages/{draft_id}/attachments", params={"$top": int(top)})
    value = resp.get("value") if isinstance(resp, dict) else None
    if not isinstance(value, list):
        return []

    out: List[AttachmentInfo] = []
    for a in value:
        if not isinstance(a, dict):
            continue
        out.append(
            AttachmentInfo(
                id=str(a.get("id") or "").strip(),
                name=str(a.get("name") or "").strip(),
                is_inline=bool(a.get("isInline")),
                content_id=str(a.get("contentId") or "").strip(),
            )
        )
    return out


def delete_attachment(client: GraphAPIClient, draft_id: str, attachment_id: str) -> None:
    client.request("DELETE", f"me/messages/{draft_id}/attachments/{attachment_id}")


def add_inline_attachment(client: GraphAPIClient, draft_id: str, *, cid: str, path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(str(path))

    content_type, _ = mimetypes.guess_type(str(path))
    if not content_type:
        content_type = "application/octet-stream"

    payload: Dict[str, Any] = {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": path.name,
        "contentType": content_type,
        "isInline": True,
        "contentId": cid,
        "contentBytes": base64.b64encode(path.read_bytes()).decode("ascii"),
    }

    client.post(f"me/messages/{draft_id}/attachments", json=payload)


def replace_inline_attachments(
    client: GraphAPIClient,
    draft_id: str,
    *,
    cid_to_path: Sequence[Tuple[str, Path]],
    delete_if_name_prefixes: Sequence[str] = (),
) -> Dict[str, Any]:
    """Replace inline attachments for a set of CIDs.

    - Deletes existing inline attachments matching the target CIDs.
    - Optionally deletes inline attachments whose name starts with one of the prefixes.
    - Adds new inline attachments with the same CIDs.

    Returns a summary dict suitable for writing to an exports JSON artifact.
    """

    wanted_cids = {cid for cid, _ in cid_to_path}

    deleted: List[Dict[str, str]] = []
    for a in list_attachments(client, draft_id):
        if not a.id or not a.is_inline:
            continue

        should_delete = a.content_id in wanted_cids
        if not should_delete and delete_if_name_prefixes:
            should_delete = any((a.name or "").startswith(pref) for pref in delete_if_name_prefixes)

        if should_delete:
            delete_attachment(client, draft_id, a.id)
            deleted.append({"id": a.id, "name": a.name, "contentId": a.content_id})

    added: List[Dict[str, str]] = []
    for cid, path in cid_to_path:
        add_inline_attachment(client, draft_id, cid=cid, path=path)
        added.append({"contentId": cid, "name": path.name})

    return {"deleted": deleted, "added": added}


def split_quoted_tail(existing_html: str) -> Tuple[str, str]:
    """Return (head, quoted_tail).

    Preserves the existing quoted thread by locating the first From:/Sent: block
    for the reply chain and keeping everything from there onward.
    """

    markers = [
        "<br><b>From:</b>",
        "<b>From:</b>",
    ]

    idx = -1
    for m in markers:
        idx = existing_html.find(m)
        if idx >= 0:
            break

    if idx < 0:
        return existing_html, ""

    return existing_html[:idx], existing_html[idx:]
