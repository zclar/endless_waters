# Dreadwake Shipyard — furnished edition

**[Download Dreadwake_Shipyard.mcworld](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Dreadwake_Shipyard.mcworld)**

On Android, open the download with Minecraft, then choose **Dreadwake Shipyard -
Furnished Edition**. Requires Bedrock **26.60+**. Import as a new world: previously
imported copies do not update. Both decoration packs are bundled and activated.
No experiments or setup commands are required.

This separate flat Creative world contains three water docks and a labeled
boardwalk. It does not change your ocean world; ships do not generate there yet.

| Dock | Variant | Crew | Main-deck teleport |
| --- | --- | --- | --- |
| West | New | 12 pillagers | `/tp @s 20 -45 42` |
| Middle | Tattered | 8 pillagers | `/tp @s 116 -45 42` |
| East | Abandoned | None | `/tp @s 212 -45 42` |

Spawn is **120, -51, -10**. Fly in Creative or use boarding ramps and ladders.
The interiors include six crew berths, cargo stores, a brig, an iron-door vault,
a galley and mess, ammunition racks, infirmary supplies and a furnished captain's
cabin with a chart table, instruments, books, seating and canopy beds.
Ropes, canvas, bottles, tools, lamps and loose equipment fill out the rooms.
The weathered variants lose some furnishings; the abandoned vault is breached.

Each ship contains **30 vanilla loot chests**, assigned room-specific native loot
tables. Contents roll when first opened, with weighted items, varying quantities
and occasional rare finds. Abandoned stores have a greater chance of missing
supplies. Reopening a chest does not reroll it. Decorative treasure chests and
cabinets are props; vanilla chests hold the actual loot. Deck barrels are empty.

The ships, cannons and wheel are stationary decorations. Furniture is primarily
decorative; selected props cycle styles or colors and lamps toggle on interaction.
See the [catalog](../decor/README.md). Keep Normal difficulty to retain pillagers;
Peaceful removes them permanently. Reimport to restore the original crews.

## Validation and reproduction

`validation.json` records official Bedrock server 1.26.63.1 build/reload checks:
every ship block, dry holds, clear interior cells, crew count and equipment,
registered decoration states, interactions, item availability and native loot
variation. Packaging requires successful build and reload reports. The temporary
diagnostic builder is excluded; the decoration runtime packs are included.

Phone rendering and real network multiplayer remain untested. Native loot tables
are exercised with disposable test containers; the actual ship chests remain
unopened for you. No third-party structure code is executed or redistributed.

```sh
python3 tools/build_ship_review.py prepare --server-dir /path/to/server
# Start BDS, wait for DREADWAKE_READY, stop cleanly.
# Restart BDS, wait for DREADWAKE_RELOAD_READY, stop cleanly.
python3 tools/build_ship_review.py package --server-dir /path/to/server
```

Use a fresh `--world` folder when changing layouts. The official server and its
seed metadata are supplied separately and are not redistributed.
