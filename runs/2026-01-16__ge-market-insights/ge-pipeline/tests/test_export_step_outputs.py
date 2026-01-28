from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from src.runner.orchestrator import RunContext, run_pipeline
from src.steps import export_step


class _RecordingLogger:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def info(self, payload: dict[str, object]) -> None:
        self.events.append(payload)


class _DummyStep:
    def __init__(self, name: str, delay: float = 0.0) -> None:
        self.name = name
        self._delay = delay

    def run(self, ctx: RunContext) -> None:  # pragma: no cover - delay-only stub
        if self._delay:
            time.sleep(self._delay)


def _make_context(tmp_path: Path) -> RunContext:
    run_dir = tmp_path / "snapshots" / "test-run"
    result_dir = run_dir / "result_sheets"
    paths = {
        "run_dir": str(run_dir),
        "result_sheets_dir": str(result_dir),
        "repo_root": str(tmp_path),
        "config_path": str(tmp_path / "config.yaml"),
    }
    return RunContext(cfg={}, run_id="test-run", paths=paths, logger=_RecordingLogger())


def test_export_writes_shares_member_csv(tmp_path: Path) -> None:
    ctx = _make_context(tmp_path)
    run_dir = Path(ctx.paths["run_dir"])
    shares_df = pd.DataFrame(
        {
            "program_id": ["Surpass"],
            "category_id": ["Cat"],
            "facility_id": ["FAC123"],
            "event_month": [0],
            "member_at_t0": [True],
            "t0_total_cat_spend_6m": [123.45],
        }
    )
    ctx.cache["answers_df"] = pd.DataFrame({"program_id": ["Surpass"], "category_id": ["Cat"], "member_t0_total_spend_6m": [123.45]})
    ctx.cache["panels"] = {"shares_member_df": shares_df}

    export_step.Step().run(ctx)

    shares_path = run_dir / "shares_member.csv"
    assert shares_path.exists(), "shares_member.csv should be written to the snapshot directory"
    written = pd.read_csv(shares_path)
    assert len(written) == len(shares_df)
    assert set(written.columns) >= {"program_id", "category_id", "facility_id", "event_month"}
    artifacts = ctx.cache["export"]["artifacts"]
    assert "shares_member.csv" in artifacts
    assert artifacts["shares_member.csv"]["rows"] == len(shares_df)


def test_run_pipeline_records_step_durations(tmp_path: Path) -> None:
    ctx = _make_context(tmp_path)
    logger = ctx.logger  # type: ignore[assignment]

    steps = [_DummyStep("alpha", delay=0.01), _DummyStep("beta", delay=0.01)]
    run_pipeline(ctx, steps)  # type: ignore[arg-type]

    assert "step_durations" in ctx.cache
    durations = ctx.cache["step_durations"]
    assert set(durations.keys()) == {"alpha", "beta"}
    assert all(value >= 0 for value in durations.values())
    assert ctx.cache["pipeline_elapsed_seconds"] >= sum(durations.values())

    pipeline_events = [event for event in logger.events if event.get("event") == "pipeline_complete"]
    assert pipeline_events, "pipeline_complete event should be logged"
    complete_event = pipeline_events[-1]
    assert set(complete_event["step_durations"].keys()) == {"alpha", "beta"}
    assert complete_event["elapsed_seconds"] >= sum(durations.values())


def test_run_pipeline_emits_progress_events(tmp_path: Path) -> None:
    ctx = _make_context(tmp_path)
    logger = ctx.logger  # type: ignore[assignment]

    steps = [_DummyStep("long", delay=0.05)]
    run_pipeline(ctx, steps, progress_interval_seconds=0.01)  # type: ignore[arg-type]

    progress_events = [event for event in logger.events if event.get("event") == "pipeline_progress"]
    assert progress_events, "Expected at least one periodic progress log"
    for event in progress_events:
        assert event.get("elapsed_seconds") is not None
        assert event.get("current_step") == "long"
