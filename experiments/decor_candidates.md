# Decorations and items research — 2026-11-05

Direction: assemble a reusable decoration/item library before furnishing the
Dreadwake heavily. Historical research notes; the selected adaptations are now
implemented in v0.6.0. See [catalog and scope](decor/README.md) and the runtime
validation in `ship_review/validation.json`. No downloaded code was executed.

## Best candidates

| Source | Useful content | Reuse and implementation status |
| --- | --- | --- |
| [Ocean Overhaul](https://github.com/VoX/ocean-overhaul) | Nautical hardware, driftwood building set, ocean ornament blocks, aquarium, harpoon | [MIT](https://github.com/VoX/ocean-overhaul/blob/main/LICENSE). Java source: selected content needs Bedrock adaptation, especially interactive mechanics. Existing adaptation covers only a subset; do not duplicate existing items. |
| [FurniDeco](https://github.com/arexon/furnideco) | Author advertises 25 furniture/decor types and 80+ variants, craftable and interactive | [Apache-2.0](https://github.com/arexon/furnideco/blob/main/LICENSE). Native Bedrock source. Preserve notices/license and identify changes. Current-engine compatibility and exact selected models still need inspection; not tested with Endless Waters. |
| [Farmer's Delight](https://github.com/vectorwing/FarmersDelight) | Cooking pots, stoves, cutting boards, baskets, cabinets, produce crates, sacks, rope/netting, food and drink items | [MIT](https://github.com/vectorwing/FarmersDelight/blob/1.21/LICENSE). Java source: adapt selected props and recipes; full farming/cooking system is a separate scope. [Item/block inventory](https://github.com/vectorwing/FarmersDelight/blob/1.21/src/main/resources/assets/farmersdelight/lang/en_us.json). |

These are candidates under repository licenses, not an asset-by-asset clearance
or a claim of working ports. Pin revisions and check selected asset notices before
import, preserve attribution, then test placement, drops, crafting, saving and
multiplayer on Bedrock. Check submerged placement for underwater decorations.

## Not cleared for copying

- [Another Furniture license](https://github.com/crispytwig/AnotherFurniture/blob/1.21.1/LICENSE): resource directories are All Rights Reserved despite MIT code.
- [Supplementaries license](https://github.com/MehVahdJukaar/Supplementaries/blob/1.21.1/LICENSE.md): public redistribution and asset reuse restricted; permission needed.
- [Medieval Furniture remaster](https://github.com/shaiku/medieval): impressive advertised selection, but inspected repository did not establish permission from the original asset creator. Not approved for redistribution.

## Proposed original additions to fill gaps

These are our design ideas, not claims that the sources above contain them:

- Captain/navigation: rolled charts, open logbook, inkwell, sextant, mounted compass.
- Crew: hammocks, hanging coats, boots, mugs, personal lockers.
- Cargo: open/closed crates, rope coils, canvas bundles, sacks, strapped chests.
- Armory: weapon racks, cannonballs, powder kegs, repair tools.
- Underwater base: portholes, bulkhead doors, valves, pipes, gauges, consoles,
  lockers, oxygen cylinders and equipment racks.
- Salvage/ruins: broken pottery, coins, barnacled debris, damaged prop variants.

Suggested first milestone: roughly 30–40 distinct props across cargo, navigation,
crew and galley categories; color/wood/weathering variants are additional. Show
them together in a Creative display world before using them in ships. Add utility
items after the static props; avoid making new survival recipes depend on currently
unavailable ocean-structure resources. Detailed furnishing follows this library.
