from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

RUN_ROOT = Path(__file__).resolve().parents[1]

# Local import (run-local path)
sys.path.append(str(RUN_ROOT / "scripts" / "utils"))
from azure_client import AzureOpenAIResponsesClient  # type: ignore



SYSTEM_PROMPT = """
You are a senior presentation designer and reverse-engineer.

You will receive an image of a slide.

Your task: produce a reconstruction spec so an engineer can rebuild this slide in a branded template using editable objects (text boxes, shapes, simple diagrams), NOT as a single flat background image.

Constraints:
- Prefer simple, Premier-style layouts.
- It does not need to be pixel-perfect.
- Extract all visible text accurately.
- Identify any photographic images on the slide and return approximate bounding boxes so we can crop them from the render and reuse them.
- If the slide is a diagram, return a simplified set of labeled boxes (and optional arrows) that conveys the same message.

Output requirements (IMPORTANT):
- Output STRICT JSON only. No markdown.
- Coordinates must be normalized 0-1000 relative to the image width/height.
""".strip()


def _encode_image_b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def _extract_json(text: str) -> Dict[str, Any]:
    # Model may return leading/trailing text; try to extract the first JSON object.
    m = re.search(r"\{[\s\S]*\}\s*$", text.strip())
    if not m:
        m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError("No JSON object found in model output")
    return json.loads(m.group(0))


def _build_prompt(slide_index: int) -> str:
    return (
        "Return a reconstruction spec for this slide. "
        "Include layout hint and content in reading order. "
        f"Slide index: {slide_index}.\n\n"
        "JSON schema (example; follow this shape):\n"
        "{\n"
        "  \"layout_hint\": \"title|section|content|two_col|image_focus\",\n"
        "  \"title\": \"...\",\n"
        "  \"subtitle\": \"...\",\n"
        "  \"bullets\": [\"...\"],\n"
        "  \"notes\": \"short guidance for rebuild\",\n"
        "  \"photos\": [\n"
        "    {\"label\": \"train\", \"bbox\": [x,y,w,h]}\n"
        "  ],\n"
        "  \"diagram\": {\n"
        "    \"nodes\": [\n"
        "      {\"label\": \"...\", \"bbox\": [x,y,w,h]}\n"
        "    ],\n"
        "    \"arrows\": [\n"
        "      {\"from\": 0, \"to\": 1, \"label\": \"optional\"}\n"
        "    ]\n"
        "  }\n"
        "}\n"
    )


def extract_for_slide(client: AzureOpenAIResponsesClient, image_path: Path, slide_index: int) -> Dict[str, Any]:
    # Resize + JPEG compress to reduce payload size for API stability.
    # Keep max dimension at 1400px (still readable for slide text in most cases).
    tmp_path: Optional[Path] = None
    mime = "image/png"
    img_to_send = image_path
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        max_dim = max(img.size)
        if max_dim > 1400:
            scale = 1400 / max_dim
            new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
            img = img.resize(new_size)

        tmp_path = image_path.with_suffix(".tmp.jpg")
        img.save(tmp_path, format="JPEG", quality=82, optimize=True)
        img_to_send = tmp_path
        mime = "image/jpeg"

    b64 = _encode_image_b64(img_to_send)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": _build_prompt(slide_index)},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        },
    ]

    raw = client.chat(messages, reasoning_effort="low", max_output_tokens=2500, timeout_s=180)
    try:
        return _extract_json(raw)
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--renders-dir",
        default=str(RUN_ROOT / "exports" / "conversion" / "source_renders"),
        help="Directory with slide_XX.png renders",
    )
    parser.add_argument(
        "--out-dir",
        default=str(RUN_ROOT / "exports" / "conversion" / "slide_specs"),
        help="Where to write slide spec JSON files",
    )
    parser.add_argument(
        "--slides",
        default="",
        help="Comma-separated slide numbers (1-based) to process. Empty means all slides present in renders dir.",
    )
    args = parser.parse_args()

    renders_dir = Path(args.renders_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.slides.strip():
        wanted = [int(s.strip()) for s in args.slides.split(",") if s.strip()]
    else:
        wanted = []

    client = AzureOpenAIResponsesClient()

    # Only accept real slide renders like slide_01.png (ignore any temp files).
    slide_paths = sorted(
        [p for p in renders_dir.glob("slide_*.png") if re.fullmatch(r"slide_\d+\.png", p.name)]
    )
    if wanted:
        wanted_set = set(wanted)
        slide_paths = [p for p in slide_paths if int(p.stem.split("_")[1]) in wanted_set]

    if not slide_paths:
        raise SystemExit(f"No slide PNGs found in {renders_dir}")

    for p in slide_paths:
        slide_num = int(p.stem.split("_")[1])
        out_path = out_dir / f"slide_{slide_num:02d}.json"
        if out_path.exists():
            # Idempotent: don't redo if already extracted.
            continue

        print(f"Extracting spec for slide {slide_num} -> {out_path.name}")
        spec = extract_for_slide(client, p, slide_num)
        spec.setdefault("_meta", {})
        spec["_meta"].update({"source_render": str(p), "slide_index": slide_num})
        out_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
