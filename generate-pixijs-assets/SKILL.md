---
name: generate-pixijs-assets
description: Generate, postprocess, organize, and integrate PixiJS-ready web game art assets. Use when Codex needs to create or adapt raster game art for a PixiJS project, including sprites, animation sheets, texture atlases, backgrounds, maps, props, particles, UI art, icons, loading-screen art, victory or level-complete celebration overlays, asset manifests, PixiJS Assets bundles, and TypeScript asset indexes for browser games.
---

# Generate PixiJS Assets

## Overview

Use this skill to turn a game need into production-ready art files that a PixiJS web game can load predictably. The output should include both the visual assets and the small integration layer needed by the project: manifest entries, aliases, bundle names, dimensions, animation metadata, and verification notes.

## Workflow

1. Inspect the target project before generating assets.
   - Identify the PixiJS version, build system, asset folder, existing loader, texture/spritesheet format, naming conventions, and whether assets live in `public/`, `src/`, or a CDN-backed folder.
   - Prefer the project's existing loader pattern. Only add a new manifest or generated asset index when the project has no equivalent pattern.
   - If the official PixiJS skills are installed, use `pixijs` first as the router, then load the most relevant specialized skill: `pixijs-assets` for `Assets`, manifests, bundles, spritesheets, formats, and resolution; `pixijs-scene-sprite` for `Sprite`, `AnimatedSprite`, `NineSliceSprite`, and `TilingSprite`; `pixijs-performance` for atlas, batching, memory, and unload decisions; `pixijs-create` when the project uses `create-pixi`, `creation-web`, or AssetPack.

2. Convert the request into an asset brief.
   - Define asset categories: `sprites`, `animations`, `backgrounds`, `maps`, `props`, `particles`, `ui`, `icons`, `fonts`, `celebration-overlays`.
   - Define required sizes, camera scale, target resolution, transparency, animation states, frame counts, and intended PixiJS object type (`Sprite`, `AnimatedSprite`, `TilingSprite`, `Container`, `NineSliceSprite`, `ParticleContainer`, or custom shader/mesh).
   - Resolve dimensions before choosing defaults. If the user request includes frame size, atlas size, tile size, viewport size, display size, or high-DPI scale, honor that explicit size first; then use project constraints; only then fall back to asset-role defaults. Read `references/size-planning.md` when dimensions are mentioned or when the asset might appear blurry or memory-heavy.
   - For victory, level-complete, stage-clear, reward, unlock, combo, achievement, or other celebratory popups, read `references/celebration-overlays.md` and plan a UI/FX package instead of a single baked full-screen image.
   - Decide frame count and sheet structure before generating. Read `references/animation-planning.md` when the action needs more than 4 frames, multiple phases, projectiles, muzzle FX, impact FX, or engine-specific atlas layout.
   - Decide the transparency route before generating. Read `references/transparency.md` for native-transparent output, alpha validation, and chroma-key fallback rules.
   - If style is underspecified, infer a compact style bible from the game genre and existing art. Ask only when the missing detail would cause unusable assets.

3. Generate or adapt the artwork.
   - Use existing project art as the first style reference when available.
   - Use `generate2dsprite` for character, prop, projectile, spell, and animation-sheet work when that skill is available.
   - Use `generate2dmap` for tilemaps, RPG maps, battle arenas, parallax layers, and walkable-background work when that skill is available.
   - Use `imagegen` for standalone raster art, UI skins, backgrounds, icons, textures, and cutouts when direct image generation is the best fit.
   - Keep raw generation artifacts separate from final game assets. Final assets must have predictable names and live where the project can import or serve them.

4. Postprocess for PixiJS.
   - Prefer PNG or WebP for sprites and UI. Use PNG when alpha edges matter or when the project has no WebP fallback strategy.
   - Use native transparent PNG/WebP for sprites, props, particles, icons, and UI overlays whenever the active image-generation path supports it.
   - Avoid chroma-key extraction for soft FX, glow, smoke, glass, hair-like edges, motion blur, translucent materials, or assets whose colors are close to the key color. Use native transparency or simplify the art so the silhouette is opaque.
   - Validate alpha with `scripts/alpha_qc.py` before finalizing transparent assets.
   - Keep sprite frames on a consistent grid or emit explicit frame metadata.
   - Avoid texture bleeding: add padding/extrusion when packing atlases, and verify trimmed frames preserve the intended anchor/pivot.
   - For repeated large backgrounds, consider layered parallax images or `TilingSprite` textures instead of one oversized bitmap.

5. Produce PixiJS integration artifacts.
   - Use `scripts/build_pixi_manifest.py` to generate a PixiJS `Assets` manifest and optional TypeScript asset constants from a folder of final images or spritesheet JSON.
   - Use `scripts/build_pixi_spritesheet.py` to generate PixiJS spritesheet JSON for fixed-grid atlas PNGs, especially 6/8/9/12/16-frame animations.
   - Prefer the project's existing AssetPack pipeline when one exists. Use this skill's manifest script as a lightweight fallback for projects that do not already use AssetPack.
   - Read `references/pixi-asset-contracts.md` when deciding manifest structure, alias names, spritesheet metadata, or resolution variants.
   - Read `references/integration-checklist.md` before modifying the app's loader or scene code.

6. Verify in the actual game.
   - Run the project's lint/build/test command when available.
   - Start the local dev server for frontend changes and inspect the relevant scene in a browser.
   - Check that all requested assets load without 404s, alpha is intact, animations play at the intended frame rate, anchors align with collisions/hitboxes, and mobile/retina rendering is not blurry or memory-heavy.

## Output Contract

For each completed asset pass, provide:

- Final asset paths.
- Bundle and alias names.
- Source bitmap size, frame/cell size when applicable, and intended runtime display size when known.
- Expected PixiJS usage (`Assets.loadBundle`, `Assets.load`, `Sprite.from`, `AnimatedSprite`, etc.).
- Any generated manifest or TypeScript index paths.
- For celebration overlays, component list and choreography/timeline metadata.
- Transparency route used: native alpha, project pipeline alpha, or chroma-key fallback.
- Verification performed and remaining risks.

## Script Quick Start

Generate a manifest from a folder of final assets:

```bash
python3 scripts/build_pixi_manifest.py public/assets --public-base assets --out public/assets/manifest.json --ts-out src/assets/generated-assets.ts
```

Use one bundle for a small game:

```bash
python3 scripts/build_pixi_manifest.py public/assets --bundle game --public-base assets --out public/assets/manifest.json
```

Group bundles by the first directory level by default:

```text
public/assets/ui/button-start.png      -> bundle: ui, alias: ui/button-start
public/assets/player/idle.json         -> bundle: player, alias: player/idle
public/assets/backgrounds/level-1.webp -> bundle: backgrounds, alias: backgrounds/level-1
```

Validate alpha on a final transparent PNG:

```bash
python3 scripts/alpha_qc.py public/assets/player/player.png --fail-no-alpha --json-out public/assets/player/player-alpha-qc.json
```

Generate PixiJS spritesheet JSON for a fixed-grid atlas:

```bash
python3 scripts/build_pixi_spritesheet.py public/assets/player/shoot-atlas.png --rows 2 --cols 4 --prefix player-shoot --animation shoot --out public/assets/player/shoot.json --anchor 0.5,1
```
