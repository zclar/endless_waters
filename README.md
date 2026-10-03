# Endless Waters

## ⬇️ [Download for Minecraft Bedrock (.mcpack)](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Endless_Waters.mcpack)

**On your phone:** tap the download link above, then open **Endless_Waters.mcpack** with Minecraft. Once it imports, enable **Endless Waters — Depths** in your new world's **Behavior Packs**.

An intentionally simple Minecraft Bedrock add-on: the Overworld is endless water with procedurally varied seabed depths and no exposed land.

## What it does

- Replaces newly generated Overworld surface columns with water.
- Keeps a solid stone seabed so the world remains mineable and survivable.
- Varies water depth continuously by deterministic world-coordinate noise.
- Includes shallow shelves, normal ocean, deep ocean, and trench-like areas.
- Does not add land, islands, structures, custom blocks, custom items, or custom loot.
- Leaves the Nether and End unchanged.

This is for a new normal/infinite Bedrock world. Activate the behavior pack before creating the world. The pack targets Bedrock 26.50+ and uses no experimental toggles or custom scripts.

## Install on a phone

1. Download the `.mcpack` link above.
2. Open it with Minecraft.
3. Create a new normal, infinite Overworld.
4. Activate **Endless Waters — Depths** under Behavior Packs.
5. Enable cheats, then create the world.

The pack only controls newly generated chunks, so adding it to an existing world will leave previously generated land in place. Do not use Flat world generation.

## Build

```sh
python3 tools/build.py
python3 tools/validate.py
```

The generated package is `dist/Endless_Waters.mcpack`.
