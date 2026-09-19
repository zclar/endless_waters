import { BlockPermutation, BlockVolume, system, world } from '@minecraft/server';
import { CELL, hash, regionKey, seedNumber, siteAt } from './layout.js';
import { Plan, harbor, outpost, estate, ship, trialEntrance } from './buildings.js';
import { decorate } from './nature.js';

let seed = 0;
let dimension;
let busy = false;
let activeKey;
const done = new Set();
const waitingPlayers = new Set();
const permutations = new Map();
const failureCooldown = new Map();

function permutation(block, states = {}) {
  const key = block + JSON.stringify(states);
  if (!permutations.has(key)) permutations.set(key, BlockPermutation.resolve('minecraft:' + block, states));
  return permutations.get(key);
}

function getState(key) {
  const value = world.getDynamicProperty(key);
  return typeof value === 'string' ? JSON.parse(value) : undefined;
}

function complete(key) {
  if (done.has(key)) return true;
  if (getState(key)?.done) {
    if (done.size > 512) done.clear();
    done.add(key);
    return true;
  }
  return false;
}

export function surfaceAt(x, z) {
  // Read terrain only, not trees/roofs. Used once and saved before building.
  for (let y = 85; y >= 28; y--) {
    const b = dimension.getBlock({ x, y, z });
    if (!b) throw new Error('Terrain is not loaded');
    if (['minecraft:grass_block', 'minecraft:sand', 'minecraft:stone', 'minecraft:dirt', 'minecraft:sandstone'].includes(b.typeId)) return y;
  }
  return 27;
}

function camp(p, site) {
  const name = site.primary === 'cherry' ? 'cherry_grove' : site.primary === 'autumn' ? 'dappled_forest' :
    site.primary === 'tropical' ? 'bamboo_jungle' : 'birch_forest';
  p.command(`place structure minecraft:abandoned_camp_${name} ${p.x} ${p.y + 1} ${p.z} true false true`);
}

function makePlan(site, state) {
  const p = new Plan(site.x, state.y, site.z);
  const ground = (x, z) => state.ground[`${x},${z}`] ?? 27;
  decorate(p, site, seed, ground);
  if (site.kind === 'harbor' || site.kind === 'pirate') harbor(p, site.kind === 'pirate');
  else if (site.kind === 'outpost') outpost(p);
  else if (site.kind === 'estate') estate(p);
  else if (site.kind === 'camp') camp(p, site);
  if (site.ship) {
    const boat = new Plan(site.x + 38, 59, site.z + 80);
    ship(boat, site.kind !== 'harbor');
    p.ops.push(...boat.ops);
  }
  if (site.trial) {
    const tx = site.x + 30, tz = site.z - 23;
    p.command(`place structure minecraft:trial_chambers ${tx} -26 ${tz} true false true`);
    const entry = new Plan(tx, ground(30, -23), tz);
    trialEntrance(entry);
    p.ops.push(...entry.ops);
  }
  if (site.starter) {
    p.chest(-6, 1, 23, 'chests/shipwrecksupply');
    // An actual rowing boat, separate from the stationary sailing ship.
    p.mob(5, 64 - p.y, 70, 'boat');
  }
  return p.ops;
}

function sampleGround(site) {
  const ground = {};
  // Only sample positions actually used by the deterministic decoration plan.
  for (let i = 0; i < 130; i++) {
    const x = Math.floor(hash(i, site.cx, seed ^ 3001) * 110) - 55;
    const z = Math.floor(hash(i, site.cz, seed ^ 3002) * 110) - 55;
    ground[`${x},${z}`] = surfaceAt(site.x + x, site.z + z);
  }
  for (const [x, z] of [[-32, 0], [-30, 3], [30, 2], [33, 2], [0, -33], [3, -32], [30, -23]])
    ground[`${x},${z}`] = surfaceAt(site.x + x, site.z + z);
  for (let z = 40; z <= 65; z++) ground[`-10,${z}`] = surfaceAt(site.x - 10, site.z + z);
  return ground;
}

export function applyOperation(op) {
  if (op.type === 'fill') {
    dimension.fillBlocks(new BlockVolume(op.from, op.to), permutation(op.block, op.states));
  } else if (op.type === 'mob') {
    const entity = dimension.spawnEntity('minecraft:' + op.mob, op.at);
    if (op.name) entity.nameTag = op.name;
  } else if (op.type === 'loot') {
    const { x, y, z } = op.at;
    const result = dimension.runCommand(`loot insert ${x} ${y} ${z} loot "${op.table}"`);
    if (!result.successCount) throw new Error('Loot insertion failed: ' + op.table);
  } else if (op.type === 'command') {
    const result = dimension.runCommand(op.command);
    if (!result.successCount) throw new Error('Placement failed: ' + op.command);
  }
}

function release() {
  try { world.tickingAreaManager.removeTickingArea('endless:building'); } catch { /* already removed */ }
  busy = false;
  activeKey = undefined;
}

export async function generateSite(cx, cz) {
  const key = regionKey(cx, cz);
  if (busy || complete(key)) return false;
  busy = true;
  activeKey = key;
  const site = siteAt(cx, cz, seed);
  try {
    // Hold the whole build plus a margin. Terrain generation finishes before
    // any scenery is placed, including neighboring chunks at the shore.
    await world.tickingAreaManager.createTickingArea('endless:building', {
      dimension,
      from: { x: site.x - (site.trial ? 112 : 64), y: 0, z: site.z - (site.trial ? 112 : 64) },
      to: { x: site.x + (site.trial ? 144 : 64), y: 0, z: site.z + 112 }
    });
    let state = getState(key);
    if (!state) {
      const y = surfaceAt(site.x, site.z);
      if (y < 66) {
        world.setDynamicProperty(key, JSON.stringify({ done: true, empty: true }));
        release(); return true;
      }
      state = { y, cursor: 0, ground: sampleGround(site) };
      world.setDynamicProperty(key, JSON.stringify(state));
    }
    const ops = makePlan(site, state);
    // Validate all block permutations before making any changes.
    for (const op of ops) if (op.type === 'fill') permutation(op.block, op.states);
    system.runJob((function* () {
      try {
        while (state.cursor < ops.length) {
          const op = ops[state.cursor];
          // Save non-repeatable operations first: a crash may skip a reward,
          // but cannot duplicate villagers, enemies, or refill looted chests.
          if (op.type !== 'fill') {
            state.cursor++;
            world.setDynamicProperty(key, JSON.stringify(state));
          }
          applyOperation(op);
          if (op.type === 'fill') {
            state.cursor++;
            world.setDynamicProperty(key, JSON.stringify(state));
          }
          yield;
        }
        world.setDynamicProperty(key, JSON.stringify({ done: true, kind: site.kind, y: state.y }));
        done.add(key);
        if (site.starter) {
          world.setDefaultSpawnLocation({ x: 112, y: state.y + 1, z: 137 });
          world.setDynamicProperty('endless:spawn_y', state.y + 1);
        }
        console.warn(`[Endless Waters] Finished ${site.kind} at ${site.x}, ${site.z}.`);
      } catch (error) {
        failureCooldown.set(key, system.currentTick + 1200);
        console.error(`[Endless Waters] Paused ${key} at operation ${state.cursor}: ${error}`);
      } finally { release(); }
    })());
    return true;
  } catch (error) {
    failureCooldown.set(key, system.currentTick + 1200);
    console.error(`[Endless Waters] Could not prepare ${key}: ${error}`);
    release();
    return false;
  }
}

function welcome(player) {
  if (player.getDynamicProperty('endless:welcomed')) return;
  waitingPlayers.add(player.id);
  player.addEffect('water_breathing', 1200, { showParticles: false });
  player.addEffect('resistance', 1200, { amplifier: 4, showParticles: false });
  player.addEffect('slow_falling', 1200, { showParticles: false });
  player.sendMessage('§bEndless Waters§r — preparing your harbor. Your voyage begins shortly.');
}

function tick() {
  const players = world.getAllPlayers().filter(p => p.dimension.id === 'minecraft:overworld');
  for (const player of players) {
    if (!player.getDynamicProperty('endless:welcomed') && !waitingPlayers.has(player.id)) welcome(player);
    if (waitingPlayers.has(player.id)) {
      const y = world.getDynamicProperty('endless:spawn_y');
      if (typeof y === 'number') {
        player.teleport({ x: 112.5, y, z: 137.5 }, { dimension });
        player.setDynamicProperty('endless:welcomed', true);
        waitingPlayers.delete(player.id);
        player.sendMessage('§bWelcome to Endless Waters!§r Follow the dock to your boat. Pirate sails mean trouble.');
      } else {
        player.addEffect('water_breathing', 1200, { showParticles: false });
        player.addEffect('resistance', 1200, { amplifier: 4, showParticles: false });
        player.addEffect('slow_falling', 1200, { showParticles: false });
      }
    }
  }
  if (!players.length || busy) return;
  if (!complete(regionKey(0, 0))) { void generateSite(0, 0); return; }
  const candidates = [];
  for (const player of players) {
    const cx = Math.floor(player.location.x / CELL), cz = Math.floor(player.location.z / CELL);
    for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) {
      const site = siteAt(cx + dx, cz + dz, seed);
      const distance = Math.hypot(site.x - player.location.x, site.z - player.location.z);
      if (distance < 200) candidates.push({ ...site, distance });
    }
  }
  candidates.sort((a, b) => a.distance - b.distance);
  for (const site of candidates) {
    const key = regionKey(site.cx, site.cz);
    if (!complete(key) && (failureCooldown.get(key) ?? 0) <= system.currentTick) {
      void generateSite(site.cx, site.cz); break;
    }
  }
}

export function initialize() {
  dimension = world.getDimension('overworld');
  seed = seedNumber(world.seed);
  world.afterEvents.playerSpawn.subscribe(({ player, initialSpawn }) => { if (initialSpawn) welcome(player); });
  system.runInterval(tick, 20);
  // Administrator diagnostics; no player chat interception or custom items.
  system.afterEvents.scriptEventReceive.subscribe(event => {
    if (event.id === 'endless:status') {
      const message = `Endless Waters 0.1.0 | ${activeKey ?? 'ready'} | spawn: ${world.getDynamicProperty('endless:spawn_y') ?? 'preparing'}`;
      console.warn(message);
      event.sourceEntity?.sendMessage?.(message);
    }
  });
  console.warn('[Endless Waters] Ocean terrain and island discoveries enabled.');
}
