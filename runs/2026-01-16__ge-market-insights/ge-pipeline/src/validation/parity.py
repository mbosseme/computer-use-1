from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

KEY_COLUMNS: tuple[str, str] = ("program_id", "category_id")


@dataclass
class ParityResult:
    """Summary of parity comparison between two PRD answers tables."""

    matched: bool
    row_count_diff: int
    missing_keys: list[tuple[str, str]] = field(default_factory=list)
    extra_keys: list[tuple[str, str]] = field(default_factory=list)
    numeric_max_diff: dict[str, float] = field(default_factory=dict)
    categorical_mismatches: dict[str, list[tuple[str, str]]] = field(default_factory=dict)

    def report_lines(self) -> list[str]:
        lines = [
            f"matched={self.matched}",
            f"row_count_diff={self.row_count_diff}",
        ]
        if self.missing_keys:
            lines.append(f"missing_keys={len(self.missing_keys)}")
        if self.extra_keys:
            lines.append(f"extra_keys={len(self.extra_keys)}")
        if self.numeric_max_diff:
            formatted = ", ".join(f"{col}: {diff:.6g}" for col, diff in self.numeric_max_diff.items())
            lines.append(f"numeric_max_diff={{{formatted}}}")
        if self.categorical_mismatches:
            formatted = ", ".join(f"{col}: {len(rows)}" for col, rows in self.categorical_mismatches.items())
            lines.append(f"categorical_mismatches={{{formatted}}}")
        return lines

    def raise_if_failed(self) -> None:
        if not self.matched:
            details = " ; ".join(self.report_lines())
            raise ValueError(f"Parity validation failed: {details}")


def _load_prd_answers(path: Path) -> pd.DataFrame:
    csv_path = path
    if csv_path.is_dir():
        csv_path = csv_path / "prd_answers.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Expected prd_answers.csv at {csv_path}")
    df = pd.read_csv(csv_path)
    if not all(col in df.columns for col in KEY_COLUMNS):
        raise ValueError(f"prd_answers.csv at {csv_path} missing key columns {KEY_COLUMNS}")
    return df


def _numeric_columns(df: pd.DataFrame, ignore: Iterable[str]) -> list[str]:
    numeric_cols: list[str] = []
    for col in df.columns:
        if col in ignore:
            continue
        series = df[col]
        if is_numeric_dtype(series) and not is_bool_dtype(series):
            numeric_cols.append(col)
    return numeric_cols


def compare_prd_answers(
    baseline: Path,
    candidate: Path,
    *,
    tolerance: float = 1e-6,
) -> ParityResult:
    """Compare two PRD answers CSVs and return a summary of differences."""

    baseline_df = _load_prd_answers(Path(baseline))
    candidate_df = _load_prd_answers(Path(candidate))

    baseline_df = baseline_df.copy()
    candidate_df = candidate_df.copy()

    # Normalize column ordering
    candidate_df = candidate_df.loc[:, baseline_df.columns]

    baseline_df.set_index(list(KEY_COLUMNS), inplace=True)
    candidate_df.set_index(list(KEY_COLUMNS), inplace=True)

    missing_keys = sorted(set(baseline_df.index) - set(candidate_df.index))
    extra_keys = sorted(set(candidate_df.index) - set(baseline_df.index))

    common_index = baseline_df.index.intersection(candidate_df.index)
    row_count_diff = candidate_df.shape[0] - baseline_df.shape[0]

    numeric_cols = _numeric_columns(baseline_df.reset_index(), KEY_COLUMNS)
    numeric_diff: dict[str, float] = {}
    for col in numeric_cols:
        if col not in candidate_df.columns:
            continue
        base_series = baseline_df.loc[common_index, col]
        cand_series = candidate_df.loc[common_index, col]
        # Align index order
        cand_series = cand_series.reindex(base_series.index)
        diff = (cand_series - base_series).abs().max()
        numeric_diff[col] = float(diff if pd.notna(diff) else 0.0)

    categorical_mismatch: dict[str, list[tuple[str, str]]] = {}
    categorical_cols = [col for col in baseline_df.columns if col not in numeric_cols]
    for col in categorical_cols:
        if col not in candidate_df.columns:
            continue
        base_values = baseline_df.loc[common_index, col]
        cand_values = candidate_df.loc[common_index, col].reindex(base_values.index)
        mismatch_mask = (base_values.fillna("<NA>") != cand_values.fillna("<NA>"))
        if mismatch_mask.any():
            mismatch_coords = [tuple(idx) for idx in base_values.index[mismatch_mask]]
            categorical_mismatch[col] = mismatch_coords

    max_numeric_diff = max(numeric_diff.values(), default=0.0)
    matched = (
        row_count_diff == 0
        and not missing_keys
        and not extra_keys
        and max_numeric_diff <= tolerance
        and not categorical_mismatch
    )

    return ParityResult(
        matched=matched,
        row_count_diff=row_count_diff,
        missing_keys=list(missing_keys),
        extra_keys=list(extra_keys),
        numeric_max_diff={col: diff for col, diff in numeric_diff.items() if diff > tolerance},
        categorical_mismatches=categorical_mismatch,
    )
