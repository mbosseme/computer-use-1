#!/usr/bin/env python3
"""Scan git worktrees and produce a categorized registry for the orchestrator.

Usage:
    python -m runs.2026-03-02__orchestrator.scripts.scan_worktrees [--output FILE]

Outputs a JSON array of worktree metadata including:
- path, branch, slug (from directory name)
- category (inferred from slug keywords)
- has_handoff (whether a HANDOFF.md exists in the run directory)
- last_modified (most recent file modification in the worktree's run dir)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# Category keywords → category label
_CATEGORY_KEYWORDS = {
    "client": [
        "baxter", "solventum", "ge-market", "b-braun", "viberon",
        "mckinsey", "fda-cdrh",
    ],
    "strategy": [
        "premier-strategy", "portfolio-expansion", "orchestrator",
    ],
    "people": [
        "employee-performance", "accelerating_technology_delivery",
    ],
    "operations": [
        "timesheets", "o365-outlook", "onenote",
    ],
    "personal": [
        "disney", "personal-finance", "personal-shopping",
        "second-home", "465-attic", "tiller-transaction",
        "nc-preschool",
    ],
    "core": [
        "playwright-general", "doc-synthesis", "batch-research",
        "playwright-robustness", "validate_insight",
    ],
    "research": [
        "research",
    ],
}


def _categorize(slug: str) -> str:
    slug_lower = slug.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in slug_lower:
                return category
    return "other"


def _extract_slug(path: str) -> str:
    """Extract the slug from a worktree directory name like wt-2026-01-22__baxter-market-insights."""
    dirname = os.path.basename(path)
    # Strip wt- prefix and date
    match = re.match(r"wt-\d{4}-\d{2}-\d{2}__(.+)", dirname)
    if match:
        return match.group(1)
    match = re.match(r"wt-core-\d{4}-\d{2}-\d{2}__(.+)", dirname)
    if match:
        return f"core/{match.group(1)}"
    return dirname


def _find_handoff(wt_path: str) -> Optional[str]:
    """Look for a HANDOFF.md in the worktree's run directory."""
    runs_dir = Path(wt_path) / "runs"
    if not runs_dir.exists():
        return None
    for run_dir in sorted(runs_dir.iterdir(), reverse=True):
        handoff = run_dir / "HANDOFF.md"
        if handoff.exists():
            return str(handoff)
    return None


def _last_modified_in(directory: str) -> Optional[str]:
    """Find the most recently modified file in a directory tree."""
    latest = 0.0
    dir_path = Path(directory)
    if not dir_path.exists():
        return None
    for f in dir_path.rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            try:
                mtime = f.stat().st_mtime
                if mtime > latest:
                    latest = mtime
            except OSError:
                pass
    if latest > 0:
        return datetime.fromtimestamp(latest).isoformat()[:19]
    return None


def scan_worktrees() -> List[Dict[str, Any]]:
    """Scan all git worktrees from the current repo."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True, text=True, check=True,
        cwd=str(Path(__file__).resolve().parents[3]),
    )

    worktrees: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {}

    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "")
        elif line.startswith("HEAD "):
            current["head"] = line.split(" ", 1)[1][:8]
        elif line == "bare":
            current["bare"] = True

    if current:
        worktrees.append(current)

    # Enrich each worktree
    enriched = []
    for wt in worktrees:
        path = wt.get("path", "")
        if wt.get("bare"):
            continue

        slug = _extract_slug(path)
        category = _categorize(slug)
        handoff = _find_handoff(path)

        # Look for last activity in runs/ dir
        runs_dir = Path(path) / "runs"
        last_mod = None
        if runs_dir.exists():
            for run_dir in sorted(runs_dir.iterdir(), reverse=True):
                if run_dir.is_dir() and run_dir.name != "README.md":
                    last_mod = _last_modified_in(str(run_dir))
                    break

        enriched.append({
            "slug": slug,
            "category": category,
            "path": path,
            "branch": wt.get("branch", ""),
            "has_handoff": handoff is not None,
            "handoff_path": handoff,
            "last_activity": last_mod,
        })

    # Sort: most recently active first
    enriched.sort(key=lambda x: x.get("last_activity") or "", reverse=True)
    return enriched


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan worktrees for orchestrator registry")
    parser.add_argument("--output", "-o", type=str, default=None)
    args = parser.parse_args()

    worktrees = scan_worktrees()

    output = json.dumps(worktrees, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Found {len(worktrees)} worktrees → {args.output}", file=sys.stderr)
    else:
        print(output)

    # Print summary to stderr
    categories: Dict[str, int] = {}
    for wt in worktrees:
        cat = wt["category"]
        categories[cat] = categories.get(cat, 0) + 1
    print(f"\nSummary: {len(worktrees)} worktrees", file=sys.stderr)
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}", file=sys.stderr)


if __name__ == "__main__":
    main()
