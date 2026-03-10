from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from agent_tools.llm.env import load_repo_dotenv


_RESERVED_SCOPES = {"offline_access", "openid", "profile"}


@dataclass(frozen=True)
class GraphEnv:
    tenant_id: str
    client_id: str
    authority_url: str
    scopes: List[str]
    token_cache_file: str
    base_url: str
    planner_timezone: Optional[str]


def _interpolate_authority(authority: str, tenant_id: str) -> str:
    # python-dotenv does not always expand ${VARS}; support the common pattern.
    return authority.replace("${AZURE_TENANT_ID}", tenant_id)


def _parse_scopes(raw: str) -> List[str]:
    scopes = [s.strip() for s in raw.replace(" ", ",").split(",") if s.strip()]

    # Filter reserved scopes to avoid MSAL "reserved scope" errors.
    filtered: List[str] = []
    seen = set()
    for s in scopes:
        if s in _RESERVED_SCOPES:
            continue
        if s not in seen:
            filtered.append(s)
            seen.add(s)

    return filtered


def load_graph_env(repo_root: Path) -> GraphEnv:
    load_repo_dotenv(repo_root)

    tenant_id = (os.getenv("AZURE_TENANT_ID") or "").strip()
    if not tenant_id:
        raise RuntimeError("Missing AZURE_TENANT_ID")

    client_id = (os.getenv("AZURE_CLIENT_ID") or "").strip().lower()
    if not client_id:
        raise RuntimeError("Missing AZURE_CLIENT_ID")

    authority_url = (os.getenv("AZURE_AUTHORITY_URL") or "").strip()
    if not authority_url:
        authority_url = f"https://login.microsoftonline.com/{tenant_id}"
    authority_url = _interpolate_authority(authority_url, tenant_id)

    if authority_url.rstrip("/").endswith("/common"):
        raise RuntimeError(
            "AZURE_AUTHORITY_URL must be tenant-specific (not /common). "
            "Use https://login.microsoftonline.com/<tenant_id>"
        )

    raw_scopes = os.getenv(
        "GRAPH_API_SCOPES",
        "Calendars.ReadWrite,Tasks.ReadWrite,User.Read",
    )
    scopes = _parse_scopes(raw_scopes)
    if not scopes:
        raise RuntimeError("GRAPH_API_SCOPES resolved to an empty scope set")

    token_cache_file = (os.getenv("TOKEN_CACHE_FILE") or ".token_cache.json").strip()

    base_url = (os.getenv("GRAPH_API_BASE_URL") or "https://graph.microsoft.com/v1.0").strip()

    planner_timezone = (os.getenv("PLANNER_TIMEZONE") or "").strip() or None

    return GraphEnv(
        tenant_id=tenant_id,
        client_id=client_id,
        authority_url=authority_url,
        scopes=scopes,
        token_cache_file=token_cache_file,
        base_url=base_url,
        planner_timezone=planner_timezone,
    )
