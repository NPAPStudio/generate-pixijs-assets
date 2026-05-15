# PixiJS Asset Contracts

Use this reference when deciding how generated art should be named, packed, described, and loaded by PixiJS.

## Manifests and bundles

PixiJS `Assets` supports a manifest object with a top-level `bundles` array. Each bundle has a `name` and an `assets` list. Each asset should have a stable `alias` and a browser-resolvable `src`.

```ts
import { Assets } from "pixi.js";
import manifest from "./manifest.json";

await Assets.init({ manifest });
const uiAssets = await Assets.loadBundle("ui");
const buttonTexture = await Assets.load("ui/button-start");
```

Prefer bundle names that match loading phases or scene ownership:

- `preload`: loading-screen art, minimal logo, loading bar.
- `ui`: buttons, panels, icons, cursors.
- `player`, `enemies`, `projectiles`: frequently reused gameplay entities.
- `level-1`, `level-2`: level-specific backgrounds, props, maps.
- `shared`: textures reused across scenes.

Use aliases without file extensions unless the existing project keeps extensions in aliases. Keep aliases stable even if source file formats change from PNG to WebP.

When multiple formats or resolutions exist, prefer PixiJS resolver patterns instead of picking one file manually:

```json
{ "alias": "hero", "src": "hero@{1,2}x.{webp,png}" }
```

Attach per-loader options directly to manifest entries when needed:

```json
{ "alias": "tile", "src": "tile.png", "data": { "scaleMode": "nearest" } }
```

Initialize `Assets` once with all startup options combined. Do not call `Assets.init` once for a manifest and again for a base path or texture preferences.

## File naming

Use lowercase kebab-case for files and directories:

```text
player/idle/player-idle-0001.png
ui/button-start.png
backgrounds/forest-dawn-layer-02.webp
```

Avoid spaces, mixed case, punctuation beyond hyphen/underscore, and names that encode temporary prompt wording.

## Resolution variants

Use one of these patterns, matching the existing project:

- `asset.png`, `asset@2x.png`: common for high-DPI sprite/UI variants.
- `asset.{png,webp}`: useful when the loader resolves preferred formats.
- Separate bundles such as `level-1-low` and `level-1-high`: useful for memory-constrained games.

Document intended display size separately when the source bitmap is high-resolution. Do not rely on filename alone to communicate scale. When the user provides dimensions, preserve them in the asset metadata or integration notes rather than replacing them with role-based defaults.

## Spritesheets

For PixiJS spritesheet JSON, prefer a common atlas structure with `frames` and `meta.image`, or keep the project's existing TexturePacker/AssetPack format. Frame names should be animation-friendly:

```text
player-idle-0001
player-idle-0002
player-run-0001
```

Record animation metadata near the asset integration code:

```ts
export const playerAnimations = {
  idle: ["player-idle-0001", "player-idle-0002"],
  run: ["player-run-0001", "player-run-0002", "player-run-0003"],
} as const;
```

When trimming frames, preserve source size, sprite source size, and pivot/anchor decisions. For character animation, keep feet aligned across frames.

Ensure `meta.scale` matches the atlas resolution. If an atlas image is exported as a high-DPI source but `meta.scale` is wrong, sprites render at the wrong size.

Use AssetPack or the project's existing atlas packer for production atlases when available. The lightweight manifest script in this skill does not pack separate PNG frames into atlases; it only indexes browser-loadable final assets.

## Anchors and pivots

Declare expected anchor conventions in code or metadata:

- Characters: usually bottom-center, `(0.5, 1)`.
- Icons and UI buttons: usually center, `(0.5, 0.5)`.
- Tiles and background layers: usually top-left, `(0, 0)`.
- Projectiles: usually center or nose-aligned depending on collision math.

Match existing collision and scene placement code before changing anchor assumptions.

## Texture size and memory

Keep atlases below the project's WebGL target limits. If unknown, stay at or below 2048x2048 for broad mobile compatibility and split large art into scene bundles. Prefer multiple scene-specific atlases over one global atlas that every scene must load.

Large backgrounds should be intentionally sized for the camera. Split very wide scenes into parallax layers or repeated textures instead of shipping huge single images.
