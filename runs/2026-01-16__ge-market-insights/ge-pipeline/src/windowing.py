"""
Dynamic analysis window helpers aligned to PRD §2b.

Computes:
- CURRENT_MONTH: calendar month at runtime (UTC by default)
- DATA_CUTOFF_MONTH: latest month with complete transactions (never current month; prior month only after the 15th)
- CORE_START/CORE_END (35-month core)
- PRE_START (CORE_START - 6 months), POST_END (CORE_END + 18 months)

Returns YYYY-MM strings for easy parameterization of SQL (@START_MONTH, @END_MONTH)
and notebook parameters.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Dict, Optional


def _to_first_of_month(d: date) -> date:
    return date(d.year, d.month, 1)


def _shift_months(d: date, delta: int) -> date:
    """Shift date by delta months, clamping to first of month.

    Example: 2025-09-18, -2 -> 2025-07-01
    """
    y = d.year + (d.month - 1 + delta) // 12
    m = (d.month - 1 + delta) % 12 + 1
    return date(y, m, 1)


def _ym_str(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


@dataclass(frozen=True)
class AnalysisWindow:
    current_month: str
    data_cutoff_month: str
    core_start: str
    core_end: str
    pre_start: str
    post_end: str

    def as_params(self) -> Dict[str, str]:
        """Convenience mapping for BigQuery parameters and notebook vars."""
        return {
            "CURRENT_MONTH": self.current_month,
            "DATA_CUTOFF_MONTH": self.data_cutoff_month,
            # For SQL read range
            "START_MONTH": self.pre_start,
            "END_MONTH": self.post_end,
            # Optionally expose core window
            "CORE_START": self.core_start,
            "CORE_END": self.core_end,
        }


def compute_analysis_window(now_utc: Optional[datetime] = None) -> AnalysisWindow:
    """Compute PRD-aligned analysis window given 'now' (UTC by default).

    - CURRENT_MONTH = month of 'now'
    - DATA_CUTOFF_MONTH:
        * never includes the current calendar month
        * includes the prior month only when today is the 15th or later
        * otherwise falls back to two months prior
    - CORE window = 35 months ending at DATA_CUTOFF_MONTH
    - PRE buffer = 12 months before CORE_START
    - POST buffer = 18 months after CORE_END

    Returns months as YYYY-MM strings.
    """
    now = now_utc or datetime.now(timezone.utc)
    cur_month = _to_first_of_month(now.date())
    prev_month = _shift_months(cur_month, -1)
    two_months_prior = _shift_months(cur_month, -2)

    if now.day >= 15:
        cutoff_month = prev_month
    else:
        cutoff_month = two_months_prior

    core_end = cutoff_month
    core_start = _shift_months(core_end, -34)  # inclusive span of 35 months
    pre_start = _shift_months(core_start, -12)
    post_end = _shift_months(core_end, +18)

    return AnalysisWindow(
        current_month=_ym_str(cur_month),
        data_cutoff_month=_ym_str(cutoff_month),
        core_start=_ym_str(core_start),
        core_end=_ym_str(core_end),
        pre_start=_ym_str(pre_start),
        post_end=_ym_str(post_end),
    )


__all__ = [
    "AnalysisWindow",
    "compute_analysis_window",
]
