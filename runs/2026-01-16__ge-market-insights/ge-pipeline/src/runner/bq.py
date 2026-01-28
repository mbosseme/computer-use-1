"""BigQuery helper utilities (ADC-first)."""
from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, Any, Dict, Sequence

import pandas as pd

try:  # pragma: no cover - optional import guard for dependency-light environments
    from google.cloud import bigquery
except Exception:  # pragma: no cover
    bigquery = None  # type: ignore

if TYPE_CHECKING:  # pragma: no cover - static typing support only
    from google.cloud import bigquery as _bq_mod

    _ClientT = _bq_mod.Client
    _ScalarParamT = _bq_mod.ScalarQueryParameter
    _QueryJobConfigT = _bq_mod.QueryJobConfig
else:  # pragma: no cover - runtime fallback to Any
    _ClientT = Any  # type: ignore[assignment]
    _ScalarParamT = Any  # type: ignore[assignment]
    _QueryJobConfigT = Any  # type: ignore[assignment]

_CLIENT: _ClientT | None = None


def _require_bigquery() -> None:
    if bigquery is None:
        raise RuntimeError(
            "google-cloud-bigquery is required. Install dependencies from requirements.txt"
        )


def _get_client() -> _ClientT:
    _require_bigquery()
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    assert bigquery is not None  # narrow for type checkers
    project_id = (
        os.getenv("BIGQUERY_PROJECT_ID")
        or os.getenv("BIGQUERY_PROJECT")
        or os.getenv("VERTEX_AI_PROJECT")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or None
    )
    try:
        _CLIENT = bigquery.Client(project=project_id)
    except Exception as exc:  # pragma: no cover - network/auth failure path
        raise RuntimeError(
            "Failed to initialize BigQuery client; ensure ADC auth is configured."
        ) from exc
    return _CLIENT


def render_sql(template: str, params: Dict[str, Any]) -> str:
    """Render SQL template using Python ``format`` style parameters."""
    return template.format(**params)


def _job_config(parameters: Sequence[_ScalarParamT] | None) -> _QueryJobConfigT:
    _require_bigquery()
    assert bigquery is not None  # narrow for type checkers
    if not parameters:
        return bigquery.QueryJobConfig()
    return bigquery.QueryJobConfig(query_parameters=list(parameters))


def query_df(
    sql: str,
    *,
    parameters: Sequence[_ScalarParamT] | None = None,
    max_retries: int = 3,
    retry_wait_seconds: float = 3.0,
) -> pd.DataFrame:
    """Execute SQL and return a pandas DataFrame with basic retries."""

    client = _get_client()
    attempt = 0
    last_exc: Exception | None = None
    while attempt < max_retries:
        attempt += 1
        try:
            job = client.query(sql, job_config=_job_config(parameters))
            return job.result().to_dataframe(create_bqstorage_client=False)
        except Exception as exc:  # pragma: no cover - network failure path
            last_exc = exc
            if attempt >= max_retries:
                break
            time.sleep(retry_wait_seconds)
    raise RuntimeError(f"BigQuery query failed after {max_retries} attempts: {last_exc}")
