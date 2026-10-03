# v0.4.0 depth and cleanup checks

Test engine: Bedrock Dedicated Server 1.26.52.3; seed 987654321.
These are sampled engine checks, not a guarantee for every seed or a phone
performance benchmark. The earlier v0.3.0 measurements remain in `../seabed/`.

## Changes under test

Shallow original floors are deepened along their original contours. Former
above-water terrain produces depths of `18 + 41*h/(h+10)`, where `h` is its
height above the shoreline. Original shallow water uses `18 + 0.5*depth`.
Selection rounds down to whole-block depths. Floors already at least 36 blocks
deep are preserved. Cave openings and later underwater decorations can affect
the measured top solid block. Terrain templates never write below Y=0.

Most former land biome types map to deep ocean types. Warm/lukewarm regions use
sand; regular/cold deep regions use gravel. Biome identity and physical depth
are separate: a coastal part of a deep biome can still be shallower.

A final world-generation pass clears Y=63 through Y=319. The old heightmap bound
missed late-generated ruined portals. Direct block placement over the full
range removes those remnants without relying on the heightmap. It only runs
while chunks generate; it does not scan existing chunks or player builds.

## Floating portals

`results/portals.json` records four v0.3.0 samples and two v0.4.0 regressions.
The two failing 32×32 sites contained 64 and 187 blocks above sea level; the
updated generator left zero at both. Both retained below-zero cave air, ores,
kelp and seagrass, with no ice, underwater grass/logs, or failed water surfaces.
Cave occupancy can change because newly exposed openings admit water.

An initial full-height structure-template cleanup also passed but loaded these
areas in 37.5 and 43.5 seconds. The shipped direct-block implementation took 8.8
and 17.0 seconds on the same machine. These timings include surrounding chunk
generation and are not controlled per-chunk benchmarks.

## Depth survey and fixtures

`probe.js` samples eight 16×16 areas, scanning Y=319 down to Y=-64. Depth means
62 minus the highest non-decoration solid block at or below sea level. The
`atLeast30` count uses 30 blocks as a measurement threshold, not a claim about
Minecraft's biome classification. Results are recorded separately from portal
regressions because the survey enables deliberate test fixtures.

`results/survey.json`: all 2,048 columns passed the water-surface, above-water,
ice, underwater-grass and underwater-log checks; all eight fixture markers
remained. Measured depths ranged from 18 to 55 blocks. Of these columns, 836
were at least 30 blocks deep. These deliberately chosen sites include known
shallow oceans and coasts; they do not establish a global deep/shallow ratio.
Seven areas retained below-zero cave air. The warm reef sample still generated
coral and sea pickles; other samples generated kelp and seagrass.

To reproduce, copy `probe_pack/` into a separate server behavior pack folder,
then copy `probe.js` to its `scripts/main.js`. Enable that test pack alongside
the generated v0.4.0 behavior/resource packs in a fresh seed-987654321 world.
It requires `@minecraft/server` 2.10.0 and uses ticking areas without a player.
Watch for `OCEAN_COMPARE` records and `OCEAN_COMPARE_DONE`.

The test pack places reeds at Y=64, obsidian at Y=100, and gold at Y=319 during
`after_surface_pass`. A diamond block at Y=-63 is a positive control proving
that the fixture rules ran. The release must have zero above-water blocks while
retaining that underground marker. Reeds can also break through ordinary block
updates; the solid fixtures independently check the full clearing range.

**The probe, fixture blocks, and scripts are never bundled in the download.**
