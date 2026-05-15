# Icon And SVG Asset Workflow

Use this reference for small UI icons, HUD icons, toolbar icons, inventory/status symbols, SVG requests, tintable icons, and icon sets. Small icons fail when treated like generic image generation: AI tends to add noisy detail, inconsistent geometry, weak silhouettes, and uneven stroke weight. Use a dedicated icon pipeline.

## Choose The Pipeline

- **Symbolic UI icon**: vector-first. Reuse the project's icon set first; otherwise use a proven icon family or author a simple SVG on a grid. Examples: close, pause, coin, heart, mute, settings, retry, trophy outline, lock, arrow, inventory tab.
- **Game item, ability, reward, badge, or shop icon**: high-resolution raster-first unless the desired style is flat. Generate or paint at 512px/1024px, simplify the silhouette, then export 64px/128px/256px variants and inspect the smallest intended size.
- **Brand, logo, faction mark, elemental symbol, or simple emblem**: vector-first if it must be crisp, tintable, or animated by path; raster-first only when painterly lighting and texture are the point.

Do not generate a final 16px/24px/32px icon directly with image generation. Create a larger source and reduce it, or create SVG source.

## Vector-First Rules

1. Match the existing UI language before creating anything new: icon library, stroke width, corner radius, fill style, viewBox size, color tokens, and hover/disabled states.
2. Use a consistent grid: normally `viewBox="0 0 24 24"` for system UI, `32 32` for game HUD, or `48 48` for richer status icons.
3. Keep geometry simple. At 24px, use 1-3 primary shapes; at 32px, 2-5 shapes; at 48px, small accent shapes are acceptable.
4. Prefer one color plus `currentColor` for tintable UI icons. Use two colors only when the second color communicates state or depth.
5. Use stable stroke settings for outline icons: `stroke="currentColor"`, `stroke-width="2"` on a 24 grid, `stroke-linecap="round"`, `stroke-linejoin="round"`, `fill="none"`.
6. For filled icons, use clean silhouettes with intentional counters. Avoid thin islands, tiny holes, excessive gradients, filters, embedded images, external references, and text.
7. Keep source SVG separate from exported textures. Do not only keep the rasterized output.

## Raster-First Rules For Game Icons

1. Generate or paint a large transparent source, usually 512px or 1024px square.
2. Ask for a centered object, readable silhouette, no text, no UI frame unless requested, transparent background, strong lighting separation, and minimal tiny detail.
3. Downsample to the actual sizes used by the game: commonly 32, 48, 64, 96, 128, and `@2x` variants.
4. Inspect on the actual UI background and on a neutral light/dark checker. If the icon only works large, simplify and regenerate.
5. For inventory grids, badges, and ability bars, produce a contact sheet with all icons at final display size to catch style drift.

## PixiJS Integration

- For DOM UI, prefer inline SVG or the app's icon component when available.
- For PixiJS scene UI, SVG can be loaded as a texture, but many small icons may batch better as pre-rasterized PNG/WebP atlas textures.
- For tintable PixiJS sprites, export a white monochrome PNG/WebP or use an SVG texture designed around `currentColor` only when the loader pipeline preserves the expected color behavior.
- For high-DPI displays, export `@2x` assets or set the texture resolution metadata according to the project's existing pattern.
- Name consistently: `icons/play.svg`, `icons/play@2x.png`, `ui/icons/play`, or the project's existing alias format.

## Prompt Patterns

For symbolic SVG icons, prefer code generation over raster generation:

```text
Create an SVG icon for {meaning}. Style: 24x24 viewBox, outline, stroke=currentColor, stroke-width=2, round linecaps and joins, no fill, no text, no filters, no embedded images, readable at 16px.
```

For illustrative game icons:

```text
Square transparent PNG source for a fantasy game ability icon: {object/effect}. Centered, strong silhouette, readable at 48px, no text, no border frame, crisp edges, limited palette, high contrast against dark and light UI backgrounds.
```

## Quality Checks

Run `scripts/svg_icon_qc.py` on SVG sources. Then inspect rendered icons at the smallest in-game size. A good icon still reads when blurred slightly, shown in grayscale, or tinted to a single color.

Reject or revise icons with:

- Missing `viewBox`.
- Inconsistent stroke weight within a set.
- More colors than the UI system supports.
- Embedded rasters, external references, filters, or text.
- Important details below one device pixel at the target size.
- A silhouette that cannot be identified at the final display size.

