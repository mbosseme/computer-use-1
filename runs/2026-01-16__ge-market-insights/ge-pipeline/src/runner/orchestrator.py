"""Lightweight pipeline orchestration primitives."""
from __future__ import annotations

import threading
import time

from dataclasses import dataclass, field
from typing import Any, Dict, Protocol


@dataclass
class RunContext:
    """Runtime context shared across pipeline steps."""

    cfg: Dict[str, Any]
    run_id: str
    paths: Dict[str, str]
    logger: Any
    cache: Dict[str, Any] = field(default_factory=dict)


class Step(Protocol):
    """Protocol for pipeline steps."""

    name: str

    def run(self, ctx: RunContext) -> None:
        """Execute the step, mutating the run context as needed."""


def run_pipeline(
    ctx: RunContext,
    steps: list[Step],
    *,
    progress_interval_seconds: float = 60.0,
) -> None:
    """Execute each step in order, emitting structured logs."""

    pipeline_started = time.perf_counter()
    durations: Dict[str, float] = {}
    ctx.cache["current_step"] = None

    stop_event = threading.Event()

    def _progress_loop() -> None:
        if progress_interval_seconds <= 0:
            return
        while not stop_event.wait(progress_interval_seconds):
            elapsed = time.perf_counter() - pipeline_started
            ctx.logger.info(
                {
                    "event": "pipeline_progress",
                    "elapsed_seconds": elapsed,
                    "current_step": ctx.cache.get("current_step"),
                }
            )

    progress_thread: threading.Thread | None = None
    if progress_interval_seconds > 0:
        progress_thread = threading.Thread(target=_progress_loop, name="pipeline-progress", daemon=True)
        progress_thread.start()

    try:
        for step in steps:
            ctx.cache["current_step"] = step.name
            ctx.logger.info({"event": "step_start", "step": step.name})
            step_started = time.perf_counter()
            step.run(ctx)
            step_elapsed = time.perf_counter() - step_started
            durations[step.name] = step_elapsed
            ctx.logger.info({"event": "step_end", "step": step.name, "elapsed_seconds": step_elapsed})
    finally:
        stop_event.set()
        if progress_thread is not None:
            progress_thread.join(timeout=max(progress_interval_seconds, 1.0))
        ctx.cache["current_step"] = None

    pipeline_elapsed = time.perf_counter() - pipeline_started
    ctx.logger.info(
        {
            "event": "pipeline_complete",
            "steps": len(steps),
            "elapsed_seconds": pipeline_elapsed,
            "step_durations": durations,
        }
    )
    ctx.cache["step_durations"] = durations
    ctx.cache["pipeline_elapsed_seconds"] = pipeline_elapsed
