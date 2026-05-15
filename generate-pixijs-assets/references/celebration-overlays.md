# Celebration Overlays

Use this reference for victory, level-complete, stage-clear, reward, achievement, unlock, combo, jackpot, or mission-complete popups and animations.

## Principle

Build a reusable UI/FX package, not one baked full-screen image. Separate stable UI pieces from animated effects and let PixiJS choreograph the reveal. Bake text into images only when the user explicitly asks for fixed decorative lettering; otherwise render text with `Text` or `BitmapText`.

## Asset split

A typical package includes:

- UI: dim overlay metadata, modal panel, title ribbon, badge/trophy, stars, reward slots, buttons, close icon, decorative corners.
- FX: burst, sparkle, glow ring, coin pop, star pop, confetti pieces, ribbon streamers.
- Metadata: manifest aliases, frame durations, anchors, nine-slice borders, intended display size, and timeline/choreography.

Prefer PixiJS objects by role:

- `Container`: owns the whole overlay and timeline.
- `Graphics`: dim background, unless the project uses a textured dim.
- `NineSliceSprite`: scalable panel and buttons.
- `Sprite`: badges, icons, rewards, static ornaments.
- `AnimatedSprite`: burst, sparkle, star pop, coin pop.
- `ParticleContainer`: confetti, small coins, tiny sparkles.

## Size planning

Apply `size-planning.md` first. If no project or user dimensions are available, use these logical defaults:

- viewport assumption: `1280x720`.
- modal panel display size: `640x400` to `760x460`.
- primary button display size: `240x72` to `300x88`.
- reward icon display size: `72` to `128`.
- star/badge display size: `96` to `160`.
- particle texture source: `32` to `64`.
- FX spritesheet cells: `128` for small sparkles, `192` or `256` for burst/glow/star-pop.

For high-DPI UI, generate at `@2x` or higher but document the intended runtime display size. Keep full FX atlases under the project texture limit; if unknown, keep each atlas at or below `2048x2048`.

For scalable panels/buttons, prefer nine-slice-safe art with generous corners and edges. Record border values such as `{ left: 48, top: 48, right: 48, bottom: 48 }` in integration notes or TypeScript metadata.

## Generation prompts

For UI pieces:

```text
Transparent PNG game UI asset pack for a victory overlay.
No baked text, no background, no full-screen screenshot.
Separate centered modal panel, title ribbon, reward slots, star icons, trophy badge, primary button states, and close icon.
Clean readable mobile game style, consistent lighting, crisp alpha edges, high-DPI source.
```

For FX sheets:

```text
Transparent PNG spritesheet for a victory burst effect.
Exact 2x4 grid, eight equal square cells, no borders, no background.
The burst expands and fades over the frames, centered in each cell, generous transparent padding.
```

Avoid soft FX that require chroma-key cleanup. Use native transparent output whenever available.

## Choreography

Emit a small declarative timeline near the asset index so the game can reproduce the celebration:

```ts
export const victoryOverlayTimeline = [
  { at: 0, target: "backdrop", action: "fade", from: 0, to: 0.65, duration: 180 },
  { at: 80, target: "panel", action: "pop", from: 0.82, to: 1, duration: 260 },
  { at: 220, target: "titleRibbon", action: "drop", duration: 220 },
  { at: 320, target: "burst", action: "playOnce", fps: 18 },
  { at: 420, target: "stars", action: "staggerPop", gap: 120 },
  { at: 620, target: "rewards", action: "staggerReveal", gap: 90 },
  { at: 700, target: "confetti", action: "emit", duration: 1500 },
] as const;
```

Use per-frame durations for impact frames instead of adding too many generated frames. Keep panel motion in code; reserve spritesheets for visual phenomena that need drawn frame changes.

## Suggested file layout

```text
assets/celebration/victory/panel@2x.png
assets/celebration/victory/button-primary@2x.png
assets/celebration/victory/button-primary-pressed@2x.png
assets/celebration/victory/star-filled@2x.png
assets/celebration/victory/reward-slot@2x.png
assets/celebration/victory/confetti-pieces.png
assets/celebration/victory/burst-atlas.png
assets/celebration/victory/burst.json
src/assets/victory-overlay-assets.ts
```

Use stable aliases such as `celebration/victory/panel`, `celebration/victory/burst`, and `celebration/victory/confetti-pieces`.

## Acceptance checks

Before finalizing:

- Verify transparent alpha on all UI and FX PNGs.
- Confirm no essential text is baked into images unless requested.
- Check panel/buttons scale cleanly at mobile and desktop sizes.
- Confirm spritesheet cells do not touch edges and anchors are centered unless metadata says otherwise.
- Preview the overlay on both dark and bright game backgrounds.
- Ensure the manifest, timeline, and intended display sizes match the generated source sizes.
