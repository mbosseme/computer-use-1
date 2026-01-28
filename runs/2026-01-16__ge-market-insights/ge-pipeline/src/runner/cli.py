"""Typer-based entrypoint for orchestrating the analysis pipeline."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import typer
from typer.models import OptionInfo

from .context import make_context
from .orchestrator import run_pipeline
from ..validation.parity import ParityResult, compare_prd_answers
from ..steps import charts_step, export_step, kpis_step, materialize_step, outline_step, qa_step, windowing_step, selector_step
from ..templates import render_outline as outline_renderer
from ..pptx_builder import build_deck as deck_builder

from types import SimpleNamespace
import shutil
from dataclasses import dataclass


def _looks_like_timestamped(name: str) -> bool:
    try:
        datetime.strptime(name, "%Y-%m-%d_%H-%M-%S")
        return True
    except ValueError:
        return False


def _latest_timestamped_dir(base: Path) -> Path:
    candidates = sorted(
        (child for child in base.iterdir() if child.is_dir() and _looks_like_timestamped(child.name)),
        key=lambda p: p.name,
        reverse=True,
    )
    if not candidates:
        raise typer.BadParameter(f"No timestamped directories found under {base}")
    return candidates[0]


def _validate_dir(path: Path, *, must_exist: bool = True, label: str = "directory") -> Path:
    resolved = path.expanduser().resolve()
    if must_exist and not resolved.exists():
        raise typer.BadParameter(f"{label} does not exist: {resolved}")
    if must_exist and not resolved.is_dir():
        raise typer.BadParameter(f"{label} is not a directory: {resolved}")
    return resolved


@dataclass
class DeckRunConfig:
    template: Path
    output: Path
    style: Path | None
    deck_vars: Path
    csv: Path
    charts_dir: Path


def _run_pipeline_stage(ctx, include_charts: bool) -> None:
    steps = [
        windowing_step.Step(),
        materialize_step.Step(),
        kpis_step.Step(),
        qa_step.Step(),
        export_step.Step(),
    ]
    if include_charts:
        steps.append(charts_step.Step())
    run_pipeline(ctx, steps)


def _run_summary_stage(ctx) -> None:
    selector_step.Step().run(ctx)
    outline_step.Step().run(ctx)


def _rebind_context_to_snapshot(ctx, snapshot_dir: Path) -> None:
    snapshot_dir = snapshot_dir.resolve()
    ctx.paths["run_dir"] = str(snapshot_dir)
    ctx.paths["result_sheets_dir"] = str((snapshot_dir / "result_sheets").resolve())
    ctx.run_id = snapshot_dir.name
    if isinstance(ctx.cfg, dict):
        run_cfg = ctx.cfg.setdefault("run", {})
        if isinstance(run_cfg, dict):
            run_cfg["run_id"] = ctx.run_id


def _hydrate_answers_from_snapshot(ctx, snapshot_dir: Path) -> None:
    answers_path = snapshot_dir / "prd_answers.csv"
    if not answers_path.exists():
        raise typer.BadParameter(f"Snapshot is missing prd_answers.csv: {answers_path}")
    answers_df = pd.read_csv(answers_path)
    ctx.cache["answers_df"] = answers_df
    export_cache = ctx.cache.setdefault("export", {})
    if isinstance(export_cache, dict):
        export_cache["answers_df"] = answers_df


def _resolve_snapshot_dir_for_reuse(
    *,
    explicit: Optional[Path],
    snapshots_root: Path,
    label: str = "analytics snapshot",
) -> Path:
    if explicit is not None:
        snapshot_dir = _validate_dir(explicit, label=label)
    else:
        snapshot_dir = _latest_timestamped_dir(_validate_dir(snapshots_root, label="snapshots root"))
    required = snapshot_dir / "prd_answers.csv"
    if not required.exists():
        raise typer.BadParameter(f"{label} missing required file prd_answers.csv: {required}")
    return snapshot_dir


def _hydrate_reconciliation_cache(ctx, recon_dir: Path) -> Optional[Path]:
    recon_dir = recon_dir.resolve()
    summary_json = recon_dir / "summary.json"
    if not summary_json.exists():
        raise typer.BadParameter(f"Reconciliation run missing summary.json: {summary_json}")
    summary_payload = json.loads(summary_json.read_text(encoding="utf-8"))
    ctx.cache["reconciliation_summary"] = {
        "output_dir": str(recon_dir),
        "summary_metrics": summary_payload,
        "overlap_summary": summary_payload.get("overlap_summary"),
    }
    manifest_path = recon_dir / "manifest.json"
    if manifest_path.exists():
        ctx.cache["reconciliation_manifest"] = str(manifest_path)
        return manifest_path
    return None


def _resolve_reconciliation_dir_for_reuse(
    *,
    explicit: Optional[Path],
    recon_base: Path,
) -> Path:
    base_dir = _validate_dir(recon_base, label="reconciliation base directory")
    if explicit is not None:
        recon_dir = _validate_dir(explicit, label="reconciliation run")
    else:
        recon_dir = _latest_timestamped_dir(base_dir)
    summary_json = recon_dir / "summary.json"
    if not summary_json.exists():
        raise typer.BadParameter(f"Reconciliation run missing summary.json: {summary_json}")
    return recon_dir


def _coerce_optional_path(value: Optional[Path]) -> Optional[Path]:
    if value is None:
        return None
    if isinstance(value, OptionInfo):
        return None
    return value


def _ensure_path(path_like: Path | str | None, base: Path) -> Optional[Path]:
    if path_like in (None, "", False):
        return None
    path = path_like if isinstance(path_like, Path) else Path(str(path_like))
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def _run_reconciliation_stage(ctx, repo_root: Path, recon_cfg: Dict[str, Any]) -> Optional[Path]:
    dashboard_path_raw = recon_cfg.get("dashboard_path") if isinstance(recon_cfg, dict) else None
    if not dashboard_path_raw:
        raise typer.BadParameter("reconciliation stage requires reports.reconciliation.dashboard_path or override")

    dashboard_path = _ensure_path(dashboard_path_raw, repo_root)
    assert dashboard_path is not None
    if not dashboard_path.exists():
        raise FileNotFoundError(f"Dashboard export not found: {dashboard_path}")

    output_base_raw = recon_cfg.get("output_dir", "recon")
    output_base = _ensure_path(output_base_raw, repo_root)
    assert output_base is not None
    output_base.mkdir(parents=True, exist_ok=True)
    run_dir = build_output_directory(output_base)

    shares_path = _ensure_path(recon_cfg.get("shares_path"), repo_root)
    category_map_path = _ensure_path(recon_cfg.get("category_map_path"), repo_root)
    contract_mapping_path = _ensure_path(recon_cfg.get("contract_mapping_path"), repo_root)

    shares_df = _load_shares_dataframe(ctx, shares_path)
    dashboard_df = _load_dashboard_dataframe(dashboard_path)
    category_map = load_category_map(category_map_path)
    contract_map = load_contract_number_mapping(contract_mapping_path)

    status_column = recon_cfg.get("status_column", "System Status")
    required_status = recon_cfg.get("required_status", "PA-Completed")
    category_column = recon_cfg.get("category_column", "Contract Category")
    facility_column = recon_cfg.get("facility_column", "Entity Code")
    spend_column = recon_cfg.get("spend_column", "Category Spend")
    spend_positive_only = bool(recon_cfg.get("spend_positive_only", True))
    emit_intersection = bool(recon_cfg.get("emit_intersection", True))
    contract_number_column = recon_cfg.get("contract_number_column")

    result = run_dashboard_reconciliation(
        shares_df,
        dashboard_df,
        category_map=category_map,
        contract_map=contract_map,
        contract_number_column=contract_number_column,
        status_column=status_column,
        required_status=required_status,
        category_column=category_column,
        facility_column=facility_column,
        spend_column=spend_column,
        spend_positive_only=spend_positive_only,
        emit_intersection=emit_intersection,
    )

    member_delta_threshold = float(recon_cfg.get("member_delta_threshold", 5.0))
    overlap_threshold = float(recon_cfg.get("overlap_threshold", 0.5))
    summary_metrics = compute_summary_metrics(
        result.members,
        member_delta_threshold=member_delta_threshold,
        overlap_threshold=overlap_threshold,
    )

    members_path = run_dir / "members.csv"
    spend_path = run_dir / "spend.csv"
    members_intersection_path = run_dir / "members_intersection.csv"
    spend_intersection_path = run_dir / "spend_intersection.csv"
    mapped_categories_path = run_dir / "mapped_category_details.csv"
    unmapped_categories_path = run_dir / "unmapped_categories.csv"

    result.members.to_csv(members_path, index=False)
    result.spend.to_csv(spend_path, index=False)
    if emit_intersection and result.members_intersection is not None:
        result.members_intersection.to_csv(members_intersection_path, index=False)
    if emit_intersection and result.spend_intersection is not None:
        result.spend_intersection.to_csv(spend_intersection_path, index=False)
    result.mapped_category_details.to_csv(mapped_categories_path, index=False)
    result.unmapped_categories.to_csv(unmapped_categories_path, index=False)

    summary_md_path = run_dir / "summary.md"
    summary_json_path = run_dir / "summary.json"
    notes = {
        "dashboard_path": str(dashboard_path),
        "shares_source": "pipeline" if shares_path is None else str(shares_path),
        "category_map": str(category_map_path) if category_map_path is not None else None,
        "contract_mapping": str(contract_mapping_path) if contract_mapping_path is not None else None,
        "contract_number_column": contract_number_column,
        "spend_positive_only": spend_positive_only,
        "emit_intersection": emit_intersection,
        "status_column": status_column,
        "required_status": required_status,
        "category_column": category_column,
        "facility_column": facility_column,
        "spend_column": spend_column,
        "member_delta_threshold": member_delta_threshold,
        "overlap_threshold": overlap_threshold,
    }
    summary_text = render_summary_markdown(
        summary_metrics,
        mapping_counts=result.mapping_counts,
        overlap_summary=result.overlap_summary,
        notes={key: value for key, value in notes.items() if value is not None},
    )
    summary_md_path.write_text(summary_text, encoding="utf-8")
    summary_payload = {
        "member_delta_threshold": summary_metrics["member_delta_threshold"],
        "overlap_threshold": summary_metrics["overlap_threshold"],
        "member_delta_gt_threshold_pct": summary_metrics["member_delta_gt_threshold_pct"],
        "overlap_lt_threshold_pct": summary_metrics["overlap_lt_threshold_pct"],
        "top_member_deltas": _frame_to_records(summary_metrics.get("top_member_deltas")),
        "top_spend_deltas": _frame_to_records(summary_metrics.get("top_spend_deltas")),
        "mapping_counts": _to_serializable(dict(result.mapping_counts)),
        "filter_counts": _to_serializable(dict(result.filter_counts)),
        "dashboard_stats": _to_serializable(dict(result.dashboard_stats)),
        "overlap_summary": _to_serializable(dict(result.overlap_summary)),
        "notes": {key: value for key, value in notes.items() if value is not None},
    }
    summary_json_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    manifest = {
        "dashboard": str(dashboard_path),
        "shares_source": "pipeline" if shares_path is None else str(shares_path),
        "summary_metrics": summary_payload,
        "overlap_summary": dict(result.overlap_summary),
        "mapping_counts": dict(result.mapping_counts),
        "filter_counts": dict(result.filter_counts),
        "dashboard_stats": dict(result.dashboard_stats),
        "files": {
            "members": str(members_path),
            "spend": str(spend_path),
            "members_intersection": str(members_intersection_path) if emit_intersection else None,
            "spend_intersection": str(spend_intersection_path) if emit_intersection else None,
            "mapped_category_details": str(mapped_categories_path),
            "unmapped_categories": str(unmapped_categories_path),
            "summary_markdown": str(summary_md_path),
            "summary_json": str(summary_json_path),
        },
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    ctx.cache["reconciliation_summary"] = {
        "output_dir": str(run_dir),
        "summary_metrics": summary_payload,
        "overlap_summary": dict(result.overlap_summary),
    }
    ctx.cache["reconciliation_manifest"] = str(manifest_path)

    return manifest_path


def _run_deck_stage(deck_cfg: DeckRunConfig) -> Path:
    deck_args = SimpleNamespace(
        template=str(deck_cfg.template),
        csv=str(deck_cfg.csv),
        charts=str(deck_cfg.charts_dir),
        out=str(deck_cfg.output),
        style_yaml=str(deck_cfg.style) if deck_cfg.style else None,
        deck_vars=str(deck_cfg.deck_vars),
    )
    Path(deck_cfg.output).parent.mkdir(parents=True, exist_ok=True)
    return deck_builder.build(deck_args)
from ..reconciliation import (
    build_output_directory,
    compare_to_prd,
    filter_measured_members,
    resolve_latest_prd_answers,
    summarize_by_category,
    reconcile_dashboard as run_dashboard_reconciliation,
    load_category_map,
    load_contract_number_mapping,
    compute_summary_metrics,
    render_summary_markdown,
)

app = typer.Typer(no_args_is_help=True)

DEFAULT_CONTRACT_MAPPING_PATH = Path(
    "reference_files/Contract Number and Name to Contract Category Mapping.csv"
)


def _deck_config(
    ctx_cfg: dict[str, Any] | Any,
    repo_root: Path,
    run_dir: Path,
    template_override: Optional[Path] = None,
    output_override: Optional[Path] = None,
    style_override: Optional[Path] = None,
) -> DeckRunConfig:
    reports_cfg = ctx_cfg.get("reports", {}) if isinstance(ctx_cfg, dict) else {}
    deck_cfg = reports_cfg.get("deck", {}) if isinstance(reports_cfg, dict) else {}
    template_cfg = template_override or deck_cfg.get("template")
    if template_cfg is None:
        raise typer.BadParameter("Deck template must be provided via config or --deck-template")
    template_path = template_cfg if isinstance(template_cfg, Path) else Path(str(template_cfg))
    if not template_path.is_absolute():
        template_path = (repo_root / template_path).resolve()
    if not template_path.exists():
        raise typer.BadParameter(f"Deck template not found: {template_path}")

    style_cfg = style_override if style_override is not None else deck_cfg.get("style_yaml")
    style_path = None
    if style_cfg:
        style_path = style_cfg if isinstance(style_cfg, Path) else Path(str(style_cfg))
        if not style_path.is_absolute():
            style_path = (repo_root / style_path).resolve()

    output_cfg = output_override if output_override is not None else deck_cfg.get("output")
    if output_cfg is None:
        output_path = run_dir / "presentations" / f"Deck_{run_dir.name}.pptx"
    else:
        output_path = output_cfg if isinstance(output_cfg, Path) else Path(str(output_cfg))
        if not output_path.is_absolute():
            formatted = str(output_path).format(run_id=run_dir.name)
            output_path = (run_dir / formatted).resolve()
        else:
            output_path = Path(str(output_path).format(run_id=run_dir.name))

    deck_vars_path = run_dir / "deck_vars.json"
    csv_path = run_dir / "prd_answers.csv"
    charts_dir = (run_dir / "result_sheets").resolve()

    return DeckRunConfig(
        template=template_path,
        output=output_path,
        style=style_path,
        deck_vars=deck_vars_path,
        csv=csv_path,
        charts_dir=charts_dir,
    )


def _load_shares_dataframe(
    ctx,
    shares_path: Optional[Path],
) -> pd.DataFrame:
    if shares_path is not None:
        resolved = shares_path.expanduser().resolve()
        if not resolved.exists():
            raise typer.BadParameter(f"Shares file does not exist: {resolved}")
        suffix = resolved.suffix.lower()
        if suffix in {".csv", ".txt"}:
            sep = "\t" if suffix == ".txt" else ","
            return pd.read_csv(resolved, sep=sep)
        if suffix in {".tsv"}:
            return pd.read_csv(resolved, sep="\t")
        if suffix in {".parquet"}:
            return pd.read_parquet(resolved)
        if suffix in {".feather"}:
            return pd.read_feather(resolved)
        raise typer.BadParameter("Unsupported shares file format; use CSV, TSV, Parquet, or Feather.")

    windowing_step.Step().run(ctx)
    materialize_step.Step().run(ctx)

    panels = ctx.cache.get("panels", {})
    shares_df = panels.get("shares_member_df")
    if not isinstance(shares_df, pd.DataFrame) or shares_df.empty:
        typer.echo("shares_member_df not available after materialize step; ensure pipeline configuration is correct.")
        raise typer.Exit(code=1)
    return shares_df


def _load_dashboard_dataframe(path: Path) -> pd.DataFrame:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise typer.BadParameter(f"Dashboard export not found: {resolved}")
    suffix = resolved.suffix.lower()
    if suffix in {".csv"}:
        return pd.read_csv(resolved)
    if suffix in {".tsv", ".txt"}:
        return pd.read_csv(resolved, sep="\t")
    if suffix in {".parquet"}:
        return pd.read_parquet(resolved)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(resolved)
    raise typer.BadParameter("Unsupported dashboard format; use CSV, TSV, Excel, or Parquet.")


def _write_dataframe(path: Path, frame: Optional[pd.DataFrame]) -> None:
    if frame is None:
        frame_to_write = pd.DataFrame()
    elif getattr(frame, "empty", False):
        frame_to_write = frame.copy()
    else:
        frame_to_write = frame
    frame_to_write.to_csv(path, index=False)


def _frame_to_records(frame: Optional[pd.DataFrame]) -> list[Dict[str, Any]]:
    if isinstance(frame, pd.DataFrame) and not frame.empty:
        sanitized = frame.replace({pd.NA: None})
        return json.loads(sanitized.to_json(orient="records"))
    return []


def _to_serializable(data: Dict[str, Any]) -> Dict[str, Any]:
    serializable: Dict[str, Any] = {}
    for key, value in data.items():
        if value is pd.NA:
            serializable[key] = None
            continue
        if isinstance(value, (pd.Series, pd.Index)):
            serializable[key] = value.tolist()
        elif isinstance(value, (pd.DataFrame,)):
            serializable[key] = value.to_dict(orient="records")
        elif isinstance(value, (pd.Timestamp,)):
            serializable[key] = value.isoformat()
        elif isinstance(value, float) and math.isnan(value):
            serializable[key] = None
        elif isinstance(value, (np.integer, np.floating)):
            converted = value.item()
            if isinstance(converted, float) and math.isnan(converted):
                serializable[key] = None
            else:
                serializable[key] = converted
        else:
            serializable[key] = value
    return serializable


@app.command("reconcile-dashboard")
def reconcile_dashboard(
    dashboard_path: Path = typer.Argument(..., help="Path to the dashboard export (CSV, TSV, Excel, or Parquet)."),
    config: str = typer.Option("config/default.yaml", "--config", "-c", help="Pipeline config used to materialize panels when shares-path is not provided."),
    output_dir: Path = typer.Option(Path("recon"), help="Base directory (default `recon/`) where each run writes a timestamped folder."),
    shares_path: Optional[Path] = typer.Option(None, help="Optional path to a precomputed shares_member dataframe (CSV, TSV, Parquet, or Feather)."),
    category_map_path: Optional[Path] = typer.Option(None, help="Optional YAML mapping from dashboard categories to canonical PRD labels."),
    contract_mapping_path: Optional[Path] = typer.Option(
        DEFAULT_CONTRACT_MAPPING_PATH,
        "--contract-mapping-path",
        help="Optional CSV mapping contract numbers to canonical categories (defaults to repository reference file when present).",
    ),
    contract_number_column: Optional[str] = typer.Option(
        None,
        help="Optional dashboard column containing contract numbers (defaults to parsing from the category column).",
    ),
    spend_positive_only: bool = typer.Option(True, help="Restrict dashboard members to positive spend rows."),
    member_delta_threshold: float = typer.Option(5.0, help="Absolute member delta threshold for summary metrics."),
    overlap_threshold: float = typer.Option(0.5, help="Facility overlap threshold for summary metrics."),
    emit_intersection: bool = typer.Option(True, "--emit-intersection/--no-emit-intersection", help="Emit intersection CSV outputs."),
    status_column: str = typer.Option("System Status", help="Dashboard column containing workflow status."),
    required_status: str = typer.Option("PA-Completed", help="Status value required for inclusion."),
    category_column: str = typer.Option("Contract Category", help="Dashboard column containing category labels."),
    facility_column: str = typer.Option("Entity Code", help="Dashboard column containing facility identifiers."),
    spend_column: str = typer.Option("Category Spend", help="Dashboard column containing spend values."),
) -> None:
    """Reconcile Surpass PRD cohorts against a dashboard export and emit diagnostics."""

    ctx = make_context(config)
    repo_root = Path(ctx.paths["repo_root"]).resolve()

    shares_df = _load_shares_dataframe(ctx, shares_path)
    dashboard_df = _load_dashboard_dataframe(dashboard_path)
    category_map = load_category_map(category_map_path)
    contract_map = load_contract_number_mapping(contract_mapping_path)

    result = run_dashboard_reconciliation(
        shares_df,
        dashboard_df,
        category_map=category_map,
        contract_map=contract_map,
        contract_number_column=contract_number_column,
        status_column=status_column,
        required_status=required_status,
        category_column=category_column,
        facility_column=facility_column,
        spend_column=spend_column,
        spend_positive_only=spend_positive_only,
        emit_intersection=emit_intersection,
    )

    summary_metrics = compute_summary_metrics(
        result.members,
        member_delta_threshold=member_delta_threshold,
        overlap_threshold=overlap_threshold,
    )

    dashboard_resolved = dashboard_path.expanduser().resolve()
    shares_source = (
        "pipeline"
        if shares_path is None
        else str(shares_path.expanduser().resolve())
    )
    category_map_resolved = (
        str(category_map_path.expanduser().resolve()) if category_map_path is not None else None
    )
    if contract_mapping_path is not None:
        resolved_contract_mapping = contract_mapping_path.expanduser().resolve()
        contract_mapping_resolved = (
            str(resolved_contract_mapping) if resolved_contract_mapping.exists() else None
        )
    else:
        contract_mapping_resolved = None

    predicate = f"{status_column} == '{required_status}'"
    predicate += f" and {spend_column} {'>' if spend_positive_only else '>='} 0"

    notes = {
        "predicate": predicate,
        "dashboard_path": str(dashboard_resolved),
        "shares_source": shares_source,
        "category_map": category_map_resolved,
        "contract_mapping": contract_mapping_resolved,
        "contract_number_column": contract_number_column,
        "spend_positive_only": spend_positive_only,
        "emit_intersection": emit_intersection,
    }

    summary_markdown = render_summary_markdown(
        summary_metrics,
        mapping_counts=result.mapping_counts,
        overlap_summary=result.overlap_summary,
        notes=notes,
    )

    summary_payload: Dict[str, Any] = {
        "member_delta_threshold": summary_metrics["member_delta_threshold"],
        "overlap_threshold": summary_metrics["overlap_threshold"],
        "member_delta_gt_threshold_pct": summary_metrics["member_delta_gt_threshold_pct"],
        "overlap_lt_threshold_pct": summary_metrics["overlap_lt_threshold_pct"],
        "top_member_deltas": _frame_to_records(summary_metrics.get("top_member_deltas")),
        "top_spend_deltas": _frame_to_records(summary_metrics.get("top_spend_deltas")),
        "mapping_counts": _to_serializable(dict(result.mapping_counts)),
        "filter_counts": _to_serializable(dict(result.filter_counts)),
        "dashboard_stats": _to_serializable(dict(result.dashboard_stats)),
        "overlap_summary": _to_serializable(dict(result.overlap_summary)),
        "notes": notes,
    }

    base_output = output_dir if output_dir.is_absolute() else repo_root / output_dir
    base_output.mkdir(parents=True, exist_ok=True)
    run_dir = build_output_directory(base_output)

    members_path = run_dir / "members.csv"
    spend_path = run_dir / "spend.csv"
    members_intersection_path = run_dir / "members_intersection.csv"
    spend_intersection_path = run_dir / "spend_intersection.csv"
    mapped_categories_path = run_dir / "mapped_category_details.csv"
    unmapped_categories_path = run_dir / "unmapped_categories.csv"
    summary_md_path = run_dir / "summary.md"
    summary_json_path = run_dir / "summary.json"

    _write_dataframe(members_path, result.members)
    _write_dataframe(spend_path, result.spend)
    if emit_intersection:
        _write_dataframe(members_intersection_path, result.members_intersection)
        _write_dataframe(spend_intersection_path, result.spend_intersection)
    _write_dataframe(mapped_categories_path, result.mapped_category_details)
    _write_dataframe(unmapped_categories_path, result.unmapped_categories)
    summary_md_path.write_text(summary_markdown, encoding="utf-8")
    summary_json_path.write_text(json.dumps(summary_payload, indent=2, allow_nan=False), encoding="utf-8")

    def _rel(path: Path) -> str:
        try:
            return str(path.relative_to(repo_root))
        except ValueError:
            return str(path)

    members_intersection_rows = (
        int(len(result.members_intersection)) if emit_intersection and isinstance(result.members_intersection, pd.DataFrame) else 0
    )
    spend_intersection_rows = (
        int(len(result.spend_intersection)) if emit_intersection and isinstance(result.spend_intersection, pd.DataFrame) else 0
    )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "config": str(Path(config).expanduser().resolve()),
        "dashboard_path": str(dashboard_resolved),
        "shares_source": shares_source,
        "category_map": category_map_resolved,
        "contract_mapping": contract_mapping_resolved,
        "options": {
            "spend_positive_only": spend_positive_only,
            "member_delta_threshold": member_delta_threshold,
            "overlap_threshold": overlap_threshold,
            "emit_intersection": emit_intersection,
            "status_column": status_column,
            "required_status": required_status,
            "category_column": category_column,
            "facility_column": facility_column,
            "spend_column": spend_column,
            "contract_number_column": contract_number_column,
        },
        "counts": {
            "members_rows": int(len(result.members)),
            "spend_rows": int(len(result.spend)),
            "members_intersection_rows": members_intersection_rows,
            "spend_intersection_rows": spend_intersection_rows,
        },
        "filter_counts": _to_serializable(dict(result.filter_counts)),
        "mapping_counts": _to_serializable(dict(result.mapping_counts)),
        "dashboard_stats": _to_serializable(dict(result.dashboard_stats)),
        "overlap_summary": _to_serializable(dict(result.overlap_summary)),
        "files": {
            "members": _rel(members_path),
            "spend": _rel(spend_path),
            "members_intersection": _rel(members_intersection_path) if emit_intersection else None,
            "spend_intersection": _rel(spend_intersection_path) if emit_intersection else None,
            "mapped_category_details": _rel(mapped_categories_path),
            "unmapped_categories": _rel(unmapped_categories_path),
            "summary_markdown": _rel(summary_md_path),
            "summary_json": _rel(summary_json_path),
        },
    }

    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")

    typer.echo(
        "Dashboard reconciliation written to "
        f"{run_dir.relative_to(repo_root)} (members: {len(result.members)}, spend: {len(result.spend)})"
    )


@app.command("render-outline")
def render_outline_command(
    deck_vars: Path = typer.Argument(..., help="Path to deck_vars.json produced by the pipeline."),
    template: Path = typer.Option(
        Path("templates/executive_summary_outline.jinja2"),
        help="Jinja2 template to render.",
    ),
    output: Path = typer.Option(
        Path("outputs/executive_summary_outline.md"),
        help="Destination path for the rendered outline.",
    ),
) -> None:
    """Render the executive summary outline from deck_vars.json."""
    repo_root = Path.cwd()
    deck_path = deck_vars if deck_vars.is_absolute() else repo_root / deck_vars
    template_path = template if template.is_absolute() else repo_root / template
    output_path = output if output.is_absolute() else repo_root / output

    if not deck_path.exists():
        raise typer.BadParameter(f"deck_vars not found: {deck_path}")
    if not template_path.exists():
        raise typer.BadParameter(f"Template not found: {template_path}")

    rendered = outline_renderer(deck_path, template_path, output_path)
    typer.echo(f"Outline rendered to {output_path}")
    if rendered:
        typer.echo(f"Rendered length: {len(rendered)} characters")

@app.command()
def all(config: str = "config/default.yaml", no_charts: bool = False) -> None:
    """Run the full pipeline (optionally skipping chart generation)."""
    ctx = make_context(config)
    steps = [
        windowing_step.Step(),
        materialize_step.Step(),
        kpis_step.Step(),
        qa_step.Step(),
        export_step.Step(),
    ]
    if not no_charts:
        steps.append(charts_step.Step())
    steps.append(selector_step.Step())
    steps.append(outline_step.Step())
    run_pipeline(ctx, steps)


@app.command("run-all")
def run_all(
    config: str = typer.Option("config/default.yaml", help="Pipeline config YAML."),
    pipeline: bool = typer.Option(True, "--pipeline/--no-pipeline", help="Run the main analysis pipeline."),
    reconciliation: bool = typer.Option(False, "--reconciliation/--no-reconciliation", help="Run the reconciliation stage after the pipeline."),
    summary: bool = typer.Option(True, "--summary/--no-summary", help="Generate deck variables and outline."),
    deck: bool = typer.Option(True, "--deck/--no-deck", help="Build the PowerPoint deck."),
    no_charts: bool = typer.Option(False, help="Skip chart generation during the pipeline stage."),
    deck_template: Optional[Path] = typer.Option(None, help="Override deck template path."),
    deck_output: Optional[Path] = typer.Option(None, help="Override deck output path (supports {run_id})."),
    deck_style: Optional[Path] = typer.Option(None, help="Override deck style YAML."),
    outputs_dir: Optional[Path] = typer.Option(None, help="Optional base directory for consolidated outputs."),
    analytics_snapshot: Optional[Path] = typer.Option(
        None,
        help="Existing analytics snapshot directory to reuse when --pipeline is disabled.",
    ),
    recon_run: Optional[Path] = typer.Option(
        None,
        help="Existing reconciliation output directory to reuse when --reconciliation is disabled.",
    ),
) -> None:
    """Run configurable analytics, reconciliation, summary, and deck stages."""

    ctx = make_context(config)
    repo_root = Path(ctx.paths["repo_root"]).resolve()
    run_dir = Path(ctx.paths["run_dir"]).resolve()
    snapshots_root = Path(ctx.paths["snapshots_dir"]).resolve()

    analytics_snapshot = _coerce_optional_path(analytics_snapshot)
    recon_run = _coerce_optional_path(recon_run)

    executed_stages = {"pipeline": False, "reconciliation": False, "summary": False, "deck": False}
    analytics_dir: Optional[Path] = None
    recon_dir: Optional[Path] = None

    if pipeline:
        _run_pipeline_stage(ctx, include_charts=not no_charts)
        executed_stages["pipeline"] = True
        analytics_dir = Path(ctx.paths["run_dir"]).resolve()
    else:
        if not (summary or deck or reconciliation):
            typer.echo("No stages selected after disabling pipeline; nothing to do.")
        analytics_dir = _resolve_snapshot_dir_for_reuse(explicit=analytics_snapshot, snapshots_root=snapshots_root)
        _rebind_context_to_snapshot(ctx, analytics_dir)
        _hydrate_answers_from_snapshot(ctx, analytics_dir)
        run_dir = Path(ctx.paths["run_dir"]).resolve()
        typer.echo(f"Reusing analytics snapshot: {analytics_dir}")

    recon_manifest_path: Optional[Path] = None
    if reconciliation:
        recon_cfg = {}
        if isinstance(ctx.cfg, dict):
            recon_cfg = ctx.cfg.get("reports", {}).get("reconciliation", {}) or {}
        recon_cfg = dict(recon_cfg)
        if not executed_stages["pipeline"]:
            if analytics_dir is None:
                raise typer.BadParameter("Reconciliation stage requires analytics outputs. Provide --analytics-snapshot or enable --pipeline.")
            shares_candidate = analytics_dir / "shares_member.csv"
            if not shares_candidate.exists():
                raise typer.BadParameter(f"shares_member.csv not found in snapshot: {shares_candidate}")
            recon_cfg["shares_path"] = str(shares_candidate)
        if recon_run is not None:
            typer.echo("Warning: --recon-run ignored because reconciliation stage is running.")
        recon_manifest_path = _run_reconciliation_stage(ctx, repo_root, recon_cfg)
        executed_stages["reconciliation"] = True
        recon_dir = recon_manifest_path.parent if recon_manifest_path is not None else None
    else:
        recon_cfg = {}
        if isinstance(ctx.cfg, dict):
            recon_cfg = ctx.cfg.get("reports", {}).get("reconciliation", {}) or {}
        recon_base_raw = recon_cfg.get("output_dir", "recon")
        recon_base = _ensure_path(recon_base_raw, repo_root)
        # Only attempt to reuse reconciliation outputs when explicitly provided.
        # Summary/deck generation should not implicitly depend on reconciliation.
        if recon_run is not None:
            recon_dir = _resolve_reconciliation_dir_for_reuse(explicit=recon_run, recon_base=recon_base)
            recon_manifest_path = _hydrate_reconciliation_cache(ctx, recon_dir)
            if recon_manifest_path is None:
                candidate_manifest = recon_dir / "manifest.json"
                if candidate_manifest.exists():
                    ctx.cache["reconciliation_manifest"] = str(candidate_manifest)
                    recon_manifest_path = candidate_manifest
            typer.echo(f"Reusing reconciliation outputs: {recon_dir}")

    if summary:
        if not executed_stages["pipeline"] and not (run_dir / "prd_answers.csv").exists():
            raise typer.BadParameter("Summary stage requires pipeline outputs. Enable --pipeline or provide existing snapshot.")
        _run_summary_stage(ctx)
        executed_stages["summary"] = True

    deck_cfg: Optional[DeckRunConfig] = None
    deck_path: Optional[Path] = None
    if deck:
        if not (run_dir / "deck_vars.json").exists():
            raise typer.BadParameter("Deck generation requires deck_vars.json. Enable --summary or supply the file.")
        deck_cfg = _deck_config(ctx.cfg if isinstance(ctx.cfg, dict) else {}, repo_root, run_dir, deck_template, deck_output, deck_style)
        deck_path = Path(_run_deck_stage(deck_cfg)).resolve()
        executed_stages["deck"] = True

    outline_info = ctx.cache.get("outline", {}) if isinstance(ctx.cache.get("outline"), dict) else ctx.cache.get("outline")
    outline_path = None
    if isinstance(outline_info, dict):
        outline_path = outline_info.get("path")
    outline_path = Path(outline_path).resolve() if outline_path else None

    outputs_base = outputs_dir if outputs_dir is not None else (repo_root / "outputs")
    outputs_base = outputs_base.resolve()
    outputs_base.mkdir(parents=True, exist_ok=True)
    run_outputs_dir = outputs_base / ctx.run_id
    run_outputs_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, dict[str, Any]] = {}

    def _copy_artifact(path: Optional[Path], label: str) -> None:
        if not path or not path.exists():
            return
        target = run_outputs_dir / path.name
        shutil.copy2(path, target)
        artifacts[label] = {"path": str(target.relative_to(outputs_base)), "bytes": path.stat().st_size}

    deck_vars_path = run_dir / "deck_vars.json"
    if executed_stages["deck"] and deck_path is not None:
        _copy_artifact(deck_path, "deck")
    if executed_stages["summary"]:
        _copy_artifact(deck_vars_path, "deck_vars")
        if outline_path is not None:
            _copy_artifact(outline_path, "outline")
    if recon_manifest_path is not None:
        _copy_artifact(recon_manifest_path, "reconciliation_manifest")

    try:
        snapshots_rel = str(run_dir.relative_to(repo_root))
    except ValueError:
        snapshots_rel = str(run_dir)

    manifest = {
        "run_id": ctx.run_id,
        "config": str(Path(config).resolve()),
        "pipeline_elapsed_seconds": ctx.cache.get("pipeline_elapsed_seconds"),
        "artifacts": artifacts,
        "snapshots_dir": snapshots_rel,
        "outputs_dir": str(run_outputs_dir),
        "stages": executed_stages,
    }
    manifest_path = run_outputs_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    artifacts["manifest"] = {"path": str(manifest_path.relative_to(outputs_base)), "bytes": manifest_path.stat().st_size}

    if executed_stages["deck"] and deck_path is not None:
        typer.echo(f"Deck written to {deck_path}")
    if executed_stages["summary"] and outline_path:
        typer.echo(f"Outline rendered to {outline_path}")
    if executed_stages["reconciliation"] and recon_manifest_path:
        typer.echo(f"Reconciliation outputs written to {recon_manifest_path.parent}")
    typer.echo(f"Consolidated artifacts: {run_outputs_dir}")

@app.command()
def validate(
    baseline: str,
    candidate: str,
    tolerance: float = typer.Option(1e-6, help="Absolute tolerance for numeric fields."),
) -> None:
    """Compare two PRD answer exports and raise if they diverge."""

    result: ParityResult = compare_prd_answers(Path(baseline), Path(candidate), tolerance=tolerance)
    for line in result.report_lines():
        typer.echo(line)
    if not result.matched:
        raise typer.Exit(code=1)


@app.command()
def reconcile_surpass(
    config: str = typer.Option("config/default.yaml", help="Pipeline config used to materialize panels."),
    answers_path: Optional[Path] = typer.Option(None, help="Optional explicit path to prd_answers.csv."),
    output_dir: Path = typer.Option(Path("recon/surpass_reconciliation"), help="Directory for reconciliation exports."),
) -> None:
    """Rebuild Surpass measured-in-category member counts and spend comparisons."""

    ctx = make_context(config)
    windowing_step.Step().run(ctx)
    materialize_step.Step().run(ctx)

    panels = ctx.cache.get("panels", {})
    shares_df = panels.get("shares_member_df")
    if shares_df is None or getattr(shares_df, "empty", True):
        typer.echo("shares_member_df not available; ensure materialize step succeeded.")
        raise typer.Exit(code=1)

    facility_df = filter_measured_members(shares_df)
    if facility_df.empty:
        typer.echo("No Surpass measured-in-category facilities found at t0.")
        raise typer.Exit(code=1)
    category_summary = summarize_by_category(facility_df)

    resolved_answers = resolve_latest_prd_answers(
        snapshots_dir=Path(ctx.paths["repo_root"]) / "snapshots",
        explicit_path=answers_path,
    )
    prd_answers_df = pd.read_csv(resolved_answers)
    comparison = compare_to_prd(category_summary, prd_answers_df)

    repo_root = Path(ctx.paths["repo_root"])
    export_root = output_dir if output_dir.is_absolute() else repo_root / output_dir
    export_dir = build_output_directory(export_root)

    facility_path = export_dir / "facility_detail.csv"
    category_path = export_dir / "category_summary.csv"
    comparison_path = export_dir / "category_comparison.csv"

    facility_df.to_csv(facility_path, index=False)
    category_summary.to_csv(category_path, index=False)
    comparison.to_csv(comparison_path, index=False)

    manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "config": str(Path(config).resolve()),
        "answers_path": str(resolved_answers),
        "rows": {
            "facility_detail": len(facility_df),
            "category_summary": len(category_summary),
            "category_comparison": len(comparison),
        },
        "metrics": {
            "facility_ids": int(facility_df["facility_id"].nunique()),
            "categories": int(category_summary["category_id"].nunique()),
            "t0_spend_6m_total": float(category_summary["t0_spend_6m"].sum()),
            "delta_spend_abs_sum": float(comparison["delta_t0_spend_6m"].abs().sum()),
        },
        "files": {
            "facility_detail": str(facility_path.relative_to(repo_root)),
            "category_summary": str(category_path.relative_to(repo_root)),
            "category_comparison": str(comparison_path.relative_to(repo_root)),
        },
    }
    manifest_path = export_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    typer.echo(
        f"Reconciliation written to {export_dir.relative_to(ctx.paths['repo_root'])}. "
        f"Facility rows: {len(facility_df)}, categories: {len(category_summary)}"
    )


if __name__ == "__main__":
    app()
