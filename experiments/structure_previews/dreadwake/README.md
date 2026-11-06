# The Dreadwake — pirate galleon, furnished edition

**Preview only. This ship has not been added to the Endless Waters addon or
world generation.** Review the design before integration.

**Now playable:** [download the separate flat shipyard world](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Dreadwake_Shipyard.mcworld)
with fully furnished interiors and actual pillager crews.
[Instructions and coordinates](../../ship_review/README.md).

An original block-built galleon, **111 blocks long** including its rudder, up to **43 blocks across
the sails**, with a **31-block hull beam**. The new and tattered versions are
74 blocks tall from keel to masthead; the abandoned version has broken upper
masts and is 65 blocks tall. The padded export envelope is 49 × 76 × 116.

**[Download the pictures and offline 3D viewer](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Dreadwake_Ship_Previews.zip)**

On Android, unzip the download and open the PNG images. `VIEW_SHIP.html` is an
optional offline WebGL viewer: open it in a browser, drag to rotate and pinch
to zoom, switch variants, and use the deck selector to inspect interiors.
Some Android file apps cannot launch local HTML correctly; the PNGs need only
an image viewer. No Minecraft import is needed for these previews.

## Three conditions

| New | Tattered | Abandoned |
| --- | --- | --- |
| Complete sails, bright trim, furnished interiors; 12 planned pillagers | Torn and patched sails, repaired rails, weathered planking; 8 planned pillagers | Broken upper masts, hanging sail remnants, breached decking, moss and broken cabin windows; no crew |
| [Full-size bow view](new.png) | [Full-size bow view](tattered.png) | [Full-size bow view](abandoned.png) |
| [Full-size stern view](new_stern.png) | [Full-size stern view](tattered_stern.png) | [Full-size stern view](abandoned_stern.png) |

![New Dreadwake](new.png)

![Tattered Dreadwake](tattered.png)

![Abandoned Dreadwake](abandoned.png)

## Inside the ship

- Lower hold with crew berths, cargo, brig and treasure vault.
- Gun deck with twelve decorative cannons, ammunition, galley and mess.
- Main deck with a cargo grating, capstan, stowed dinghy and boarding ladders.
- Captain's cabin with canopy beds, chart table, instruments, books and seating.
- Raised forecastle and quarterdeck, stern gallery, decorative wheel,
  anchors, figurehead, crow's nests and climbable mast ladders.
- Stern rudder, mooring bitts on the raised decks, and a ringable vanilla bell.

| Interior section | Gun deck |
| --- | --- |
| ![Interior section](interior_section.png) | ![Gun deck](gun_deck.png) |

| Lower hold | Main deck and cabin |
| --- | --- |
| ![Lower hold](lower_hold.png) | ![Main deck and cabin](main_deck.png) |

## What the previews represent

These are renders of the actual block layouts saved in the `.mcstructure`
templates, not AI concept paintings or Minecraft screenshots. Slabs, stairs,
fences and several furniture blocks have approximate geometry. Materials use
approximate colors rather than Minecraft textures. The water plane is a visual
reference, and the viewer's crew markers represent planned pillager positions.

The cannons, rudder, wheel and rigging are decorative vanilla-block assemblies;
the ship does not sail and cannons do not fire. Interior furnishings include custom furniture and clutter plus 30 native loot
chests per ship. Custom model previews approximate cube geometry and omit bone rotations. Exterior cargo
barrels remain empty. Standalone preview templates omit the review world's crew
assembly. No third-party structure assets are used.

## Validation and remaining work

`validation.json` records checks that each NBT piece matches its preview block
layout, all crew positions have floor/headroom, the hull is sealed below the
waterline in a voxel flood test, and loot-bearing chests have native randomized table references.
Each variant is exported as two pieces within the 64-block horizontal limits.

The playable shipyard's [engine validation](../../ship_review/validation.json)
covers structure loading, dry and clear interiors, empty deck barrels, crew equipment and persistence
across a restart. World-generation placement, complete survival pathfinding,
phone graphics and multiplayer still need further testing. The interactive
viewer is an additional inspection tool; it is not a Bedrock simulator.

Rebuild from the repository root:

```sh
python3 tools/pirate_ship.py
python3 tools/render_pirate_ship.py
python3 tools/validate_pirate_ship.py
```
