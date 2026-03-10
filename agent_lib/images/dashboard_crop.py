from __future__ import annotations

from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True)
class DashboardCropConfig:
    """Heuristics tuned for BI dashboard screenshots with large white gutters."""

    white_threshold: int = 245  # per-channel; >= means "background-like"
    padding: int = 10

    # When estimating empty columns/rows, how empty is "empty"?
    empty_fraction: float = 0.995

    # Find the first y where we see "canvas" (mostly white) for N consecutive rows.
    canvas_white_fraction: float = 0.85
    canvas_consecutive_rows: int = 8

    # Ignore top chrome when trimming left/right (prevents full-width toolbars from
    # forcing the crop to remain at the original width).
    trim_x_start_y_px: int = 165

    # Also avoid including browser chrome at the very top.
    min_top_px: int = 110

    # Keep a bit of header above the detected canvas start.
    header_slop_px: int = 70


def _row_white_fraction(px, w: int, y: int, thr: int) -> float:
    white = 0
    for x in range(w):
        r, g, b = px[x, y]
        if r >= thr and g >= thr and b >= thr:
            white += 1
    return white / float(w)


def _col_white_fraction(px, x: int, y0: int, y1: int, thr: int) -> float:
    white = 0
    total = max(1, (y1 - y0))
    for y in range(y0, y1):
        r, g, b = px[x, y]
        if r >= thr and g >= thr and b >= thr:
            white += 1
    return white / float(total)


def _find_canvas_start_y(px, w: int, h: int, cfg: DashboardCropConfig) -> int:
    thr = cfg.white_threshold
    need = cfg.canvas_consecutive_rows
    good = 0
    for y in range(h):
        if _row_white_fraction(px, w, y, thr) >= cfg.canvas_white_fraction:
            good += 1
            if good >= need:
                return max(0, y - need + 1)
        else:
            good = 0

    # Fallback: if we can't detect the canvas reliably, just skip a bit of chrome.
    return min(h - 1, max(0, int(h * 0.12)))


def autocrop_dashboard_content(img: Image.Image, cfg: DashboardCropConfig | None = None) -> Image.Image:
    """Crop a screenshot to focus on dashboard content.

    Why this exists:
    - Tableau-like screenshots often have full-width browser/app chrome across the top.
    - A naive "non-white bbox" crop will keep full width due to that chrome,
      leaving a huge white gutter on the right.

    This function:
    - Detects the start of the dashboard canvas (mostly white)
    - Trims left/right based on content within the canvas region (skipping top chrome)
    - Trims bottom based on the trimmed x-range
    """

    cfg = cfg or DashboardCropConfig()

    rgb = img.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    if px is None:
        # Very defensive: PIL should provide a PixelAccess for RGB images.
        return img

    thr = cfg.white_threshold
    canvas_y0 = _find_canvas_start_y(px, w, h, cfg)

    y0 = min(h - 1, canvas_y0)
    y1 = h
    y0_x = min(h - 1, max(y0, cfg.trim_x_start_y_px))

    # Left/right bounds by trimming columns that are (almost) entirely white.
    left = 0
    for x in range(w):
        if _col_white_fraction(px, x, y0_x, y1, thr) < cfg.empty_fraction:
            left = x
            break

    right = w - 1
    for x in range(w - 1, -1, -1):
        if _col_white_fraction(px, x, y0_x, y1, thr) < cfg.empty_fraction:
            right = x
            break

    # Top/bottom bounds.
    top = max(0, y0_x - cfg.header_slop_px)
    top = max(top, cfg.min_top_px)

    bottom = h - 1
    for y in range(h - 1, y0_x - 1, -1):
        white = 0
        span = max(1, (right - left + 1))
        for x in range(left, right + 1):
            r, g, b = px[x, y]
            if r >= thr and g >= thr and b >= thr:
                white += 1
        if (white / float(span)) < cfg.empty_fraction:
            bottom = y
            break

    # Safety fallback.
    if right <= left or bottom <= top:
        return img

    pad = cfg.padding
    crop_left = max(0, left - pad)
    crop_top = max(0, top - pad)
    crop_right = min(w, right + pad + 1)
    crop_bottom = min(h, bottom + pad + 1)

    return img.crop((crop_left, crop_top, crop_right, crop_bottom))
