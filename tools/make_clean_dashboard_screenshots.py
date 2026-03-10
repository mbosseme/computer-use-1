from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from agent_tools.images.dashboard_crop import DashboardCropConfig, autocrop_dashboard_content


def _iter_inputs(input_paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in input_paths:
        p = Path(raw)
        if any(ch in raw for ch in ["*", "?", "["]):
            out.extend(Path().glob(raw))
        elif p.is_dir():
            out.extend(sorted(p.glob("*.png")))
        else:
            out.append(p)
    # De-dupe while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in out:
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        unique.append(p)
    return unique


def main() -> None:
    ap = argparse.ArgumentParser(description="Auto-crop BI dashboard screenshots to remove empty gutters.")
    ap.add_argument(
        "inputs",
        nargs="+",
        help="One or more files/dirs/globs. Dirs default to *.png.",
    )
    ap.add_argument(
        "--suffix",
        default="_clean",
        help="Suffix for output files (default: _clean).",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output files if they already exist.",
    )
    ap.add_argument("--white-threshold", type=int, default=DashboardCropConfig.white_threshold)
    ap.add_argument("--empty-fraction", type=float, default=DashboardCropConfig.empty_fraction)
    ap.add_argument("--padding", type=int, default=DashboardCropConfig.padding)

    args = ap.parse_args()

    cfg = DashboardCropConfig(
        white_threshold=int(args.white_threshold),
        empty_fraction=float(args.empty_fraction),
        padding=int(args.padding),
    )

    targets = _iter_inputs(args.inputs)
    if not targets:
        raise SystemExit("No input files matched.")

    wrote = 0
    for src in targets:
        if not src.exists():
            print(f"SKIP missing: {src}")
            continue

        dst = src.with_name(src.stem + str(args.suffix) + src.suffix)
        if dst.exists() and not args.overwrite:
            print(f"SKIP exists (use --overwrite): {dst}")
            continue

        with Image.open(src) as im:
            cleaned = autocrop_dashboard_content(im, cfg)
            cleaned.save(dst)

        wrote += 1
        print(f"WROTE: {dst}")

    print(f"Done. Wrote {wrote} file(s).")


if __name__ == "__main__":
    main()
