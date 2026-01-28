#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.llm.document_extraction import sanitize_text


@dataclass(frozen=True)
class StagedDoc:
    source_path: str
    staged_path: str
    kind: str
    note: Optional[str] = None


def _run_textutil_docx_to_text(docx_path: Path) -> str:
    # macOS built-in tool; yields plain text for Office docs in many cases.
    result = subprocess.run(
        ["/usr/bin/textutil", "-convert", "txt", "-stdout", str(docx_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "textutil failed (exit={code}): {stderr}".format(
                code=result.returncode,
                stderr=(result.stderr.decode("utf-8", errors="replace")[:2000]),
            )
        )
    return result.stdout.decode("utf-8", errors="replace")


def stage_ge_docs(*, src_dir: Path, dst_dir: Path) -> dict:
    if not src_dir.exists() or not src_dir.is_dir():
        raise RuntimeError(f"Not a directory: {src_dir}")

    dst_dir.mkdir(parents=True, exist_ok=True)

    include_exts = {".pdf", ".eml", ".txt", ".md", ".docx"}
    staged: list[StagedDoc] = []
    skipped: list[str] = []
    errors: list[str] = []

    for path in sorted(src_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            skipped.append(str(path))
            continue

        ext = path.suffix.lower()
        if ext not in include_exts:
            skipped.append(str(path))
            continue

        try:
            if ext == ".docx":
                text = _run_textutil_docx_to_text(path)
                text = sanitize_text(text)

                out_name = f"{path.stem}.txt"
                out_path = dst_dir / out_name
                out_path.write_text(
                    "\n".join(
                        [
                            f"# Extracted from DOCX: {path.name}",
                            f"# Generated: {datetime.now().isoformat(timespec='seconds')}",
                            "",
                            text.strip(),
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
                staged.append(
                    StagedDoc(
                        source_path=str(path),
                        staged_path=str(out_path),
                        kind="docx->txt",
                    )
                )
            else:
                out_path = dst_dir / path.name

                # Prefer symlinks for large files to avoid duplicating OneDrive content.
                if out_path.exists():
                    out_path.unlink()

                os.symlink(path, out_path)
                staged.append(
                    StagedDoc(
                        source_path=str(path),
                        staged_path=str(out_path),
                        kind=ext.lstrip("."),
                        note="symlink",
                    )
                )
        except Exception as e:
            errors.append(f"{path}: {e}")

    manifest = {
        "generated_on": datetime.now().isoformat(timespec="seconds"),
        "source_dir": str(src_dir),
        "staging_dir": str(dst_dir),
        "staged": [asdict(s) for s in staged],
        "skipped": skipped,
        "errors": errors,
    }

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage GE docs for synthesis (symlink PDFs, convert DOCX to TXT)")
    parser.add_argument("--src", required=True, help="Source folder")
    parser.add_argument("--dst", required=True, help="Destination staging folder")
    parser.add_argument("--manifest", required=True, help="Output manifest JSON path")

    args = parser.parse_args()
    src_dir = Path(args.src)
    dst_dir = Path(args.dst)
    manifest_path = Path(args.manifest)

    manifest = stage_ge_docs(src_dir=src_dir, dst_dir=dst_dir)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if manifest.get("errors"):
        print("Staging completed with errors:")
        for e in manifest["errors"]:
            print(f"- {e}")
        return 2

    print(f"Staging completed: {len(manifest.get('staged', []))} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
