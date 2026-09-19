import test from 'node:test';
import assert from 'node:assert/strict';
import { CELL, THEMES, siteAt, hash, seedNumber, terrainHeight, regionKey } from '../behavior_packs/endless_waters/scripts/layout.js';
import { Plan, harbor, outpost, estate, ship, trialEntrance } from '../behavior_packs/endless_waters/scripts/buildings.js';

test('layout is deterministic across reloads, negative coordinates, and distant exploration', () => {
  for (const [x, z] of [[0, 0], [-1, -1], [-71, 109], [8000, -4000]]) {
    assert.deepEqual(siteAt(x, z, 7), siteAt(x, z, 7));
    assert.equal(Math.floor(siteAt(x, z, 7).x / CELL), x);
    assert.ok(hash(x, z, 7) >= 0 && hash(x, z, 7) < 1);
  }
  assert.notEqual(regionKey(-1, 0), regionKey(0, -1));
  assert.notEqual(seedNumber('123'), seedNumber('124'));
  assert.equal(siteAt(0, 0, 991).kind, 'harbor');
});

test('each island uses one or two distinct themes; all settlement types occur', () => {
  const kinds = new Set();
  let twoThemes = 0, ships = 0, trials = 0;
  for (let x = -30; x <= 30; x++) for (let z = -30; z <= 30; z++) {
    const s = siteAt(x, z, 118);
    assert.ok(THEMES.includes(s.primary) && THEMES.includes(s.secondary));
    if (s.primary !== s.secondary) twoThemes++;
    kinds.add(s.kind); ships += Number(s.ship); trials += Number(s.trial);
  }
  assert.deepEqual([...kinds].sort(), ['camp', 'estate', 'harbor', 'outpost', 'pirate', 'wild']);
  assert.ok(twoThemes > 1200 && twoThemes < 1900);
  assert.ok(ships > 1200 && ships < 1900);
  assert.ok(trials > 550 && trials < 950);
});

test('terrain guarantees water corridors and cannot connect islands into continents', () => {
  // Use extreme noise values to test the maximum possible land extent.
  for (const noise of [() => -1, () => 0, () => 1]) {
    for (let x = -1000; x <= 1000; x += CELL) {
      for (let z = -2 * CELL; z <= 2 * CELL; z++) {
        const boundary = Math.floor(x / CELL) * CELL;
        assert.ok(terrainHeight(boundary, z, noise) < 63);
      }
    }
    assert.ok(terrainHeight(112, 112, noise) >= 74);
  }
});

test('neutral-noise terrain is predominantly water with useful small islands', () => {
  let land = 0;
  for (let x = 0; x < CELL; x++) for (let z = 0; z < CELL; z++)
    land += Number(terrainHeight(x, z, () => 0) >= 63);
  const fraction = land / CELL ** 2;
  assert.ok(fraction > .1 && fraction < .2, `land proportion ${fraction}`);
});

test('all builds fit Bedrock fill limits and use only vanilla blocks and loot', () => {
  for (const build of [harbor, outpost, estate, ship, trialEntrance]) {
    const p = new Plan(-112, build === ship ? 59 : 78, -336);
    build(p);
    for (const op of p.ops) {
      if (op.type === 'fill') {
        const { from: a, to: b } = op;
        assert.ok(a.x <= b.x && a.y <= b.y && a.z <= b.z);
        assert.ok((b.x - a.x + 1) * (b.y - a.y + 1) * (b.z - a.z + 1) <= 32768);
        assert.ok(a.y >= -64 && b.y < 320);
        assert.ok(!op.block.includes(':'));
      }
      if (op.type === 'loot') assert.ok(op.table.startsWith('chests/'));
    }
  }
});
