#!/usr/bin/env python3
"""Inspect transparent game assets for alpha and likely chroma-key fringes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report alpha-channel quality metrics for an image.")
    parser.add_argument("image", help="PNG/WebP image to inspect.")
    parser.add_argument("--json-out", help="Optional JSON report output path.")
    parser.add_argument("--fail-no-alpha", action="store_true", help="Exit nonzero if image has no alpha channel.")
    parser.add_argument(
        "--max-border-opaque",
        type=int,
        help="Exit nonzero if opaque pixels on the outer border exceed this count.",
    )
    parser.add_argument(
        "--max-key-fringe",
        type=int,
        help="Exit nonzero if likely magenta/green key-color fringe pixels exceed this count.",
    )
    return parser.parse_args()


def likely_key_fringe(r: int, g: int, b: int, a: int) -> bool:
    if a == 0:
        return False
    magenta = r > 180 and b > 180 and g < 120
    green = g > 180 and r < 120 and b < 120
    return magenta or green


def analyze(path: Path) -> dict[str, object]:
    with Image.open(path) as img:
        rgba = img.convert("RGBA")
        alpha = rgba.getchannel("A")
        width, height = rgba.size
        pixels = rgba.load()
        alpha_values = list(alpha.tobytes())

        transparent = sum(1 for value in alpha_values if value == 0)
        opaque = sum(1 for value in alpha_values if value == 255)
        partial = width * height - transparent - opaque

        border_opaque = 0
        border_partial = 0
        key_fringe = 0
        for x in range(width):
            for y in (0, height - 1):
                _r, _g, _b, a = pixels[x, y]
                if a == 255:
                    border_opaque += 1
                elif a:
                    border_partial += 1
        for y in range(1, height - 1):
            for x in (0, width - 1):
                _r, _g, _b, a = pixels[x, y]
                if a == 255:
                    border_opaque += 1
                elif a:
                    border_partial += 1

        data = rgba.tobytes()
        for index in range(0, len(data), 4):
            r, g, b, a = data[index : index + 4]
            if likely_key_fringe(r, g, b, a):
                key_fringe += 1

        bbox = alpha.getbbox()
        return {
            "path": str(path),
            "mode": img.mode,
            "size": [width, height],
            "has_alpha": "A" in img.getbands(),
            "alpha_min": min(alpha_values),
            "alpha_max": max(alpha_values),
            "transparent_pixels": transparent,
            "partial_alpha_pixels": partial,
            "opaque_pixels": opaque,
            "transparent_ratio": transparent / (width * height),
            "partial_alpha_ratio": partial / (width * height),
            "alpha_bbox": list(bbox) if bbox else None,
            "border_opaque_pixels": border_opaque,
            "border_partial_pixels": border_partial,
            "likely_key_fringe_pixels": key_fringe,
        }


def main() -> int:
    args = parse_args()
    report = analyze(Path(args.image))
    text = json.dumps(report, indent=2)
    print(text)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")

    errors: list[str] = []
    if args.fail_no_alpha and not report["has_alpha"]:
        errors.append("image has no alpha channel")
    if args.max_border_opaque is not None and report["border_opaque_pixels"] > args.max_border_opaque:
        errors.append(
            f"border opaque pixels {report['border_opaque_pixels']} exceed {args.max_border_opaque}"
        )
    if args.max_key_fringe is not None and report["likely_key_fringe_pixels"] > args.max_key_fringe:
        errors.append(
            f"likely key fringe pixels {report['likely_key_fringe_pixels']} exceed {args.max_key_fringe}"
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
