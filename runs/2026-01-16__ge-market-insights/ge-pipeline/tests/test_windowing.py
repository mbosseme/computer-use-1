from datetime import datetime, timezone

from src.windowing import compute_analysis_window


def test_compute_analysis_window_fixed_now():
    # Fixed "now" = 2025-09-18 UTC (>= 15th, so include prior month)
    now = datetime(2025, 9, 18, tzinfo=timezone.utc)
    w = compute_analysis_window(now)
    # Prior month (August) is eligible
    assert w.data_cutoff_month == "2025-08"
    # Core is 35 months ending at 2025-08 -> start at 2022-10
    assert w.core_start == "2022-10"
    assert w.core_end == "2025-08"
    # Pre buffer 12 months before 2022-10 -> 2021-10
    assert w.pre_start == "2021-10"
    # Post buffer 18 months after 2025-08 -> 2027-02
    assert w.post_end == "2027-02"


def test_compute_analysis_window_before_cutoff_day():
    # Fixed "now" = 2025-09-05 UTC (< 15th, so skip prior month)
    now = datetime(2025, 9, 5, tzinfo=timezone.utc)
    w = compute_analysis_window(now)
    assert w.data_cutoff_month == "2025-07"
