# Animation Planning

Use this reference when a requested sprite animation needs more than the default 4 frames, has multiple phases, or includes projectiles/FX.

## Frame count defaults

Start small, then add frames only where the motion needs them:

- `idle`: 4 frames.
- `projectile loop`: 4 frames.
- `hit impact`: 4-6 frames.
- `shoot`, `attack`, `cast`: 6-8 frames.
- `death`, `summon`, `transformation`: 6-12 frames.
- player/hero/boss signature action: 8-16 frames.

Use nonuniform playback timing in PixiJS before increasing frames. A 6-frame action with held windup/recovery frames can read better than a noisy 12-frame generation.

## Sheet shapes

Prefer compact multi-row grids for generated raw sheets:

- 4 frames: `2x2`.
- 6 frames: `2x3`.
- 8 frames: `2x4`.
- 9 frames: `3x3`.
- 12 frames: `3x4` or `4x3`.
- 16 frames: `4x4`.

Avoid raw `1xN` strips for characters, enemies, animated props, and body actions. Long strips drift horizontally and are harder to crop consistently. If the engine needs a strip, generate and QC a compact grid first, then assemble the strip deterministically.

## Frame and cell size

Before choosing a `cell_size`, apply the size precedence in `references/size-planning.md`: user-specified dimensions first, project constraints second, role defaults last.

When no explicit size is available, use role defaults that match the intended on-screen importance:

- projectiles, icons, small props, and small FX: `128` px cells.
- compact enemies, medium props, and minor NPCs: `192` px cells.
- player characters, full-body actors, and prominent enemies: `256` px cells.
- hero, boss, close-camera, or premium character actions: `384` or `512` px cells.

For character sheets, prefer `fit_scale` around `0.85` to `0.9` so limbs and antialiasing do not touch cell edges. If a user asks for a specific rendered size, compute the source cell from display size and device pixel ratio instead of using these defaults.

## Split body, projectile, and FX

Do not put everything in one body sheet when the animation includes detached visual elements.

For a shooter/caster:

- body sheet: windup, release, recoil, recovery.
- projectile sheet: separate short loop.
- muzzle FX: separate short one-shot if needed.
- impact FX: separate one-shot.

This keeps the body scale stable and avoids a wide FX bounding box shrinking the character inside fixed cells.

## Multi-phase actions

For high-value assets, split long actions into coherent phases:

- `shoot-windup`: 4 frames.
- `shoot-release`: 4 frames.
- `shoot-recovery`: optional 2-4 frames.

After QC, assemble a final `shoot` animation list in spritesheet JSON. The animation list can reference frames from one atlas or multiple loaded sheets, depending on the project pattern.

## PixiJS playback notes

`AnimatedSprite` accepts either a texture array or frame objects with per-frame duration. Use per-frame duration for snappier attacks:

```ts
const shoot = new AnimatedSprite([
  { texture: sheet.textures["player-shoot-0001"], time: 120 },
  { texture: sheet.textures["player-shoot-0002"], time: 80 },
  { texture: sheet.textures["player-shoot-0003"], time: 50 },
  { texture: sheet.textures["player-shoot-0004"], time: 90 },
]);
```

Use `loop = false` for attacks, casts, impacts, deaths, and transformations. Use loops for idle, run, hover, projectile flight, and ambient FX.

## Acceptance checks

Before finalizing a longer animation:

- Check frame-to-frame identity, scale, and anchor stability.
- Check no frame touches the cell edge.
- Check the body does not shrink compared with idle/run sheets.
- Check detached FX are intentionally separate or the runtime metadata supports wider cells.
- Validate alpha and preview on light and dark backgrounds.
