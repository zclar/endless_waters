# Multiplayer investigation and v0.5.2

The reported join/kick has not been reproduced. There is no client error message,
host log, game-version pair or known hosting type. Do not describe this release
as a confirmed fix for the kick.

The prior Bedrock Dedicated Server 1.26.52.3 run with `starter_probe.js` produced
one boat for each of two simulated players, 590 remaining breathing ticks after
ten ticks elapsed, and prevented duplicate grants. Simulated players do not
exercise network login, resource-pack transfer or phone rendering. The temporary
server installation is no longer present in this workspace session.

Current reproducible checks:

```
node --experimental-vm-modules experiments/sea_life/lifecycle_test.mjs
python3 tools/build.py
python3 tools/validate.py
```

The Node test executes the release source with a Script API stub. It verifies
independent two-player grants, 600-tick breathing, respawn/reconnect exclusion,
a restored persistent marker, full-inventory drops, preserving stronger effects,
no block reads for players without a helmet, and one player's unavailable-block
error not preventing another player's equipment update. It is not an engine or
network test.

Gear polling now avoids block lookups for players without helmets and skips
underwater-movement component access without flippers or a stored restoration
value. Each player's update is isolated; errors are logged once until recovery
or departure. These changes address concrete unnecessary work/error propagation,
not an established cause of the reported kick.

The archive is under 200 KB, contains matching pack versions and only two release
scripts. All 294 approved terrain/biome files remain unchanged. Previous engine
measurements included area-generation loads of 8.8 and 17.0 seconds on a desktop;
those are not phone benchmarks or proof of a loading timeout.

For the next real-device check, use a copy of the world with only Endless Waters
active (disable visual packs), matching stable Minecraft versions, and modest
render distance. Compare with joining a plain world hosted by the same person.
If plain works but the addon copy fails, record the exact guest disconnect
message and host Content Log. Preserve the original world and its enabled packs.

Official references:
- https://help.minecraft.net/hc/en-us/articles/4409236107789
- https://help.minecraft.net/hc/en-us/articles/24121220131597
- https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/common-errors
