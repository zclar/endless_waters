# Endless Waters

## ⬇️ [Download Endless Waters for Bedrock (.mcaddon)](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Endless_Waters.mcaddon)

**Version 0.4.0 — deeper oceans and floating-structure cleanup.** On your phone, tap the link above,
then open **Endless_Waters.mcaddon** with Minecraft. The file contains both packs.

## Install

1. Import the download into Minecraft Bedrock **26.50 or newer**.
2. Create a **new normal/infinite world**.
3. Enable **Endless Waters — Depths** in Behavior Packs.
4. Enable **Endless Waters — Ocean Appearance** in Resource Packs.
5. Create the world. No experimental toggles are required.

This import upgrades the old Endless Waters packs. If you also installed the
separate **Seabed Preview** packs, leave those disabled. Existing worlds retain
previously generated terrain. Use a new world for consistent terrain throughout,
or explore new chunks to see the update. Existing floating portals and sugar cane
in explored chunks are not removed by importing the update.

## What changed

- Water stays at vanilla sea level, **Y=62**.
- Shallow seabeds are deepened along their existing contours, starting around
  18 blocks of water. Floors already at least 36 blocks deep retain their heights.
- Above-water land becomes a sloping procedural seabed, with depth derived from
  the world's original terrain. Exploration continues as new chunks generate.
- Dry depressions below sea level fill with water and use ocean surface materials.
- Surface climates become non-freezing oceans, including warm/lukewarm and deep
  variants. Native kelp, seagrass and coral can generate.
- Most former land biome types now become deep ocean types. Warm/lukewarm
  regions have sandy floors; regular/cold deep regions have gravel. These are
  vanilla ocean materials, with temperatures kept above freezing.
- A final generation pass clears everything above sea level, including floating
  ruined portals and sugar cane. It runs during generation, never over player builds.
- Underground terrain, ores and caves beneath the new floor remain largely
  intact. Newly exposed cave openings can flood, and decorations can change.
- No custom blocks, items, loot or buildings are added. The Nether and End are
  unchanged. Vanilla structure preservation is not guaranteed.

## Tested

Bedrock Dedicated Server **1.26.52.3**: two reproduced floating-portal sites
contained **64 and 187 above-water blocks** in v0.3.0 and **zero** in v0.4.0.
Both updated samples retained underground caves, kelp and seagrass, with no ice
or underwater grass/logs.

An additional **2,048-column survey across eight areas** found depths from
**18 to 55 blocks**, no above-water blocks or ice, and both sand and gravel floors.
Deliberate above-water test blocks were cleared, while underground markers
remained. The warm reef sample still generated coral and sea pickles.

These are sampled engine checks, not a guarantee for every seed. In-game visual
quality for this update and phone performance still need a player check. See the
[v0.4.0 test notes and measurements](experiments/depths/README.md) and the
[historical v0.3.0 tests](experiments/seabed/README.md).

## Build

```sh
python3 tools/build.py
python3 tools/validate.py
```

The phone-importable package is `dist/Endless_Waters.mcaddon`.
