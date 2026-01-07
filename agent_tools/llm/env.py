from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


@dataclass(frozen=True)
class AzureOpenAIEnv:
    api_key: Optional[str]
    api_url: Optional[str]
    responses_api_url: Optional[str]
    deployment_name: Optional[str]


def load_repo_dotenv(repo_root: Path) -> None:
    """Best-effort load of repo-root .env (never commit secrets).

    If python-dotenv isn't installed, this is a no-op.
    """

    if load_dotenv is None:
        return

    dotenv_path = repo_root / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=False)


def read_azure_openai_env() -> AzureOpenAIEnv:
    return AzureOpenAIEnv(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_url=os.getenv("AZURE_OPENAI_URL"),
        responses_api_url=os.getenv("AZURE_OPENAI_RESPONSES_URL"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    )
