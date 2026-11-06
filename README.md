# Endless Waters

## ⬇️ [Download Endless Waters for Bedrock (.mcaddon)](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Endless_Waters.mcaddon)

**Version 0.6.0 — furniture, nautical decorations, foods and a recoverable harpoon.** On your phone, tap the link above,
then open **Endless_Waters.mcaddon** with Minecraft. The file contains both packs.

## ⛵ [Download the pirate-ship review world (.mcworld)](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Dreadwake_Shipyard.mcworld)

**Dreadwake Shipyard - Furnished Edition:** a separate flat Creative world with
new, tattered and abandoned ships, furnished cabins, crew quarters, galley,
cargo hold, brig and treasure vault. Each ship has 30 randomized loot chests;
the new/tattered ships have pillager crews. Open the file with Minecraft and
select **Dreadwake Shipyard - Furnished Edition**. Import as a new world.
Requires Bedrock **26.60+**; the included decoration packs activate with the world.
[World details and ship coordinates](experiments/ship_review/README.md).

**174 new catalog entries:** furniture, nautical and galley props, 14 foods,
and a throwable harpoon. Use a stonecutter with driftwood planks (or iron for
metal fittings) to select decorations. [Catalog, recipes and controls](experiments/decor/README.md).
Cabinets, seats and appliances are decorative; real ship storage uses vanilla chests.

## Install

1. Import the download into Minecraft Bedrock **26.60 or newer**.
2. Open your existing v0.4.0 world, or create a **new normal/infinite world**.
3. Enable **Endless Waters — Depths** in Behavior Packs.
4. Enable **Endless Waters — Ocean Appearance** in Resource Packs.
5. Create the world. No experimental toggles are required.

This import upgrades the old Endless Waters packs. If you also installed the
separate **Seabed Preview** packs, leave those disabled. Existing worlds retain
previously generated terrain. **Upgrading from v0.4.0 does not require a new
world:** the terrain generator is identical, and the new creatures can spawn in
existing ocean areas. If upgrading from v0.3.0 or earlier, a new world or new
chunks are needed for the v0.4.0 depth and floating-remnant fixes.

## Starting boat

On their first join after installing v0.5.2, each player receives one vanilla
oak boat and 30 seconds of water breathing. This also applies once in an
existing world upgraded from an earlier addon version. The grant is saved per
player, so reconnecting or respawning does not give additional boats. If their
inventory is full, the boat drops at their location. A stronger or longer
existing water-breathing effect is preserved.

## Multiplayer status

The reported guest join/kick is still under investigation. v0.5.2 reduces
unnecessary gear checks while players load and isolates errors per player;
it is not a confirmed fix for that disconnect. See the
[multiplayer test notes](experiments/sea_life/multiplayer_notes.md) for verified
checks and the next real-device comparison. The
[structure plan](experiments/structure_plan.md) covers detailed ships, large raft
villages, wrecks, crashed submarines, underwater bases and ancient ruins; only the separate pirate ship review world
is available so far. [Research candidates](experiments/structure_candidates.md)
are tracked separately.

**Pirate ship review:** [explore the playable shipyard](experiments/ship_review/README.md),
[see the pictures](experiments/structure_previews/dreadwake/README.md), or
[download pictures and the offline viewer](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Dreadwake_Ship_Previews.zip).
The ships are not included in the ocean addon yet.

## New sea life

- **Jellyfish:** five colors, translucent bells and swaying tentacles; occasional
  small groups in oceans. Passive, with a chance to drop a vanilla slime ball.
- **Seahorses:** five colors with animated tails and fins; uncommon solitary
  swimmers in warm/lukewarm oceans. Passive, with a rare vanilla bone-meal drop.
- Both have Creative spawn eggs. Name tags keep them from naturally despawning.
  They need water to survive. Bucketing is not implemented in this version.
- Spawn limits keep populations modest; actual encounter frequency depends on
  nearby water mobs. No experimental toggles are required.

These are adaptations from the MIT-licensed **Ocean Overhaul**,
not a port of the entire Java mod. See [credits and scope](THIRD_PARTY_NOTICES.md).

With cheats enabled, you can test them while swimming:

```mcfunction
/summon endless:jellyfish ~ ~ ~
/summon endless:seahorse ~ ~ ~
```

## Diving gear and building blocks

All seven additions have crafting-table recipes, ultimately using vanilla
ingredients. The recipe book shows their layouts after unlocking them.

| Addition | Ingredients | Use |
| --- | --- | --- |
| Deep-Sea Helmet | 5 iron ingots, 2 Sea Glass, 1 amethyst shard | Night vision while your head is underwater |
| Oxygen Tank | 7 iron ingots, 1 Sea Glass | Water breathing while worn |
| Flippers | 4 dried kelp, 2 iron ingots | 1.5× underwater movement attribute |
| 8 Sea Glass | 7 glass, 1 ink sac, 1 amethyst shard | Transparent building block |
| 3 Driftwood Planks | 3 oak planks, 1 dried kelp | Wooden building block |
| 4 Polished Prismarine Bricks | 4 prismarine bricks | Decorative stone |
| Pearl Lantern | 4 prismarine crystals, 1 sea lantern | Light level 15 |

Wear equipment in the head, chest and feet armor slots. Each piece works
independently. Flippers leave land movement unchanged. The helmet's vision
lingers for up to 15 seconds after removal to avoid repeated night-vision
flashing; breathing expires within five seconds. Stronger potion effects are
preserved. Repair the gear with iron ingots in an anvil.

Amethyst shards come from underground geodes; squid provide ink sacs. The suit
needs no guardian drops or ocean monument. Polished Prismarine Bricks and the
Pearl Lantern still use prismarine ingredients, so those optional decorations
may be hard to craft if a monument does not survive world generation.
No custom ore or loot ingredient is required. Gear bonuses use a small stable
Script API routine; it does not edit terrain.

## Prizma / Vibrant Visuals

The resource pack declares `pbr` support and includes material definitions for
all 18 new textures: rough wood, smoother glass/stone and an emissive lantern.
The original color textures remain available in Classic graphics. These are
initial material settings; their appearance has not been verified on a phone.

When using Prizma, put it **above Endless Waters — Ocean Appearance** in the
world's active resource packs, and select Vibrant Visuals on a supported device.
Test with one visual pack at a time. Endless Waters adds no global water,
lighting, fog, shader or color-grading files and replaces no vanilla textures.

**Compatibility is not yet confirmed for a particular Prizma/Vibrance version.**
Custom ocean biomes can use a visual pack's global defaults instead of its
vanilla-biome presets. A pack-specific biome bridge may still be necessary;
material support alone does not solve that mismatch. See the
[Bedrock biome visual-settings documentation](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/biomecustomization?view=minecraft-bedrock-stable).

## What changed

- Water stays at vanilla sea level, **Y=62**.
- Shallow seabeds are deepened along their existing contours, starting around
  18 blocks of water. Floors already at least 36 blocks deep retain their heights.
- Above-water land becomes a sloping procedural seabed, with depth derived from
  the world's original terrain. Exploration continues as new chunks generate.
- Dry depressions below sea level fill with water and use ocean surface materials.
- Surface climates become non-freezing oceans, including warm/lukewarm and deep
  variants. Native kelp, seagrass and coral can generate.
- Most former land biome types now become deep ocean types. Warm/lukewarm
  regions have sandy floors; regular/cold deep regions have gravel. These are
  vanilla ocean materials, with temperatures kept above freezing.
- A final generation pass clears everything above sea level, including floating
  ruined portals and sugar cane. It runs during generation, never over player builds.
- Underground terrain, ores and caves beneath the new floor remain largely
  intact. Newly exposed cave openings can flood, and decorations can change.
- The new creatures use vanilla item drops. Four craftable building blocks are
  added; no new generated settlements or structures are included. Nether/End
  terrain is unchanged. Vanilla structure preservation is not guaranteed.

## Tested

The v0.4.0 terrain checks below still apply: all **294 generation/biome files**
are byte-for-byte unchanged in v0.5.2. Creature, gear and building-block checks are documented in
[the sea-life test notes](experiments/sea_life/README.md).

Bedrock Dedicated Server **1.26.52.3**: two reproduced floating-portal sites
contained **64 and 187 above-water blocks** in v0.3.0 and **zero** in v0.4.0.
Both updated samples retained underground caves, kelp and seagrass, with no ice
or underwater grass/logs.

An additional **2,048-column survey across eight areas** found depths from
**18 to 55 blocks**, no above-water blocks or ice, and both sand and gravel floors.
Deliberate above-water test blocks were cleared, while underground markers
remained. The warm reef sample still generated coral and sea pickles.

These are sampled engine checks, not a guarantee for every seed. In-game visual
quality for this update and phone performance still need a player check. See the
[v0.4.0 test notes and measurements](experiments/depths/README.md) and the
[historical v0.3.0 tests](experiments/seabed/README.md).

## Build

```sh
python3 tools/build.py
python3 tools/validate.py
```

The phone-importable package is `dist/Endless_Waters.mcaddon`.
