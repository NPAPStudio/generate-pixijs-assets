#!/usr/bin/env python3
"""Generate a PixiJS Assets manifest and optional TypeScript constants."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath


DEFAULT_EXTENSIONS = ("png", "webp", "jpg", "jpeg", "avif", "svg", "json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan a final asset folder and generate a PixiJS Assets manifest."
    )
    parser.add_argument("asset_root", help="Directory containing final browser-loadable assets.")
    parser.add_argument("--out", required=True, help="Manifest JSON output path.")
    parser.add_argument(
        "--public-base",
        default="",
        help="URL prefix for src paths, such as 'assets' for files in public/assets.",
    )
    parser.add_argument(
        "--bundle",
        help="Put all assets into this bundle. Defaults to grouping by directory.",
    )
    parser.add_argument(
        "--bundle-depth",
        type=int,
        default=1,
        help="Directory depth used for bundle names when --bundle is not set.",
    )
    parser.add_argument(
        "--root-bundle",
        default="main",
        help="Bundle name for files directly inside asset_root.",
    )
    parser.add_argument(
        "--extensions",
        default=",".join(DEFAULT_EXTENSIONS),
        help="Comma-separated file extensions to include.",
    )
    parser.add_argument(
        "--keep-extensions",
        action="store_true",
        help="Keep file extensions in aliases. Default aliases omit extensions.",
    )
    parser.add_argument("--ts-out", help="Optional TypeScript constants output path.")
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation for manifest and embedded TypeScript manifest.",
    )
    return parser.parse_args()


def slug_part(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"[^a-z0-9./-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "asset"


def normalize_posix(path: PurePosixPath, keep_extension: bool) -> str:
    parts = list(path.parts)
    if not keep_extension:
        parts[-1] = PurePosixPath(parts[-1]).stem
    return "/".join(slug_part(part) for part in parts)


def src_for(path: PurePosixPath, public_base: str) -> str:
    base = public_base.strip("/")
    rel = path.as_posix()
    return f"{base}/{rel}" if base else rel


def bundle_for(path: PurePosixPath, args: argparse.Namespace) -> str:
    if args.bundle:
        return slug_part(args.bundle)
    parent_parts = path.parts[:-1]
    if not parent_parts:
        return slug_part(args.root_bundle)
    depth = max(1, args.bundle_depth)
    return "/".join(slug_part(part) for part in parent_parts[:depth])


def should_skip(path: Path, output_paths: set[Path]) -> bool:
    if path in output_paths:
        return True
    return any(part.startswith(".") for part in path.parts)


def collect_assets(args: argparse.Namespace) -> dict[str, list[dict[str, str]]]:
    root = Path(args.asset_root).resolve()
    if not root.is_dir():
        raise SystemExit(f"asset_root is not a directory: {root}")

    extensions = {
        ext.strip().lower().removeprefix(".")
        for ext in args.extensions.split(",")
        if ext.strip()
    }
    output_paths = {Path(args.out).resolve()}
    if args.ts_out:
        output_paths.add(Path(args.ts_out).resolve())

    bundles: dict[str, list[dict[str, str]]] = {}
    aliases: dict[str, Path] = {}

    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file() or should_skip(file_path.resolve(), output_paths):
            continue
        if file_path.suffix.lower().removeprefix(".") not in extensions:
            continue

        rel_path = PurePosixPath(file_path.relative_to(root).as_posix())
        alias = normalize_posix(rel_path, args.keep_extensions)
        if alias in aliases:
            other = aliases[alias]
            raise SystemExit(
                "duplicate asset alias after normalization: "
                f"{alias} for {other} and {file_path}. "
                "Rename one file or use --keep-extensions."
            )
        aliases[alias] = file_path

        bundle_name = bundle_for(rel_path, args)
        bundles.setdefault(bundle_name, []).append(
            {"alias": alias, "src": src_for(rel_path, args.public_base)}
        )

    if not bundles:
        raise SystemExit(f"no matching assets found in {root}")

    return bundles


def build_manifest(bundles: dict[str, list[dict[str, str]]]) -> dict[str, object]:
    return {
        "bundles": [
            {"name": name, "assets": assets}
            for name, assets in sorted(bundles.items(), key=lambda item: item[0])
        ]
    }


def write_json(path: Path, data: dict[str, object], indent: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent, sort_keys=False) + "\n", encoding="utf-8")


def ts_string_array(values: list[str]) -> str:
    return "[\n" + "".join(f"  {json.dumps(value)},\n" for value in values) + "] as const"


def write_ts(path: Path, manifest: dict[str, object], indent: int) -> None:
    bundles = manifest["bundles"]
    bundle_names = [bundle["name"] for bundle in bundles]  # type: ignore[index]
    aliases = [
        asset["alias"]
        for bundle in bundles  # type: ignore[assignment]
        for asset in bundle["assets"]  # type: ignore[index]
    ]
    body = "\n".join(
        [
            "/* Generated by build_pixi_manifest.py. */",
            "",
            f"export const assetManifest = {json.dumps(manifest, indent=indent)} as const;",
            "",
            f"export const assetBundles = {ts_string_array(bundle_names)};",
            "",
            f"export const assetAliases = {ts_string_array(aliases)};",
            "",
            "export type AssetBundleName = (typeof assetBundles)[number];",
            "export type AssetAlias = (typeof assetAliases)[number];",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main() -> int:
    args = parse_args()
    bundles = collect_assets(args)
    manifest = build_manifest(bundles)
    write_json(Path(args.out), manifest, args.indent)
    if args.ts_out:
        write_ts(Path(args.ts_out), manifest, args.indent)

    count = sum(len(bundle["assets"]) for bundle in manifest["bundles"])  # type: ignore[index]
    print(f"Wrote {len(manifest['bundles'])} bundles and {count} assets to {args.out}")
    if args.ts_out:
        print(f"Wrote TypeScript constants to {args.ts_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
