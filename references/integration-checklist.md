# PixiJS Integration Checklist

Use this checklist before changing game code or declaring an asset pass complete.

## Before writing files

- Locate the current asset root and confirm whether runtime URLs are relative to `/`, Vite `public/`, imported `src` modules, or a CDN.
- Check whether the project already uses `Assets.init`, `Assets.addBundle`, AssetPack, TexturePacker JSON, or custom loader code.
- Keep generated files in an obviously generated path if the repo already has one, such as `src/assets/generated.ts`.
- Do not move existing art unless the user asked for a reorganization.

## Manifest integration

- Initialize `Assets` once, ideally during boot/preload.
- Load bundles at scene boundaries with `Assets.loadBundle`.
- Load individual aliases with `Assets.load` only when the project already does direct alias loading or the asset is truly one-off.
- Keep aliases independent from file extension so art can move from PNG to WebP without touching gameplay code.
- If the project uses a base path, ensure manifest `src` paths and `Assets.init({ basePath })` do not double-prefix URLs.

## Scene integration

- Create sprites from loaded textures or aliases according to the local pattern.
- Set anchors/pivots immediately after creating sprites.
- For `AnimatedSprite`, confirm frame order, frame duration, loop mode, and first frame.
- For UI, test hover/pressed/disabled art states if they exist.
- For backgrounds, test camera movement and viewport resizing.

## Browser verification

- Open the scene in the local dev server.
- Check the console and network panel for missing assets, wrong MIME types, and CORS issues.
- Verify alpha edges against both light and dark backgrounds.
- Exercise scene transitions to catch unloaded bundle mistakes.
- Test one narrow/mobile viewport if the asset is visible in responsive UI.

## Canvas and WebGL screenshots

Headless browser screenshots can be unreliable for PixiJS/WebGL scenes. If an automated screenshot is blank or only shows the page background, do not immediately treat it as an asset failure.

Check in this order:

- Confirm the page, JavaScript, manifest, spritesheet JSON, and image files return `200`.
- Confirm the DOM contains a canvas and that its CSS and backing-store dimensions are nonzero.
- Check browser console errors and unhandled promise rejections.
- Open the scene in a normal headed browser when possible.
- Try a different browser/rendering path only after resource loading and canvas sizing are known good.
- Create a deterministic preview PNG/GIF from the generated assets or runtime timeline as a fallback artifact for review.

When reporting verification, distinguish `asset/runtime issue` from `headless screenshot issue`.

## Delivery notes

Report final paths, aliases, bundle names, and any code entry points changed. Mention any assets that are intentionally placeholders, any style mismatch risk, and any performance-sensitive images that may need compression or atlas packing later.
