# Validation

## Automated checks

```sh
python3 tools/build.py
node --test tests/*.test.js
python3 tools/validate.py
```

The tests check deterministic placements, negative and distant coordinates, open-water separation between islands, land coverage, theme/landmark distribution, structure fill sizes, height bounds, manifest dependencies, feature references, vanilla-only content, and exact contents of the downloadable archive.

## Real Bedrock engine smoke test

The official **Bedrock Dedicated Server 1.26.51.1** is used for engine tests. Its binary and game assets are downloaded separately into `/tmp` and are not shipped in this repository.

```sh
python3 tools/engine_smoke.py /tmp/endless-waters-bds
```

This makes a disposable world, binds the server to localhost with an empty allowlist, activates both packs, and injects the test script **only into the temporary test pack**. It checks the native terrain, actual harbor construction, loot contents, villagers, ship placement, protection of a player edit on rediscovery, other settlement builds, Wilderness Bound camp placement, and the presence of native trial spawners and vaults. The server is stopped at the end. Logs are written to ignored `test-results/engine-smoke.log`.

No client is simulated. A server smoke-test pass does not prove that the client import UI, visuals, player movement, village trading, raids, trial combat, or multiplayer reconnection all behave correctly.

## Client playtest checklist

- Import the combined `.mcaddon` and confirm both packs are available.
- Create a fresh Survival world, cheats on, experiments off; wait for harbor preparation and verify safe arrival.
- Board a rowing boat, board the larger sailing ship, and inspect its hold and cabin.
- Sail several thousand blocks in more than one direction; check water coverage, frame rate, island edges, and scenery appearance.
- Sleep, trade, farm, mine, and use the Nether. Check that island resources support survival.
- Find a pirate port, outpost, estate, autumn island, abandoned camp, and trial chamber. Play through a trial rather than only inspecting its blocks.
- Build on an island, empty a chest, save/quit, restart, and revisit. Confirm the build and chest contents persist.
- Test two players approaching separate islands, then disconnect/reconnect during generation.

## Implementation references

- [World generation passes](https://learn.microsoft.com/en-us/minecraft/creator/documents/world-generation?view=minecraft-bedrock-stable)
- [Structure template features](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/featuresreference/examples/features/minecraftstructure_template_feature?view=minecraft-bedrock-stable)
- [Stable biome replacements](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/biomesreference/examples/components/minecraftbiomes_replace_biomes?view=minecraft-bedrock-stable)
- [Bedrock place command](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/commandsreference/examples/commands/place?view=minecraft-bedrock-stable)
- [Wilderness Bound release notes](https://feedback.minecraft.net/hc/en-us/articles/48826825649933-Minecraft-Bedrock-Edition-26-50-Changelog-Wilderness-Bound)
- [Mojang's current vanilla block and loot metadata](https://github.com/Mojang/bedrock-samples)
