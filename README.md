# Endless Waters

## ⬇️ [Download Endless Waters for Bedrock (.mcaddon)](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Endless_Waters.mcaddon)

**Version 0.3.0 replaces the old generator.** On your phone, tap the link above,
then open **Endless_Waters.mcaddon** with Minecraft. The file contains both packs.

## Install

1. Import the download into Minecraft Bedrock **26.50 or newer**.
2. Create a **new normal/infinite world**.
3. Enable **Endless Waters — Depths** in Behavior Packs.
4. Enable **Endless Waters — Ocean Appearance** in Resource Packs.
5. Create the world. No experimental toggles are required.

This import upgrades the old Endless Waters packs. If you also installed the
separate **Seabed Preview** packs, leave those disabled. Existing worlds retain
previously generated terrain, so use a new world for this version.

## What changed

- Water stays at vanilla sea level, **Y=62**.
- Existing submerged floors remain, including native ocean floors and riverbeds.
- Above-water land becomes a sloping procedural seabed, with depth derived from
  the world's original terrain. Exploration continues as new chunks generate.
- Dry depressions below sea level fill with water and use ocean surface materials.
- Surface climates become non-freezing oceans, including warm/lukewarm and deep
  variants. Native kelp, seagrass and coral can generate.
- Underground terrain, ores and caves beneath the new floor remain largely
  intact. Newly exposed cave openings can flood, and decorations can change.
- No custom blocks, items, loot or buildings are added. The Nether and End are
  unchanged. Vanilla structure preservation is not guaranteed.

## Tested

Bedrock Dedicated Server **1.26.52.3**: **2,048 columns across eight areas and two
seeds** had water at sea level, no above-water blocks, no ice, and no underwater
grass blocks or logs. The sampled warm-ocean reef matched vanilla floor heights
and coral counts. Caves remained in the sampled underground areas.

These are sampled engine checks, not a guarantee for every seed. In-game visual
quality and phone performance have not yet been tested. See the
[test notes and measurements](experiments/seabed/README.md).

## Build

```sh
python3 tools/build.py
python3 tools/validate.py
```

The phone-importable package is `dist/Endless_Waters.mcaddon`.
