from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: Optional[str] = None
    deployment_name: Optional[str] = None
    api_url: Optional[str] = None
    display_name: Optional[str] = None
    max_output_tokens: Optional[int] = None
    reasoning_effort: Optional[str] = None
    supports_temperature: Optional[bool] = None
    supports_reasoning_effort: Optional[bool] = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ModelConfig":
        return ModelConfig(
            provider=str(data.get("provider", "")),
            model=data.get("model"),
            deployment_name=data.get("deployment_name"),
            api_url=data.get("api_url"),
            display_name=data.get("display_name"),
            max_output_tokens=data.get("max_output_tokens"),
            reasoning_effort=data.get("reasoning_effort"),
            supports_temperature=data.get("supports_temperature"),
            supports_reasoning_effort=data.get("supports_reasoning_effort"),
        )


def load_models_config(repo_root: Path) -> dict[str, ModelConfig]:
    """Load config/models.json if present.

    This is intentionally optional: run branches can start with just env vars.
    """

    config_path = repo_root / "config" / "models.json"
    if not config_path.exists():
        return {}

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("config/models.json must contain an object at top level")

    parsed: dict[str, ModelConfig] = {}
    for model_name, model_data in raw.items():
        if not isinstance(model_data, dict):
            raise ValueError(f"Model config for {model_name!r} must be an object")
        parsed[str(model_name)] = ModelConfig.from_dict(model_data)

    return parsed
