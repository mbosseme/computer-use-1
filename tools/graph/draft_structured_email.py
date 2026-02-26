from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.drafts import create_draft_message
from agent_tools.graph.env import load_graph_env


DEFAULT_FALLBACKS = {
    "found_s31_link": "[PASTE FOUND-S-31 EPIC LINK HERE]",
    "ciam_s12_link": "[PASTE CIAM-S-12 EPIC LINK HERE]",
    "related_epics": "[ATTACH/PASTE SCREENSHOT FROM CRAIG'S TEAMS MESSAGE HERE]",
}


def _load_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Input JSON must be an object.")
    return data


def _to_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _ensure_fields(spec: Dict[str, Any]) -> None:
    required = ["subject", "to", "greeting", "context", "sections", "asks", "close"]
    missing = [k for k in required if k not in spec]
    if missing:
        raise RuntimeError(f"Missing required field(s): {', '.join(missing)}")


def _render_section(section: Dict[str, Any], fallbacks: Dict[str, str]) -> List[str]:
    lines: List[str] = []
    title = str(section.get("title") or "").strip()
    if title:
        lines.append(title)

    budget = str(section.get("budget") or "").strip()
    if budget:
        lines.append(f"- Budget estimate: {budget}")

    link_label = str(section.get("link_label") or "Epic link")
    link_key = str(section.get("link_key") or "").strip()
    link_value = str(section.get("link") or "").strip()
    if not link_value and link_key:
        link_value = str(fallbacks.get(link_key) or "").strip()
    if link_value:
        lines.append(f"- {link_label}: {link_value}")

    extra_lines = _to_list(section.get("extra_lines"))
    for extra in extra_lines:
        lines.append(f"- {extra}")

    bullets = _to_list(section.get("summary_bullets"))
    if bullets:
        lines.append("- High-level summary:")
        for bullet in bullets:
            lines.append(f"  - {bullet}")

    confirm = str(section.get("confirm") or "").strip()
    if confirm:
        lines.append(f"- {confirm}")

    return lines


def _build_body(spec: Dict[str, Any], fallbacks: Dict[str, str]) -> str:
    lines: List[str] = []
    lines.append(str(spec["greeting"]).strip())
    lines.append("")

    for c in _to_list(spec.get("context")):
        lines.append(c)
    lines.append("")

    sections = spec.get("sections")
    if not isinstance(sections, list) or not sections:
        raise RuntimeError("sections must be a non-empty array")

    for section in sections:
        if not isinstance(section, dict):
            continue
        lines.extend(_render_section(section, fallbacks))
        lines.append("")

    asks = _to_list(spec.get("asks"))
    if asks:
        lines.append("Please reply with:")
        for idx, ask in enumerate(asks, start=1):
            lines.append(f"{idx}) {ask}")
        lines.append("")

    touchpoint = str(spec.get("touchpoint_line") or "").strip()
    if touchpoint:
        lines.append(touchpoint)
        lines.append("")

    lines.append(str(spec.get("close") or "Thanks,").strip())
    signer = str(spec.get("signer") or "").strip()
    if signer:
        lines.append(signer)

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a structured Outlook draft email from a JSON spec.")
    parser.add_argument("--input", required=True, help="Path to JSON spec file")
    parser.add_argument(
        "--fallbacks",
        default="",
        help="Optional JSON file with placeholder/link substitutions",
    )
    args = parser.parse_args()

    spec = _load_json(Path(args.input))
    _ensure_fields(spec)

    fallbacks = dict(DEFAULT_FALLBACKS)
    if args.fallbacks:
        fb = _load_json(Path(args.fallbacks))
        for k, v in fb.items():
            fallbacks[str(k)] = str(v)

    env = load_graph_env(REPO_ROOT)
    auth = GraphAuthenticator(repo_root=REPO_ROOT, env=env)
    client = GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone),
    )

    body = _build_body(spec, fallbacks)
    draft = create_draft_message(
        client,
        subject=str(spec["subject"]).strip(),
        body_text=body,
        to=_to_list(spec.get("to")),
        cc=_to_list(spec.get("cc")),
    )

    print("DRAFT_ID:", draft.id)
    print("SUBJECT:", spec["subject"])
    print("TO:", "; ".join(_to_list(spec.get("to"))))
    print("CC:", "; ".join(_to_list(spec.get("cc"))))
    print("BODY_START")
    print(body)
    print("BODY_END")


if __name__ == "__main__":
    main()
