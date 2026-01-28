"""Context creation utilities for the CLI pipeline."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict

import yaml

from .orchestrator import RunContext


@dataclass
class StructuredLogger:
    """Extremely small JSON logger backed by stdout prints."""

    def info(self, payload: Dict[str, Any]) -> None:
        print(json.dumps({"level": "INFO", **payload}, default=str))

    def error(self, payload: Dict[str, Any]) -> None:
        print(json.dumps({"level": "ERROR", **payload}, default=str))


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _resolve_run_id(cfg: Dict[str, Any]) -> str:
    run_cfg = cfg.get("run", {}) if isinstance(cfg, dict) else {}
    run_id = run_cfg.get("run_id") if isinstance(run_cfg, dict) else None
    if run_id and run_id != "auto":
        return str(run_id)
    tz_offset_minutes = 0
    if isinstance(run_cfg, dict) and isinstance(run_cfg.get("timezone_offset_minutes"), (int, float)):
        tz_offset_minutes = int(run_cfg["timezone_offset_minutes"])
    tz = timezone(timedelta(minutes=tz_offset_minutes))
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def _detect_repo_root(start: Path) -> Path:
    markers = {"README.md", "requirements.txt"}
    extra_dirs = {"src", "docs"}
    current = start.resolve()
    for _ in range(12):
        marker_hits = {m for m in markers if (current / m).exists()}
        dir_hits = {d for d in extra_dirs if (current / d).is_dir()}
        if marker_hits == markers and dir_hits:
            return current
        if current.parent == current:
            break
        current = current.parent
    return start


def make_context(config_path: str) -> RunContext:
    """Materialize a :class:`RunContext` from a YAML config path."""
    cfg_path = Path(config_path).expanduser().resolve()
    cfg = _load_yaml(cfg_path)

    run_id = _resolve_run_id(cfg)

    repo_root = _detect_repo_root(cfg_path.parent)
    snapshots_root = cfg.get("io", {}).get("snapshots_dir", "snapshots")
    snapshots_root_path = (repo_root / snapshots_root).resolve()
    snapshots_root_path.mkdir(parents=True, exist_ok=True)
    run_dir = snapshots_root_path / run_id
    result_sheets_dir = run_dir / "result_sheets"

    logger = StructuredLogger()
    paths = {
        "run_dir": str(run_dir),
        "result_sheets_dir": str(result_sheets_dir),
        "snapshots_dir": str(snapshots_root_path),
        "config_path": str(cfg_path),
        "repo_root": str(repo_root),
    }

    ctx = RunContext(cfg=cfg, run_id=run_id, paths=paths, logger=logger)
    ctx.cache["run_started_at"] = datetime.now(timezone.utc).isoformat()
    return ctx
