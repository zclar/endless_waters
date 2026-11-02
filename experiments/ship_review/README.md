# Dreadwake Shipyard — build edition

**[Download Dreadwake_Shipyard.mcworld](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Dreadwake_Shipyard.mcworld)**

On Android, download the file and open it with Minecraft. After the import,
choose **Dreadwake Shipyard - Build Edition** from your Worlds list. Use Bedrock
**26.60 or newer**; this world was built and tested with the official 26.61 server.
Import this download as a new world to get the changes; older imported copies
are not updated automatically.

This is a separate flat Creative world with three water docks and a labeled
boardwalk. The cabins and holds are cleared for your own interior builds.
There are no required behavior/resource packs, experimental toggles, setup
commands or scripts to run. It does not change your Endless Waters world.

## Explore and build

| Dock | Variant | Crew | Main-deck teleport |
| --- | --- | --- | --- |
| West | New | 12 pillagers, including a captain | `/tp @s 20 -45 42` |
| Middle | Tattered | 8 pillagers, including a captain | `/tp @s 116 -45 42` |
| East | Abandoned | None | `/tp @s 212 -45 42` |

You start on the boardwalk at **120, -51, -10**. Fly around in Creative, or use
the side boarding ramps and ladders. Each ship retains its decks, structural
beams, lighting, mast supports, interior stairs, cabin walls and windows.
The hull remains sealed below the waterline.

Bunks, beds, tables, carpets, bookshelves, galley, workshop, brig fittings,
interior cargo and loot containers have been removed from all three variants.
The lower hold, gun deck and captain's cabin are ready for your layouts.
The gun deck still has its twelve decorative cannons; the main deck keeps the
capstan, dinghy and empty cargo barrels. The wheel, anchors, sails and rigging
remain. Added details include a stern rudder, mooring bitts on the forecastle
and quarterdeck, and a ringable vanilla bell on the forecastle.

The rudder, cannons and wheel are decorative; the ships do not sail or fire.
There is no stocked loot or automatic furnishing in this build edition.
Any changes you make are saved normally.

The pillagers ignore Creative players. To test combat, give yourself equipment
and use `/gamemode survival`; return with `/gamemode creative`. Keep difficulty
on **Normal** if you want the crews to remain. Peaceful removes hostile mobs,
and this static world does not respawn them. Reimport to get a fresh copy.

## Validation and reproduction

`validation.json` records the real engine build and reload checks. The builder
resolves every palette entry, checks every solid ship block and the cleared
interior air cells, tests the dry hold after water simulation, verifies deck
barrels are empty, and checks each crew's count, health and crossbow equipment.
Reports include a fingerprint of the layout and builder so packaging requires
matching build and reload results. The final archive contains native world
data and empty pack lists; the diagnostic pack is omitted.

Phone rendering and real network multiplayer still need user testing. The
ships are not enabled in Endless Waters ocean generation yet.

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

The default folder is `dreadwake-review-shell`. Use `--world` with a fresh
folder when changing the layout. Load both ship pieces in the same tick before
allowing fluid simulation. The temporary builder uses named/tagged vanilla
pillagers for persistence and skips construction after a successful build.
