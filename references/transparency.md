# Transparency Workflow

Use this reference whenever generated game art needs a transparent background.

## Decision order

1. Prefer native transparent output when the active image-generation entry point supports it.
   - ChatGPT Images can follow prompts to make image backgrounds transparent.
   - OpenAI API models and tools differ by model and endpoint. Check current docs when choosing explicit API parameters. As of the referenced docs, `gpt-image-2` does not support `background: "transparent"` even though ChatGPT Images can create transparent backgrounds through its own product path.
   - If using an API/CLI path that exposes `background`, request `background: "transparent"` with PNG or WebP output and `quality` medium/high for final game assets.

2. If the current tool has no transparent-background control, try prompt-level native alpha first only when the tool can plausibly return alpha PNGs.
   - Prompt for "transparent background / alpha channel PNG / no visible backdrop".
   - After generation, validate the file. Do not assume a checkerboard, white background, or black preview means real alpha.

3. Use chroma-key fallback only when native transparency is unavailable or failed.
   - Generate on a perfectly flat solid key color.
   - Use `#FF00FF` for green subjects, `#00FF00` for non-green subjects, and avoid any key color present in the subject or FX.
   - Do not use chroma key for soft glow, smoke, translucent edges, motion blur, glass, semi-transparent magic, hair-like details, or fuzzy silhouettes unless the result is explicitly accepted as a rough draft.

## Prompt rules for native alpha

Use concise wording like:

```text
Create a game-ready transparent PNG sprite sheet with a real alpha channel.
No visible background, no checkerboard, no colored backdrop, no floor plane, no cast shadow, no frame borders.
Keep each sprite fully separated with clean antialiased alpha edges and generous transparent padding.
```

For spritesheets, still state the exact grid:

```text
Exact 2x2 sprite sheet, four equal square cells, transparent background across the entire sheet.
Do not draw cell borders or guide lines.
```

## Prompt rules for chroma-key fallback

Use chroma key only for mostly opaque sprites with crisp silhouettes:

```text
Perfectly flat solid #FF00FF chroma-key background for local alpha extraction.
The background must be one uniform color with no gradients, shadows, texture, lighting variation, or antialiased colored haze.
Do not use #FF00FF anywhere in the subject, outlines, glow, particles, or motion effects.
```

If the asset is green and needs a colored key, prefer magenta. If the asset contains pink/purple glow, do not use magenta; switch to native transparency or redesign the FX.

## Validation

Run `scripts/alpha_qc.py` on final transparent images. A production-ready transparent asset should usually have:

- RGBA or LA mode.
- Transparent border pixels.
- Some fully transparent pixels outside the subject.
- No large opaque rectangle covering the full image.
- Low key-color fringe count when chroma key was used.

Preview on both light and dark backgrounds before final delivery. A black preview background can exaggerate edge contrast; a white preview can hide light halos.

## PixiJS notes

Keep alpha-bearing game sprites in PNG or WebP. Avoid JPEG for any sprite, UI overlay, particle, or atlas that needs transparency.

When using premultiplied alpha-sensitive pipelines or custom shaders, test the exact PixiJS renderer path in-browser. Haloes can come from the asset, the packer, or texture sampling.
