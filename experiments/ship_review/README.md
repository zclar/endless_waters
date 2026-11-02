# Dreadwake Shipyard — playable Bedrock review world

**[Download Dreadwake_Shipyard.mcworld](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Dreadwake_Shipyard.mcworld)**

On Android, download the file and open it with Minecraft. After the import,
choose **Dreadwake Shipyard** from your Worlds list. Use Bedrock **26.60 or
newer**; this world was built and tested with the official 26.61 server.

This is a separate flat Creative world with three water docks and a labeled
boardwalk. All ships, furnishings, loot and mobs are already saved in the world.
There are no required behavior/resource packs, experimental toggles, setup
commands or scripts to run. It does not change your Endless Waters world.

## Explore the ships

| Dock | Variant | Crew | Stocked loot containers | Main-deck teleport |
| --- | --- | --- | --- | --- |
| West | New | 12 pillagers, including a captain | 13 | `/tp @s 20 -45 42` |
| Middle | Tattered | 8 pillagers, including a captain | 13 | `/tp @s 116 -45 42` |
| East | Abandoned | None | 5 | `/tp @s 212 -45 42` |

You start on the boardwalk at **120, -51, -10**. Fly around in Creative, or use
the side boarding ramps and ladders. Each ship has interior stairs between
the main deck, gun deck and lower hold. The raised foredeck and quarterdeck
have separate stairs. The cabin is at the stern.

The pillagers ignore Creative players. To test combat, give yourself equipment
and use `/gamemode survival`; return with `/gamemode creative`. Keep difficulty
on **Normal** if you want the crews to remain. Peaceful removes hostile mobs,
and this static review world does not respawn or restock them automatically.
Reimport the download to get a fresh copy.

## Furnishings and loot

The ships have bunks, two usable beds apiece, mess tables with cakes, a galley,
brewing equipment, pantry, workshop, cargo stacks, brig, a captain's chart table
with candles, canopy bunk, bookcases and navigation supplies. Workstations and
containers use vanilla blocks; cannons, wheel and most bunks are decorative.

The captain's chest holds valuables; navigation storage has a compass, spyglass,
paper and books. Other containers have arrows, a crossbow, tools, food, timber,
coal, string and metals. The abandoned ship has fewer supplies and small hidden
salvage stashes. All loot items are vanilla. These fixed review-world supplies
are not the final random loot tables for future ocean generation.

Many barrels remain empty cargo decoration. Search the captain's cabin, the
galley, workshop, upper cargo barrels and the brig. Looting or killing the crew
is saved normally; neither is reset when you reopen the world.

## Validation and reproduction

`validation.json` records the real engine build and reload checks. The builder
resolves every palette entry, checks every solid ship block, tests the dry hold
cells after water simulation, verifies each stocked inventory and each crew's
count, health and crossbow equipment. The final archive contains native world
data and empty pack lists; the diagnostic pack is omitted.

Phone rendering, touch controls and real network multiplayer still need user
testing. This world does not claim to fix the earlier Endless Waters guest-kick
report. The ships are not enabled in Endless Waters ocean generation yet.

The build sources are `build_world.js`, `contents.json`,
`tools/build_ship_review.py`, `tools/bedrock_world.py` and `tools/pirate_ship.py`.
The server binary is downloaded separately from Mojang and is not redistributed.

For developers: prepare a stopped official server with a generated
`worlds/metadata-seed/level.dat`, then run:

```sh
python3 tools/build_ship_review.py prepare --server-dir /path/to/server
# Start BDS, wait for DREADWAKE_READY, then stop it cleanly.
# Restart BDS, wait for DREADWAKE_RELOAD_READY, then stop it cleanly.
python3 tools/build_ship_review.py package --server-dir /path/to/server
```

Load both ship pieces in the same tick before allowing fluid simulation.
Staggering the pieces can let water into the unfinished hull and wash away
interior carpet. The temporary builder uses named/tagged vanilla pillagers
for persistence, removes only its own tagged crew when retrying a failed build,
and skips construction entirely after a successful build.
