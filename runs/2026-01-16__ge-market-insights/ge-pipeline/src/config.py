import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

# Load any default .env in current context (best-effort)
load_dotenv()


def _detect_repo_root() -> Path:
    """Best-effort detection of the repository root.

    Defaults to the parent of this file's directory (i.e., src/ -> repo root).
    Falls back to CWD if structure is different (e.g., during packaging/tests).
    """
    here = Path(__file__).resolve()
    # Expect .../repo/src/config.py -> repo root is parents[1]
    try:
        return here.parents[1]
    except IndexError:
        return Path.cwd()


class Config:
    """Loads configuration from environment variables and optional YAML file.

        Env vars:
            - BIGQUERY_PROJECT_ID
            - BIGQUERY_DATASET_ID (optional)

    YAML (config.yaml) (all optional):
      bigquery:
        project_id: str
        dataset_id: str
    """

    def __init__(self, root_dir: Optional[Path] = None) -> None:
        # Prefer repo root based on this module location to avoid CWD dependence
        self.root_dir = root_dir or _detect_repo_root()

        # Ensure repo-root .env is considered (non-destructive: override=False)
        load_dotenv(self.root_dir / ".env", override=False)

        # Load YAML if present
        yaml_cfg = {}
        yaml_path = self.root_dir / "config.yaml"
        if yaml_path.exists():
            with yaml_path.open("r") as f:
                yaml_cfg = yaml.safe_load(f) or {}

        # Env fallbacks
        env_project = (
            os.getenv("BIGQUERY_PROJECT_ID")
            or os.getenv("BIGQUERY_PROJECT")
            or os.getenv("VERTEX_AI_PROJECT")
            or os.getenv("GOOGLE_CLOUD_PROJECT")
        )
        env_dataset = os.getenv("BIGQUERY_DATASET_ID")

        y_bigquery = (yaml_cfg or {}).get("bigquery", {})
        self.BIGQUERY_PROJECT_ID = y_bigquery.get("project_id") or env_project
        self.BIGQUERY_DATASET_ID = y_bigquery.get("dataset_id") or env_dataset

    def get_credentials_path(self) -> Optional[str]:  # Deprecated placeholder
        """Return None (service account JSON unsupported)."""
        return None


def load_config() -> Config:
    """Return a Config anchored at the repository root by default.

    This avoids dependence on the current working directory, making notebooks
    and scripts runnable from any subfolder while still resolving .env and
    credentials at the repo root.
    """
    return Config(_detect_repo_root())
