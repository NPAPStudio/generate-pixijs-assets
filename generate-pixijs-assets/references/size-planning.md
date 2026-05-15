# Size Planning

Use this reference whenever the user mentions dimensions, the project has fixed layout/camera constraints, or a sprite could become blurry after scaling.

## Dimension precedence

Choose sizes in this order:

1. Explicit user dimensions from the prompt.
2. Project constraints from existing assets, camera zoom, tile size, collision boxes, CSS canvas size, target device pixel ratio, or loader metadata.
3. Asset-role defaults.

Do not let a role default override a size the user already gave. When a prompt says `256x256 sprite`, `64px icon`, `1024x512 background`, `2x4 sheet`, `player appears 180px tall`, `@2x`, or similar, treat that as the primary sizing requirement.

## Interpret common wording

- `frame`, `cell`, or `sprite size`: size of each spritesheet cell or standalone source image.
- `sheet` or `atlas size`: size of the whole image; derive cell size from grid rows and columns.
- `display`, `rendered`, `in game`, or `on screen`: runtime size. Choose a source bitmap large enough for the intended device pixel ratio, then document the display size separately.
- `tile size`: world/grid unit size. Tile images should match it unless the project uses resolution variants such as `@2x`.
- `background`, `map`, or `viewport`: usually exact camera or world-layer dimensions, unless it is a parallax or tiling texture.
- `@2x`, `retina`, or high-DPI: source bitmap is larger than the logical display size. Set spritesheet `meta.scale` or project metadata so PixiJS renders it at the intended logical size.

## Source-size rule

For runtime-sized sprites, estimate source size from display size and target pixel ratio:

```text
source_cell_px >= ceil(display_px * device_pixel_ratio / fit_scale)
```

Use the larger of width or height for square fixed-grid cells. `fit_scale` is the fraction of the cell occupied by the visible art after transparent padding; `0.85` to `0.9` is typical for character sheets.

Example: a character should appear about `180px` tall on a `2x` display with `fit_scale=0.9`. Use at least `ceil(180 * 2 / 0.9) = 400`, so pick a `384` or `512` cell depending on memory budget and project conventions.

## Fallback defaults

Use these only when neither the prompt nor project provides size information:

- tiny particles, bullets, pickups: `64` or `96` px cells.
- icons, small props, projectile loops: `128` px cells.
- medium props, enemies, compact NPCs: `192` px cells.
- player characters, full-body actors, prominent enemies: `256` px cells.
- hero/boss/close-camera characters: `384` or `512` px cells.
- UI buttons/panels/backgrounds: match the intended layout dimensions.

Keep full-sheet dimensions within the project's texture limits. If unknown, stay at or below `2048x2048` for broad mobile compatibility, split long animations into multiple atlases, or use resolution variants.

## Manifest notes

Record both the source bitmap dimensions and intended display dimensions in generated notes or TypeScript metadata. A filename like `@2x` is not enough; PixiJS needs correct `meta.scale`, resolution metadata, or explicit runtime sizing.
