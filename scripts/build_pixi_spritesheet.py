#!/usr/bin/env python3
"""Generate PixiJS spritesheet JSON for a fixed-grid atlas image."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def parse_anchor(value: str) -> tuple[float, float]:
    try:
        raw_x, raw_y = value.split(",", 1)
        return float(raw_x), float(raw_y)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--anchor must be formatted as x,y") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build PixiJS Spritesheet JSON for a grid atlas.")
    parser.add_argument("atlas", help="Atlas PNG/WebP path.")
    parser.add_argument("--rows", type=int, required=True, help="Grid row count.")
    parser.add_argument("--cols", type=int, required=True, help="Grid column count.")
    parser.add_argument("--prefix", required=True, help="Frame name prefix, such as player-shoot.")
    parser.add_argument("--animation", required=True, help="Animation name for the ordered frame list.")
    parser.add_argument("--out", required=True, help="Spritesheet JSON output path.")
    parser.add_argument("--image", help="Image filename to write into meta.image. Defaults to atlas basename.")
    parser.add_argument("--anchor", type=parse_anchor, default=(0.5, 0.5), help="Frame anchor as x,y.")
    parser.add_argument("--start-index", type=int, default=1, help="First frame number.")
    parser.add_argument("--digits", type=int, default=4, help="Zero-padding digits for frame names.")
    parser.add_argument("--scale", default="1", help="Spritesheet meta.scale value.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    atlas = Path(args.atlas)
    with Image.open(atlas) as image:
        width, height = image.size

    if args.rows <= 0 or args.cols <= 0:
        raise SystemExit("rows and cols must be positive")
    if width % args.cols != 0 or height % args.rows != 0:
        raise SystemExit(
            f"atlas size {width}x{height} is not evenly divisible by {args.cols} cols and {args.rows} rows"
        )

    cell_w = width // args.cols
    cell_h = height // args.rows
    anchor_x, anchor_y = args.anchor
    frames: dict[str, object] = {}
    animation_frames: list[str] = []

    frame_number = args.start_index
    for row in range(args.rows):
        for col in range(args.cols):
            frame_name = f"{args.prefix}-{frame_number:0{args.digits}d}"
            animation_frames.append(frame_name)
            frames[frame_name] = {
                "frame": {"x": col * cell_w, "y": row * cell_h, "w": cell_w, "h": cell_h},
                "sourceSize": {"w": cell_w, "h": cell_h},
                "spriteSourceSize": {"x": 0, "y": 0, "w": cell_w, "h": cell_h},
                "anchor": {"x": anchor_x, "y": anchor_y},
            }
            frame_number += 1

    data = {
        "frames": frames,
        "animations": {args.animation: animation_frames},
        "meta": {
            "image": args.image or atlas.name,
            "size": {"w": width, "h": height},
            "scale": str(args.scale),
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(animation_frames)} frames to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
