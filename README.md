# Endless Waters

A Minecraft **Bedrock 26.50+** ocean exploration add-on, built for a **new, infinite world**. Small islands, pirate ports, coastal villages, boardable sailing ships, illager estates, and vanilla treasure. No custom blocks, items, mobs, or loot tables.

**[Download Endless_Waters.mcaddon](https://github.com/zclar/endless_waters/raw/refs/heads/main/dist/Endless_Waters.mcaddon)** · [Installation and limitations](docs/INSTALL.md) · [Testing](docs/TESTING.md)

## What you can discover

- An ocean stretching through newly generated chunks, with separated small islands and generous water corridors. The nominal layout is about **85% ocean**, with roughly 80–115-block-wide islands in 224-block regions; some regions are empty.
- One or two **landscape themes** on each island: tropical jungle, oak woodland, autumn poplar, taiga, desert, or cherry. These are vegetation/material themes; the surface's actual engine biome is an ocean biome.
- A friendly starting harbor with four villagers, beds, workstations, crops, a market, an iron golem, a dock, supplies, and ordinary usable boats.
- Pirate harbors, furnished sailing ships, pillager watchtowers, and compact woodland-style illager estates. Large ships are **stationary structures** you can board and explore; vanilla rowing boats are the vehicles.
- Real **Wilderness Bound abandoned camps**, including native containers and loot, plus poplar trees and red shrubs in autumn scenery.
- Extra, complete vanilla **trial chambers**, with their actual trial spawners and vaults, and marked ladder entrances on selected islands.
- Normal deep underground generation below Y=24. The Nether and End generators are unchanged.

Settlements and scenery are added once as you approach. Their progress is saved; revisiting a completed island does not rebuild it, respawn its initial residents, or refill its chests. Let a newly discovered settlement finish appearing before building inside it.

## Install

1. Download the `.mcaddon` above and open it with Minecraft. Both packs should import.
2. Create a **new normal/infinite Overworld** in Bedrock **26.50 or newer**. Do not choose Flat.
3. Activate **Endless Waters — Archipelago** under Behavior Packs and **Endless Waters — Ocean Atmosphere** under Resource Packs.
4. Enable cheats for the structure and loot commands. No experimental toggles or Beta APIs are used.
5. Start the world and allow the starting harbor to prepare. You will be moved to its safe spawn when it is ready. Initial generation can take a minute or longer, depending on the device.

Use this pack only on a **new world**. It replaces the surface of new Overworld chunks. It is incompatible with other terrain-generation packs, and removing it mid-world will produce a boundary with ordinary mainland terrain in newly explored areas.

This is a **0.1.0 prototype**, tested with the Bedrock dedicated server. Client visuals, long sailing sessions, mobile performance, Realms, and console installation still need playtesting. See the [honest scope notes](docs/INSTALL.md#scope-notes) before starting a long-term survival world.

## Build from source

Requires Python 3.10+ and Node.js 20+. No third-party build dependencies or npm installation required.

```sh
python3 tools/build.py
node --test tests/*.test.js
python3 tools/validate.py
```

The build creates the combined `.mcaddon` and separate behavior/resource `.mcpack` files in `dist/`. Both separate packs are required if installing that way. Generated `.mcstructure` files contain our own terrain columns, not redistributed Mojang structures. Native camps, chambers, and loot are referenced from the installed game.

License: [Apache 2.0](LICENSE). Not an official Minecraft product; not approved by or associated with Mojang or Microsoft.
