# Endless Waters

## ⬇️ [Download for Minecraft Bedrock (.mcaddon)](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Endless_Waters.mcaddon)

**On your phone:** tap the download link above, then open **Endless_Waters.mcaddon** with Minecraft. It imports both packs. Enable **Endless Waters — Depths** in your new world's **Behavior Packs** and **Endless Waters — Ocean Appearance** in **Resource Packs**.

**Version 0.2.1 fixes freezing.** Import this update and create a **new world** with the packs enabled. Previously generated ice and old biome data remain in existing worlds.

An intentionally simple Minecraft Bedrock add-on: the Overworld is endless water with procedurally varied seabed depths and no exposed land.

## What it does

- Generates an ocean-only Overworld with no exposed land or islands.
- Preserves native caves, ores, and underground terrain below the new seabed.
- Varies water depth continuously by deterministic world-coordinate noise.
- Includes warm and lukewarm oceans, deep warm and deep lukewarm oceans, and the vanilla deep ocean and deep cold ocean variants. None use a freezing climate.
- Procedural ocean floors use 16–30 block water depths in normal oceans and 31–59 block depths in deep oceans. Existing ocean depths remain natural.
- Replaces Overworld surface climates with non-freezing ocean climates: no frozen biomes, icebergs, or natural surface ice. Native cave biomes remain available underground.
- Preserves existing ocean floors. Tested vanilla ocean monuments remain intact; the pack does not add custom structures, blocks, items, or loot.
- Surface biomes are exclusively oceans, so land settlements such as villages, outposts, mansions, and temples are excluded. Native cave biomes and underground structures remain available.
- Leaves the Nether and End unchanged.

This is for a new normal/infinite Bedrock world. Activate the behavior pack before creating the world. The pack targets Bedrock 26.50+ and uses no experimental toggles or custom scripts.

**Current limitation:** Bedrock generates the original terrain and native structures before this pack removes exposed land and creates the ocean floor. Ocean structures are not guaranteed in areas that originally generated as land; a structure locator can report a location where no structure survives. This version prioritizes endless, ice-free ocean. Custom structures and items are not included yet.

## Install on a phone

1. Download the `.mcaddon` link above.
2. Open it with Minecraft.
3. Create a new normal, infinite Overworld.
4. Activate **Endless Waters — Depths** under Behavior Packs.
5. Activate **Endless Waters — Ocean Appearance** under Resource Packs.
6. Create the world.

The pack only controls newly generated chunks, so adding it to an existing world will leave previously generated land in place. Do not use Flat world generation.

## Build

```sh
python3 tools/build.py
python3 tools/validate.py
```

The generated package is `dist/Endless_Waters.mcaddon`. Both the behavior pack and resource pack are bundled in this one phone-importable download.
