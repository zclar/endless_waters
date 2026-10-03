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
mod, its bosses, buckets, aquarium, coral affinity behavior, or its
custom renderer. Jellyfish use Bedrock's built-in translucent material; their
Java full-bright rendering is not reproduced in this version.

No Hopo or Moog structure assets or code are included in the distributed addon.
