from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INCLUDE_EXTS = {".pdf", ".docx", ".eml", ".txt", ".md"}


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\.[a-z0-9]{1,6}$", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "document"


def _stable_id(rel_path: str, *, length: int = 10) -> str:
    h = hashlib.sha1(rel_path.encode("utf-8"))
    return h.hexdigest()[:length]


@dataclass(frozen=True)
class MappedFile:
    rel_path: str
    src_path: str
    dst_name: str


def _iter_source_files(source_root: Path) -> Iterable[Path]:
    for p in sorted(source_root.rglob("*")):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.suffix.lower() not in INCLUDE_EXTS:
            continue
        yield p


def _ensure_symlink(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        if src.exists() and dst.exists() and src.samefile(dst):
            return
    except OSError:
        pass

    if dst.exists() or dst.is_symlink():
        dst.unlink()
    os.symlink(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a run-local symlink mirror of a source folder (recursive) into a flat directory, "
            "with stable, collision-resistant filenames derived from relative paths."
        )
    )
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--map-json", required=True, type=Path)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing files in out-dir before mirroring",
    )

    args = parser.parse_args()

    source_root: Path = args.source_root
    out_dir: Path = args.out_dir
    map_json: Path = args.map_json

    if not source_root.exists() or not source_root.is_dir():
        raise SystemExit(f"Not a directory: {source_root}")

    out_dir.mkdir(parents=True, exist_ok=True)
    map_json.parent.mkdir(parents=True, exist_ok=True)

    if args.clean:
        for existing in out_dir.iterdir():
            if existing.is_file() or existing.is_symlink():
                existing.unlink()

    mapped: list[MappedFile] = []

    for src in _iter_source_files(source_root):
        rel_path = src.relative_to(source_root).as_posix()
        sid = _stable_id(rel_path)
        slug = _slugify(src.name)
        dst_name = f"{slug}__{sid}{src.suffix.lower()}"
        dst = out_dir / dst_name

        _ensure_symlink(src, dst)
        mapped.append(MappedFile(rel_path=rel_path, src_path=str(src), dst_name=dst_name))

    data = {
        "source_root": str(source_root),
        "out_dir": str(out_dir),
        "files": [m.__dict__ for m in mapped],
    }
    map_json.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Mirrored files: {len(mapped)}")
    print(f"Wrote map: {map_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
