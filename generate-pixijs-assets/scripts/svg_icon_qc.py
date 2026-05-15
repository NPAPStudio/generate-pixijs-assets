#!/usr/bin/env python3
"""Lightweight QC for SVG icons intended for game/UI use."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET


SHAPE_TAGS = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}
WARN_TAGS = {"filter", "mask", "pattern", "linearGradient", "radialGradient"}
ERROR_TAGS = {"script", "foreignObject", "image"}
STYLE_COLOR_RE = re.compile(r"(?:fill|stroke|color|stop-color)\s*:\s*([^;]+)")
EXTERNAL_REF_RE = re.compile(r"(?:href|xlink:href)\s*=\s*['\"](?!#|data:)[^'\"]+['\"]")
IGNORED_COLORS = {"none", "currentcolor", "currentColor", "transparent", "inherit", "unset"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_viewbox(value: str | None) -> list[float] | None:
    if not value:
        return None
    parts = re.split(r"[\s,]+", value.strip())
    if len(parts) != 4:
        return None
    try:
        return [float(part) for part in parts]
    except ValueError:
        return None


def normalize_color(value: str) -> str | None:
    value = value.strip().strip("'\"")
    if not value or value in IGNORED_COLORS or value.lower() in IGNORED_COLORS:
        return None
    if value.startswith("url("):
        return None
    return value.lower()


def collect_colors(root: ET.Element) -> set[str]:
    colors: set[str] = set()
    for element in root.iter():
        for key in ("fill", "stroke", "color", "stop-color"):
            value = element.attrib.get(key)
            color = normalize_color(value) if value is not None else None
            if color:
                colors.add(color)
        style = element.attrib.get("style", "")
        for match in STYLE_COLOR_RE.finditer(style):
            color = normalize_color(match.group(1))
            if color:
                colors.add(color)
    return colors


def check_svg(path: str, args: argparse.Namespace) -> dict[str, object]:
    result: dict[str, object] = {
        "path": path,
        "ok": True,
        "errors": [],
        "warnings": [],
        "metrics": {},
    }
    errors: list[str] = result["errors"]  # type: ignore[assignment]
    warnings: list[str] = result["warnings"]  # type: ignore[assignment]

    try:
        text = open(path, "r", encoding="utf-8").read()
        root = ET.fromstring(text)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Unable to parse SVG: {exc}")
        result["ok"] = False
        return result

    if local_name(root.tag) != "svg":
        errors.append("Root element is not <svg>.")

    viewbox = parse_viewbox(root.attrib.get("viewBox"))
    if viewbox is None:
        errors.append("Missing or invalid viewBox.")
    else:
        min_x, min_y, width, height = viewbox
        if min_x != 0 or min_y != 0:
            warnings.append("viewBox does not start at 0 0; check alignment on an icon grid.")
        if width <= 0 or height <= 0:
            errors.append("viewBox width/height must be positive.")
        if width != height:
            warnings.append("viewBox is not square; confirm this is intentional for UI layout.")

    tags = [local_name(element.tag) for element in root.iter()]
    shape_count = sum(1 for tag in tags if tag in SHAPE_TAGS)
    result["metrics"] = {
        "shape_count": shape_count,
        "tag_count": len(tags),
    }

    blocked = sorted({tag for tag in tags if tag in ERROR_TAGS})
    for tag in blocked:
        errors.append(f"Uses <{tag}>; avoid embedded images, scripts, and foreignObject in game icons.")

    if args.forbid_text and "text" in tags:
        errors.append("Uses <text>; convert text to intentional paths or avoid text in small icons.")

    risky = sorted({tag for tag in tags if tag in WARN_TAGS})
    for tag in risky:
        warnings.append(f"Uses <{tag}>; verify the PixiJS/browser pipeline renders it consistently.")

    if EXTERNAL_REF_RE.search(text):
        errors.append("Uses an external href reference; keep icons self-contained.")

    colors = collect_colors(root)
    result["metrics"]["color_count"] = len(colors)  # type: ignore[index]
    result["metrics"]["colors"] = sorted(colors)  # type: ignore[index]
    if len(colors) > args.max_colors:
        warnings.append(f"Uses {len(colors)} colors; max requested is {args.max_colors}.")
    if shape_count > args.max_elements:
        warnings.append(f"Uses {shape_count} visible shape elements; max requested is {args.max_elements}.")

    if args.require_current_color and colors and colors != {"currentcolor"}:
        warnings.append("Icon is not purely currentColor/tintable.")

    if errors or (warnings and args.fail_on_warning):
        result["ok"] = False
    return result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="QC SVG icons for small game/UI usage.")
    parser.add_argument("svg", nargs="+", help="SVG file(s) to inspect.")
    parser.add_argument("--max-elements", type=int, default=16)
    parser.add_argument("--max-colors", type=int, default=2)
    parser.add_argument("--forbid-text", action="store_true", default=True)
    parser.add_argument("--allow-text", dest="forbid_text", action="store_false")
    parser.add_argument("--require-current-color", action="store_true")
    parser.add_argument("--fail-on-warning", action="store_true")
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    results = [check_svg(path, args) for path in args.svg]
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2)
            handle.write("\n")

    for result in results:
        status = "ok" if result["ok"] else "fail"
        print(f"{status}: {result['path']}")
        for error in result["errors"]:  # type: ignore[union-attr]
            print(f"  error: {error}")
        for warning in result["warnings"]:  # type: ignore[union-attr]
            print(f"  warning: {warning}")

    return 0 if all(result["ok"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
