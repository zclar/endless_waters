// Installed only in the disposable test server by tools/engine_smoke.py.
import { world, system, BlockPermutation, BlockVolume } from '@minecraft/server';
import { generateSite, applyOperation } from './runtime.js';
import { Plan, harbor, outpost, estate, ship, trialEntrance } from './buildings.js';

const sleep = ticks => new Promise(resolve => system.runTimeout(resolve, ticks));
function check(condition, message) {
  if (!condition) throw new Error(message);
  console.warn('EW_CHECK ' + message);
}

world.afterEvents.worldLoad.subscribe(() => system.run(async () => {
  try {
    console.warn('EW_SMOKE_BEGIN');
    const d = world.getDimension('overworld');
    console.warn('EW_CHECK ticking chunk capacity ' + world.tickingAreaManager.maxChunkCount);
    // Keep a one-chunk anchor alive throughout a headless run: otherwise BDS
    // can pause after the builder releases its last ticking area (no clients).
    await world.tickingAreaManager.createTickingArea('endless:anchor', {
      dimension: d, from: { x: 112, y: 0, z: 112 }, to: { x: 127, y: 0, z: 127 }
    });
    for (const build of [harbor, outpost, estate, ship, trialEntrance]) {
      const p = new Plan(112, 78, 112); build(p);
      for (const op of p.ops) if (op.type === 'fill') BlockPermutation.resolve('minecraft:' + op.block, op.states ?? {});
      check(true, 'valid permutations: ' + build.name);
    }
    await generateSite(0, 0);
    let state;
    for (let i = 0; i < 600; i++) {
      await sleep(20);
      state = JSON.parse(world.getDynamicProperty('endless:site_0_0') ?? '{}');
      if (state.done) break;
    }
    check(state?.done, 'harbor generation completed');
    await world.tickingAreaManager.createTickingArea('endless:inspect', {
      dimension: d, from: { x: 48, y: 0, z: 48 }, to: { x: 176, y: 0, z: 224 }
    });
    const ocean = d.getBlock({ x: 50, y: 62, z: 50 });
    check(ocean.typeId === 'minecraft:water', 'unfrozen sea at ocean sample');
    check(d.getBiome({ x: 50, y: 62, z: 50 }).id === 'endless:archipelago_ocean', 'ocean biome replacement active');
    check(d.getBlock({ x: 50, y: 100, z: 50 }).isAir, 'no mainland above ocean');
    check(d.getBlock({ x: 112, y: state.y, z: 112 }).typeId === 'minecraft:gravel', 'harbor stands on island');
    check(d.getBlock({ x: 150, y: 64, z: 192 }).typeId === 'minecraft:spruce_planks', 'ship deck at waterline');
    const chest = d.getBlock({ x: 106, y: state.y + 1, z: 135 }).getComponent('inventory')?.container;
    check(chest && chest.emptySlotsCount < chest.size, 'starter chest contains vanilla loot');
    check(d.getEntities({ type: 'minecraft:villager_v2', location: { x: 112, y: state.y, z: 112 }, maxDistance: 50 }).length >= 4, 'four villagers spawned');
    // A permanent player edit must survive a repeat discovery call.
    d.setBlockType({ x: 112, y: state.y, z: 112 }, 'minecraft:diamond_block');
    check(await generateSite(0, 0) === false, 'completed islands are skipped');
    check(d.getBlock({ x: 112, y: state.y, z: 112 }).typeId === 'minecraft:diamond_block', 'player edit survives rediscovery');
    for (const build of [outpost, estate, p => harbor(p, true)]) {
      const p = new Plan(112, state.y, 112); build(p);
      for (const op of p.ops) { applyOperation(op); await sleep(1); }
      check(true, 'all operations completed: ' + (build.name || 'pirate harbor'));
    }
    // Native camp pieces need an unobstructed site, not the pirate village
    // just constructed above. Supply an isolated grass platform for this test.
    d.fillBlocks(new BlockVolume({ x: 49, y: 120, z: 49 }, { x: 175, y: 120, z: 175 }), 'minecraft:grass_block');
    const nativeCamp = d.runCommand('place structure minecraft:abandoned_camp_dappled_forest 112 121 112 true false true');
    console.warn('EW_NATIVE_CAMP ' + JSON.stringify(nativeCamp));
    check(nativeCamp.successCount > 0, 'native Wilderness Bound camp placed');
    const nativeTrial = d.runCommand('place structure minecraft:trial_chambers 112 -26 112 true false true');
    check(nativeTrial.successCount > 0, 'native trial chamber placed');
    const trialVolume = new BlockVolume({ x: 48, y: -60, z: 48 }, { x: 175, y: 20, z: 175 });
    check(d.containsBlock(trialVolume, { includeTypes: ['minecraft:trial_spawner'] }), 'native trial spawners exist');
    check(d.containsBlock(trialVolume, { includeTypes: ['minecraft:vault'] }), 'native trial vaults exist');
    world.tickingAreaManager.removeTickingArea('endless:inspect');
    world.tickingAreaManager.removeTickingArea('endless:anchor');
    console.warn('EW_SMOKE_PASS');
  } catch (error) { console.error('EW_SMOKE_FAIL ' + error + ' ' + error.stack); }
}));
