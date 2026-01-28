"""I/O utilities for reading and writing pipeline artifacts."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def ensure_dir(path: str | Path) -> Path:
    """Ensure the directory exists and return a :class:`Path`."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def list_files(path: str | Path) -> list[Path]:
    """Return a sorted list of files within *path*."""
    p = Path(path)
    if not p.exists():
        return []
    return sorted([f for f in p.iterdir() if f.is_file()])
