# v0.5.0 sea-life validation

The release uses stable `@minecraft/server` 2.10.0 for diving equipment and has
no experimental dependencies. Diagnostic scripts here run in separate
server-only test packs, never in the download.

## Engine checks

Bedrock Dedicated Server **1.26.52.3**, seed **987654321**, warm-ocean sample around
X=-2000, Z=1200. `probe.js` requires `@minecraft/server` 2.10.0.

Recorded in `results/runtime.json`:

- Spawned 20 jellyfish and 20 seahorses; each species produced all five colors.
- Explicit color changes selected the expected variant for every creature.
- All 40 moved at least 0.1 blocks during 240 ticks and retained full underwater
  health. None breached the surface during that interval.
- Two dry-land controls died from lack of water within 440 ticks.
- Killing 32 jellyfish produced 14 item entities, all vanilla slime balls.
- All 40 kept creatures survived a real server restart with their colors intact.
  The reload check loads neighboring chunks because free-swimming animals can
  leave the initial sample area before shutdown.

The first test exposed an invalid nameable trigger schema, corrected to an
event/target object. Subsequent final-pack runs loaded without that error.
Persistence/despawn components do not have Script API component wrappers;
retention is checked through engine saving/loading instead of `hasComponent`.

To reproduce, create a separate script behavior pack using `probe.js` as its
entry point, enable it alongside both v0.5.0 packs in a fresh world of the seed
above, and run until `SEA_LIFE_READY_RELOAD`. Stop/restart the server, then expect
`SEA_LIFE_TEST_DONE`. A failure is printed as `SEA_LIFE_TEST_FAIL`. The dry-land
test places a small glass platform in the temporary test world.

## Natural spawning

`natural_spawn_probe.js` uses a simulated Creative player at (-2000, 63, 1200)
for two minutes, with the release's unmodified spawn rules and no summoned
creatures. Both species appeared alongside vanilla water mobs: seahorses were
first observed at 30 seconds, jellyfish at 100 seconds. At 120 seconds the sample
contained three seahorses and one jellyfish. These are observed counts, not
guaranteed encounter rates. See `results/natural_spawning.json`.

For this test only, the separate diagnostic pack adds `@minecraft/server-gametest`
`1.0.0-beta`, and the test world's `gametest` experiment is enabled. That module
provides the simulated player; neither it nor experiments are required by the
addon. The diagnostic pack manifests are included here for reproducibility.

## Gear and interactions

`gear_probe.js`, using the same isolated GameTest manifest/world, checks actual
equipment slots, effects, underwater movement, held-item placement, block drops,
spawn eggs and name tags. Results are in `results/gear.json`.

- Helmet vision and tank breathing appeared with all three pieces equipped.
- Underwater movement changed from approximately 0.02 to 0.03; it stayed at
  0.03 rather than compounding on later polls and returned to 0.02 on removal.
- Breathing expired after removal; a stronger external night-vision effect
  was preserved. A dry-land helmet check did not grant night vision.
- All four building blocks placed and dropped their own item when destroyed.
- Both Creative eggs spawned their animal and both accepted a real name tag.

Copy the release's `scripts/diving_gear.js` unchanged beside the diagnostic
script. Bedrock exposes GameTest-created simulated players only in a script
context importing GameTest; another pack's `getAllPlayers()` returned undefined
entries for them. The production loop now safely skips missing entries. The
test-context copy runs the exact same equipment logic against the engine's
simulated player without adding GameTest to the shipped pack.

The final release also loaded in the non-experimental `ocean-050-sea-life-v2`
world with no content or scripting errors; all 40 saved creatures passed the
reload check again. This headless run cannot verify client PBR rendering.

The first placement run respected too little simulated-player item-use cooldown;
allowing ten ticks between uses fixed the diagnostic without a block change.
Recipe dependency/asset checks are static; full touch-screen crafting and armor
rendering remain client checks. The movement test verifies the engine attribute,
not a measured swimming-distance ratio.

## Asset and regression checks

`python3 tools/validate.py` also validates:

- All 294 biome, generation-feature and terrain-template files match the
  approved v0.4.0 commit `faf7de8` byte for byte, using the stored baseline hashes.
- Model parent hierarchy, UV bounds, texture dimensions and file references.
- Animation bone references, client render-controller links and all five textures.
- Spawn-rule water/height restrictions and population limits; entity event links.
- Unmodified upstream source/texture hashes and full MIT notices in both packs.
- Archive contents exactly match generated files and exclude all test scripts.
- All seven recipes resolve through an acyclic chain to vanilla ingredients.
- Equipment icons/attachables, block loot and all eighteen PBR texture sets
  resolve to assets; no global visual settings or vanilla textures are replaced.

The models are rebuilt from the upstream cuboid dimensions and UV coordinates.
Java's downward Y axis is reflected into Bedrock's upward Y axis; animation
timing converts Java radians/ticks into Molang degrees/seconds.

## Limits

The headless dedicated server cannot render resource-pack models. Model links
and geometry are checked statically; actual phone appearance, transparency,
animations, touch interactions and frame rate still require an in-game check.
The upstream Java full-bright jellyfish renderer and bucket capture/release
are not included in this first adaptation.
