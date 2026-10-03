# Seabed test notes

The procedural seabed prototype was promoted to **Endless Waters v0.3.0** and
replaces v0.2.1. The measured prototype and release have identical generation
files; release packaging restores the installed pack IDs and names for upgrades.

## Approach

- Keep water at vanilla sea level, Y=62.
- Leave already-submerged terrain in place, including native ocean floors and
  riverbeds. Use non-freezing ocean climates and vanilla ocean surface materials.
- Fill air above low dry floors up to Y=62. Converted land starts with a sandy
  surface, so low depressions and ledges do not retain underwater grass.
- Where solid terrain reaches above sea level, derive an underwater depth from
  the original seed-generated height. Former hills become broad basins; lower
  terrain becomes shallow water. This is procedural and has no finite map edge.
- Replace only the upper part of each affected column: a sandstone support layer,
  three sand layers, and water. Unspecified template cells preserve the rock,
  caves, and ores beneath the cap; templates never write below Y=0.
- Clear above-water terrain before surface vegetation runs. Bedrock then adds
  ocean vegetation, including kelp and seagrass, to the resulting floor.
- Keep the native lush-cave, dripstone-cave and deep-dark biomes. Exposed caves can
  admit water; cave decorations and ore placements need not match vanilla exactly.
- Vanilla structures are not a preservation requirement for this experiment.
  No new structures, items, blocks, or loot are added.

The biome test must run at Y=62, followed by an offset to the template origin at
Y=0. Testing the biome at Y=0 can select a cave biome instead of the surface ocean
and leave whole patches of land unchanged.

## Build and validate

From the repository root:

```sh
python3 tools/build.py
python3 tools/validate.py
```

The builder regenerates the behavior and resource packs, then packages
`dist/Endless_Waters.mcaddon`. Import it and enable **Endless Waters — Depths** and
**Endless Waters — Ocean Appearance** in a **new normal/infinite world**. Disable
any separately installed Seabed Preview packs. No experiments or runtime addon
scripts are required by the release.

## Bedrock integration checks

`probe.js` is a diagnostic script for a separate test pack, not part of the addon.
It loads five 16×16 samples in Bedrock Dedicated Server 1.26.52.3, seed 987654321,
and scans from Y=319 through Y=-64. Run it once with only the probe pack and once
with the preview plus the probe pack. Each `OCEAN_COMPARE` console record includes
floor heights, ice and vegetation counts, and a below-zero cave occupancy digest.
The test script uses `@minecraft/server` 2.10.0 and ticking areas to load samples
without a connected player.

Raw measurements are in `results/`. These are sampled engine checks, not proof
that every seed or coastline is correct. No phone performance test or in-game
visual review has been completed. The final height-limited clearing implementation
passed the same five checks as the original full-height clearing implementation.
Total measured area loading time fell from 92.3 to 31.1 seconds, versus 24.1 seconds
for vanilla. Each area load can generate surrounding chunks; these are neither
per-chunk benchmarks nor phone frame-rate measurements.

The control coral reef and the final preview had identical measured
floor heights and identical coral/sea-pickle counts. The successful preview had
zero ice, zero blocks above sea level, and water at sea level in all 1,280 columns.
Three additional samples on seed 42 passed the same checks, bringing the final
total to 2,048 columns across eight areas and two seeds. The final samples also
contained no underwater grass blocks or logs. See `results/final.json` and
`results/preview_seed42.json`; the other preview files record earlier iterations.
Below-zero cave air on the control seed remained 10,934 blocks versus 10,985 in the control; water and
cave decoration can change after the surface is opened. This does **not** establish
that every cave is unchanged or every underwater transition looks natural.
