# Endless Waters — detailed structure plan

Design proposal, 2026-11-02. The first original pirate galleon is now built as
[review assets: The Dreadwake](structure_previews/dreadwake/README.md), in new,
tattered and abandoned conditions. The user explicitly wants to see it before
integration. None of these structures are included in the addon yet. The
Legacy Boat Ruins previews were rejected as too basic.

## Build list

Sizes below are design targets in blocks, to be adjusted after preview and
Bedrock placement checks. Large structures should be destinations worth
exploring, with furnished interiors and distinct silhouettes.

| Family | First build | Planned variants | Approximate scale |
| --- | --- | --- | --- |
| Surface ships | Three-masted pirate galleon with curved hull, layered stern, sails, rigging, anchors and three accessible decks | Merchant carrack with cargo cranes and stalls; lean pirate frigate with gun deck; exploration ship with chart room and dive equipment | 65–100 long, 19–29 wide |
| Raft villages | Large settlement of connected timber pontoons around an open-water harbor, with 12–18 furnished buildings | Fishing village with drying racks and net sheds; trading port with market, inn and warehouses; salvage settlement built around a retired ship hull | 100–140 across, with irregular edges and water lanes |
| Shipwrecks | Wreck adapted from the finished galleon, retaining recognizable rooms and structural ribs | Upright breached hull; bow and stern separated by a debris trail; ship resting on its side; reef-encrusted wreck with collapsed decks | 55–100 long; debris may extend farther |
| Crashed submarines | Large research submarine with rounded hull, bridge, crew quarters, laboratory, engine room and dive bay | Nose buried in sediment; split hull with exposed machinery; tilted wreck with tangled growth; smaller exploration sub as a separate design | 50–85 long for the large sub; 25–35 for the smaller one |
| Abandoned underwater bases | Connected habitat modules with observation dome, laboratories, sleeping quarters, storage and a moonpool | Breached research station; industrial salvage/mining station; overgrown observatory with collapsed connecting tunnels | 65–110 across, assembled from smaller modules |
| Ancient underwater ruins | Sunken temple complex with courtyard, statues, arches, side chambers and a buried lower sanctuary | Sandstone temple with collapsed roof; prismarine archive with reading halls; ruined town with streets and plazas; deepslate observatory with amethyst details | 45–90 across; ruined town up to 120 |

## Detail standard

- Ships need shaped bows and sterns, visible ribs, layered trim, varied sail
  shapes and believable rigging. Furnish the captain's cabin, crew berths,
  galley, chart room, workshop and hold. Decks and cabins must be reachable.
- The raft village needs visible floats, braces, joining bridges, working
  docks and several building sizes/heights. Include homes, workshops, market,
  inn, storage and small raised farm beds. Keep open water between districts;
  the settlement is supported by built pontoons, without creating an island.
- Submarines and bases need distinct rooms, machinery, windows, pipes and
  passageways. Give each abandoned build a visible cause of failure: collision,
  collapse, hull breach or overgrowth. Any dry spaces must be intentional.
- Ancient ruins need a coherent architectural style, readable former room
  functions, broken arches and statues, weathering and partial burial.
- Variants must change layout, silhouette, room use or the route through the
  structure. Recoloring or randomly deleting blocks is insufficient.
- Loot and encounter design come after the build is worth exploring. The
  first visual pass can use vanilla blocks plus our existing decorative blocks.

## Decorations to develop alongside the builds

| Set | Proposed decorations |
| --- | --- |
| Ships and raft settlement | Anchors, ship wheels, ropes, sails, nets, cargo crates, buoys, dock lights and hanging signs |
| Submarines and bases | Pipes, valve wheels, gauges, cable bundles, bulkhead panels, equipment lockers and lamps |
| Ancient ruins | Carved pillars, mosaics, broken statuary, urns and patterned stonework |

Ocean Overhaul's anchor, ship wheel, rope and tattered-sail assets are candidates
for adaptation under that project's MIT license. They are not implemented yet.
Each decoration can start as a vanilla block assembly; custom models should
serve the build and remain readable with mobile graphics settings.

## Work order and previews

1. **Detailed pirate galleon:** settle its exterior and furnished interior first.
   It establishes the detail standard and provides a foundation for wrecks.
2. **Large raft village:** design its harbor and districts, then individual
   furnished buildings and docks.
3. **Shipwrecks:** adapt the accepted ships into distinct underwater layouts.
4. **Crashed submarine**, then the **abandoned underwater base**.
5. **Ancient temple**, then the archive, ruined town and observatory.

Work through one family at a time with the user before expanding its variants.
For each first build, provide a floor plan, exterior views from several sides,
and interior/cutaway views. Show the actual block build where possible; label
any concept drawing or approximate render clearly. The previous cube-only NBT
previews are not sufficient to judge the detail of these builds.

The user wants to review structures before they are added to generation.
Preview acceptance comes before integration and publishing a new addon.

## Building in Bedrock and handing over the result

The user can build the originals in Bedrock. Work through one finished build
and its variants at a time; the assistant can handle extraction, adaptation,
placement, loot setup and addon packaging after receiving the files.

1. Use a separate Creative build world and enable coordinates. Build with
   vanilla blocks or Endless Waters blocks; record any other required packs.
2. Complete the exterior and interior of one structure. Leave space around it
   so its boundaries are easy to identify. A ship can be built in water or in
   an empty work area; record the intended waterline either way.
3. Share a `.mcstructure` export, or a copy of the Bedrock world (`.mcworld` or
   a ZIP of its world folder) with the build's coordinates. Two opposite
   bounding corners are ideal. Close the world before copying its files.
4. Note the structure name, intended seabed/surface placement, rooms that should
   remain dry, and any mobs or loot you want. Screenshots are useful references
   but the block/world file is needed for an exact import.
5. Review the extracted build, then make variants and test generated placement.

On Windows Bedrock, obtain a structure block with `/give @s structure_block`,
select the build in Save mode, and export a `.mcstructure`. Do not choose 3D
Export: that creates a `.glb` model instead of a Minecraft structure. Microsoft
documents the import/export buttons as Windows-only, so mobile handoff should
use a world copy; the file-access steps depend on iPhone/Android and storage
settings. Save to Disk inside a structure block is not the same as exporting
a shareable file.

The documented structure-block selection limit is 64 blocks on each horizontal
axis. Do not shrink the planned ships or raft village just to fit one export:
larger builds can be split into pieces, or handed over as a complete world for
extraction and subdivision.

Source: [Microsoft's structure-block guide](https://learn.microsoft.com/en-us/minecraft/creator/documents/structures/introductiontostructureblocks?view=minecraft-bedrock-stable).

## Integration constraints

Preserve the approved ocean terrain and cave generator. Surface structures
must survive the final above-water cleanup pass. Underwater structures need
depth-aware placement, restrained foundations and local sediment blending;
do not flatten large areas or fill surrounding caves to fit a build.

Large builds may need several structure pieces. Check every supported rotation,
water-filled rooms, intended air pockets, chest contents, seams, terrain fit,
reload behavior and repeat placement. Test placement cost and guest joining on
Bedrock before enabling dense generation. The existing multiplayer join issue
is still unresolved; a successful visual preview would not resolve it.

Surface vessels and raft villages are static generated builds in this plan.
No moving-ship system is proposed. Major villages/bases should be rare landmarks,
with smaller wrecks and ruins providing more frequent discoveries. Exact
spacing and loot remain to be decided through playtesting.

## Research leads

These are leads to inspect, not approved imports or tested Bedrock structures.
No downloaded mod code was executed during research.

| Lead | What the source offers | Current decision |
| --- | --- | --- |
| [Ultimate Pirate Ship Survival Base](https://www.schemcraft.com/schematics/ultimate-pirate-ship-survival-base) | Listing describes a furnished three-masted ship and labels the schematic CC BY 4.0 | Promising ship candidate, but actual asset quality and original-author provenance are not verified; no import yet |
| [Dome Helm Nuclear Submarine](https://www.minecraft-schematics.com/schematic/11549/) | Author lists a 141 × 47 × 43 submarine with several furnished machinery rooms | Much larger than our initial target; modification is mentioned, but addon redistribution permission is not established. Contains command-block systems; not downloaded or run |
| [Water Village](https://www.planetminecraft.com/project/water-village-3883130/) | Author provides a furnished water village schematic and allows credited use in worlds/servers | Public redistribution of a converted addon asset is not established; visual reference only for now |
| [Sunken Spires](https://modrinth.com/project/sunken-spires) | Ancient prismarine ruins, a temple, city and other structures | Project is marked All Rights Reserved. Its modpack/world/server allowance does not establish permission to adapt and republish its structures in this addon |
| [Trek](https://modrinth.com/datapack/trek) | Ships and ruins among a larger Java structure collection; linked author repository has MIT text | Keep as a candidate, pending inspection of the actual asset archive and selected builds |

No complete, detailed, redistribution-ready collection covering all six
families has been verified. Original builds following the plan above are the
fallback, with reusable third-party candidates considered individually.
