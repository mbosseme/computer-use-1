from __future__ import annotations

import json
from pathlib import Path

import yaml

from src.runner import cli


def _load_golden_config() -> dict:
    golden_path = Path("config/golden.yaml")
    data = yaml.safe_load(golden_path.read_text())
    return data


def test_run_all_golden(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    cfg = _load_golden_config()
    cfg["io"] = {"snapshots_dir": str(tmp_path / "snapshots")}
    cfg.setdefault("reports", {})
    cfg["reports"].setdefault("deck", {})
    deck_cfg = cfg["reports"]["deck"]
    deck_cfg["template"] = str((repo_root / "brand/Premier-FY25-PPT 16x9-Feb25.potx").resolve())
    deck_cfg["style_yaml"] = str((repo_root / "config/deck.yaml").resolve())
    deck_cfg["output"] = "presentations/Deck_{run_id}.pptx"

    config_path = repo_root / f".tmp_run_all_{tmp_path.name}.yaml"
    config_path.write_text(yaml.safe_dump(cfg))

    outputs_dir = tmp_path / "outputs"
    try:
        cli.run_all(
            config=str(config_path),
            pipeline=True,
            reconciliation=False,
            summary=True,
            deck=True,
            no_charts=True,
            deck_template=None,
            deck_output=None,
            deck_style=None,
            outputs_dir=outputs_dir,
        )
    finally:
        if config_path.exists():
            config_path.unlink()

    assert outputs_dir.exists()
    manifests = list(outputs_dir.rglob("manifest.json"))
    assert manifests, "run manifest not written"
    manifest = json.loads(manifests[0].read_text())
    deck_entry = manifest["artifacts"].get("deck")
    outline_entry = manifest["artifacts"].get("outline")
    deck_vars_entry = manifest["artifacts"].get("deck_vars")
    assert deck_entry and Path(outputs_dir / deck_entry["path"]).exists()
    assert outline_entry and Path(outputs_dir / outline_entry["path"]).exists()
    assert deck_vars_entry and Path(outputs_dir / deck_vars_entry["path"]).exists()
    assert manifest["stages"] == {
        "pipeline": True,
        "reconciliation": False,
        "summary": True,
        "deck": True,
    }
