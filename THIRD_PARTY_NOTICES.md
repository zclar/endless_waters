# Third-party content

Endless Waters v0.5.0 includes an unofficial Bedrock adaptation of jellyfish,
seahorses, three diving-kit items and four decorative blocks from
[Ocean Overhaul](https://github.com/VoX/ocean-overhaul), by
tinyclaw / VoX, copyright (c) 2026 tinyclaw / VoX, licensed under MIT.

- Pinned source: `c92b8faddec30aa6cc3664b2a3727e2dfee64440`.
- Unmodified source references, eighteen original textures, the complete license and
  a file-hash inventory are in `third_party/ocean_overhaul/`.
- Cuboid dimensions, UV coordinates and animation designs were adapted from the
  original Java models. Bedrock entity behavior, spawn rules, geometry conversion
  and pack definitions are implemented in `tools/sea_life.py`. Diving behavior,
  recipes and block definitions are rebuilt in `tools/diving_buildables.py` and
  `scripts/diving_gear.js`. PBR material settings are added by Endless Waters.
- Both imported packs contain the full MIT license and attribution notice.

This release does not include the full Java
mod, its bosses, buckets, coral affinity behavior, or its
custom renderer. Jellyfish use Bedrock's built-in translucent material; their
Java full-bright rendering is not reproduced in this version.

No Hopo or Moog structure assets or code are included in the distributed addon.

## Decoration expansion (0.6.0)

- **FurniDeco**, Arexon, Apache-2.0: https://github.com/arexon/furnideco
  (`dec73938eca679d2d0641afe3af51b122e2d63c3`). Geometry and textures adapted;
  identifiers, block definitions, recipes and interactions rewritten for modern
  Bedrock. Original source assets and license: `third_party/furnideco/`.
- **Farmer's Delight**, vectorwing, MIT: https://github.com/vectorwing/FarmersDelight
  (`dd8b9b0bfec916a2da88a6d64e3a37f4a02c3259`). Selected food textures and galley
  models adapted. No Java cooking/farming system is included. Original source
  assets and license: `third_party/farmers_delight/`.
- **Ocean Overhaul**, same pinned version above: additional building/nautical
  models, food and harpoon textures. Aquarium and clam are decorative. Harpoon
  behavior is original Bedrock code, without the Java loyalty-return behavior.

Each source has a `decor_source.json` hash receipt. Distributed packs carry the
licenses and attribution. No upstream scripts are executed. New clutter models,
ship designs, loot tables and Bedrock conversion code are original to this project.
This is a selection of adapted assets, not a complete port of these mods.
