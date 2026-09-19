// Original modular builds, made exclusively from vanilla blocks.
// Plans are deterministic and serializable, so an interrupted build can resume.
export class Plan {
  constructor(x, y, z) { this.x = x; this.y = y; this.z = z; this.ops = []; }
  at(x, y, z) { return { x: this.x + x, y: this.y + y, z: this.z + z }; }
  box(x1, y1, z1, x2, y2, z2, block, states) {
    const layerSize = (x2 - x1 + 1) * (z2 - z1 + 1);
    const layers = Math.max(1, Math.floor(32768 / layerSize));
    for (let y = y1; y <= y2; y += layers)
      this.ops.push({ type: 'fill', from: this.at(x1, y, z1), to: this.at(x2, Math.min(y2, y + layers - 1), z2), block, states });
  }
  block(x, y, z, block, states) { this.box(x, y, z, x, y, z, block, states); }
  mob(x, y, z, mob, name) { this.ops.push({ type: 'mob', at: this.at(x + .5, y, z + .5), mob, name }); }
  loot(x, y, z, table) { this.ops.push({ type: 'loot', at: this.at(x, y, z), table }); }
  command(command) { this.ops.push({ type: 'command', command }); }
  bed(x, y, z, straw = false) {
    if (straw) {
      this.block(x, y, z, 'straw_bed', { 'minecraft:cardinal_direction': 'south', head_piece_bit: false });
      this.block(x, y, z + 1, 'straw_bed', { 'minecraft:cardinal_direction': 'south', head_piece_bit: true });
    } else {
      this.block(x, y, z, 'bed', { direction: 0, head_piece_bit: false, occupied_bit: false });
      this.block(x, y, z + 1, 'bed', { direction: 0, head_piece_bit: true, occupied_bit: false });
    }
  }
  door(x, y, z, wood = 'spruce') {
    const block = wood === 'oak' ? 'wooden_door' : `${wood}_door`;
    this.block(x, y, z, block, { 'minecraft:cardinal_direction': 'south', upper_block_bit: false });
    this.block(x, y + 1, z, block, { 'minecraft:cardinal_direction': 'south', upper_block_bit: true });
  }
  chest(x, y, z, table) {
    this.block(x, y, z, 'chest', { 'minecraft:cardinal_direction': 'south' });
    this.loot(x, y, z, table);
  }
}

function house(p, x, z, wood = 'spruce', job = 'barrel') {
  p.box(x, -8, z, x + 8, -1, z + 8, 'cobblestone');
  p.box(x, 0, z, x + 8, 0, z + 8, `${wood}_planks`);
  p.box(x, 1, z, x + 8, 4, z + 8, `${wood}_planks`);
  p.box(x + 1, 1, z + 1, x + 7, 4, z + 7, 'air');
  for (const dx of [0, 8]) for (const dz of [0, 8])
    p.box(x + dx, 0, z + dz, x + dx, 5, z + dz, `${wood}_log`);
  for (let i = 0; i < 5; i++)
    p.box(x - 1 + i, 5 + i, z - 1, x + 9 - i, 5 + i, z + 9, 'dark_oak_planks');
  p.box(x + 4, 1, z, x + 4, 2, z, 'air');
  p.door(x + 4, 1, z, wood);
  p.block(x, 2, z + 4, 'glass_pane');
  p.block(x + 8, 2, z + 4, 'glass_pane');
  p.block(x + 4, 2, z + 8, 'glass_pane');
  p.block(x + 6, 1, z + 6, job);
  p.block(x + 6, 2, z + 6, 'lantern');
  p.bed(x + 2, 1, z + 5);
  p.chest(x + 6, 1, z + 2, job === 'smithing_table'
    ? 'chests/village/village_toolsmith' : 'chests/village/village_plains_house');
}

function pier(p, x, z, length = 27) {
  const seaY = 64 - p.y;
  p.box(x - 2, seaY, z, x + 2, seaY, z + length, 'spruce_planks');
  for (let i = 0; i <= length; i += 6) {
    for (const dx of [-3, 3]) {
      p.box(x + dx, seaY - 6, z + i, x + dx, seaY + 1, z + i, 'stripped_spruce_log');
      p.block(x + dx, seaY + 2, z + i, 'lantern');
    }
  }
  // A walkable staircase down to the sea, rather than a floating dock.
  for (let i = 1; i <= Math.max(0, p.y - 64); i++)
    p.box(x - 2, seaY + i, z - i, x + 2, seaY + i, z - i, 'spruce_planks');
  p.block(x + 1, seaY + 1, z + length - 2, 'barrel');
  p.loot(x + 1, seaY + 1, z + length - 2, 'chests/shipwrecksupply');
  p.mob(x, seaY + 1, z + length + 3, 'boat');
}

export function harbor(p, pirate = false) {
  const wood = pirate ? 'dark_oak' : 'spruce';
  p.box(-22, -7, -21, 22, -1, 23, 'stone');
  p.box(-22, 0, -21, 22, 0, 23, 'grass_block');
  p.box(-24, 1, -23, 24, 14, 25, 'air');
  p.box(-2, 0, -21, 2, 0, 27, 'gravel');
  p.box(-22, 0, -2, 22, 0, 2, 'gravel');
  for (const [x, z, job] of [[-19, -18, 'smithing_table'], [10, -18, 'cartography_table'], [-19, 7, 'barrel'], [10, 7, 'composter']]) {
    house(p, x, z, wood, job);
    if (!pirate) p.mob(x + 4, 1, z + 4, 'villager_v2');
  }
  // Market awning and a working village bell.
  for (const x of [-5, 5]) for (const z of [-7, 7]) p.box(x, 1, z, x, 4, z, 'oak_fence');
  for (let x = -5; x <= 5; x++) p.box(x, 5, -7, x, 5, 7, x % 2 ? 'red_wool' : 'white_wool');
  p.block(0, 1, 0, 'bell');
  p.block(-4, 1, -6, 'barrel');
  p.loot(-4, 1, -6, 'chests/shipwrecksupply');
  p.block(4, 1, 6, 'crafting_table');
  p.block(4, 2, 6, 'lantern');
  // Small crop garden; all resources remain ordinary Minecraft resources.
  p.box(11, 0, 20, 19, 0, 25, 'farmland', { moisturized_amount: 7 });
  p.box(15, 0, 20, 15, 0, 25, 'water');
  p.box(11, 1, 20, 14, 1, 25, 'wheat', { growth: 7 });
  p.box(16, 1, 20, 19, 1, 25, 'carrots', { growth: 7 });
  pier(p, 0, 43, 22);
  if (pirate) {
    for (const [x, z] of [[-7, 10], [7, -10], [-4, -17]]) p.mob(x, 1, z, 'pillager', 'Corsair');
    p.chest(-4, 1, 17, 'chests/pillager_outpost');
    flag(p, 0, 7, 0);
  } else {
    p.mob(6, 1, 3, 'iron_golem');
    p.mob(-7, 1, 20, 'cat');
  }
}

function flag(p, x, y, z) {
  p.box(x, y, z, x, y + 7, z, 'dark_oak_fence');
  p.box(x + 1, y + 4, z, x + 5, y + 7, z, 'black_wool');
  p.box(x + 2, y + 5, z, x + 3, y + 6, z, 'white_wool');
  p.block(x + 2, y + 4, z, 'white_wool');
}

export function outpost(p) {
  p.box(-9, -10, -9, 9, 0, 9, 'cobblestone');
  p.box(-8, 1, -8, 8, 21, 8, 'air');
  for (const x of [-5, 5]) for (const z of [-5, 5]) p.box(x, 1, z, x, 18, z, 'dark_oak_log');
  for (const y of [1, 7, 13, 18]) {
    p.box(-6, y, -6, 6, y, 6, 'dark_oak_planks');
    p.box(-6, y + 1, -6, 6, y + 1, -6, 'dark_oak_fence');
    p.box(-6, y + 1, 6, 6, y + 1, 6, 'dark_oak_fence');
    p.box(-6, y + 1, -6, -6, y + 1, 6, 'dark_oak_fence');
    p.box(6, y + 1, -6, 6, y + 1, 6, 'dark_oak_fence');
  }
  p.box(0, 1, -4, 0, 18, -4, 'cobblestone');
  p.box(0, 2, -3, 0, 18, -3, 'ladder', { facing_direction: 3 });
  p.box(0, 7, -3, 0, 7, -3, 'ladder', { facing_direction: 3 });
  p.box(-7, 21, -7, 7, 21, 7, 'dark_oak_planks');
  p.box(-5, 22, -5, 5, 22, 5, 'dark_oak_planks');
  p.chest(3, 19, 3, 'chests/pillager_outpost');
  p.block(-3, 19, -3, 'lantern');
  flag(p, 0, 23, 0);
  for (const [x, y, z] of [[3, 2, 3], [-3, 14, 3], [3, 19, -3]]) p.mob(x, y, z, 'pillager', 'Lookout');
  p.box(-15, 0, 8, -11, 0, 12, 'oak_planks');
  p.box(-15, 1, 8, -11, 3, 12, 'iron_bars');
  p.box(-14, 1, 9, -12, 3, 11, 'air');
  p.mob(-13, 1, 10, 'allay');
}

export function estate(p) {
  // A compact original illager estate, sized to fit a small island.
  p.box(-20, -9, -17, 20, 0, 17, 'cobblestone');
  p.box(-19, 1, -16, 19, 13, 16, 'dark_oak_planks');
  p.box(-18, 1, -15, 18, 12, 15, 'air');
  p.box(-18, 6, -15, 18, 6, 15, 'dark_oak_planks');
  for (const x of [-19, 0, 19]) for (const z of [-16, 16]) p.box(x, 0, z, x, 13, z, 'dark_oak_log');
  for (const x of [-13, -6, 6, 13]) for (const z of [-16, 16]) {
    p.box(x, 2, z, x + 2, 4, z, 'glass_pane');
    p.box(x, 8, z, x + 2, 10, z, 'glass_pane');
  }
  for (let i = 0; i < 6; i++) p.box(-21 + i, 14 + i, -18, 21 - i, 14 + i, 18, 'dark_oak_planks');
  p.box(-1, 1, -16, 1, 3, -16, 'air');
  p.box(-1, 1, -15, 1, 1, 14, 'red_carpet');
  p.box(-17, 1, 12, -7, 4, 14, 'bookshelf');
  p.box(7, 7, 12, 17, 10, 14, 'bookshelf');
  for (let i = 0; i < 6; i++) p.box(12, i + 1, -12 + i, 15, i + 1, -12 + i, 'dark_oak_planks');
  p.box(12, 6, -12, 15, 6, -7, 'air');
  p.box(12, 6, -7, 15, 6, -7, 'dark_oak_planks');
  for (const x of [-13, 13]) for (const z of [-10, 10]) p.block(x, 5, z, 'lantern', { hanging: true });
  p.chest(-16, 1, -12, 'chests/woodland_mansion');
  p.chest(16, 7, 10, 'chests/woodland_mansion');
  p.mob(-5, 1, 4, 'vindicator'); p.mob(7, 1, -6, 'vindicator');
  p.mob(0, 7, 8, 'evocation_illager');
  p.bed(-14, 7, -11); p.bed(-10, 7, -11);
}

export function ship(p, pirate = true) {
  // Keel at local y=0 (world 59); deck at 64. Stationary, boardable structure.
  for (let z = -18; z <= 18; z++) {
    const width = Math.max(1, Math.min(6, Math.floor((19 - Math.abs(z)) / 2) + 1));
    p.box(-Math.max(1, width - 2), 0, z, Math.max(1, width - 2), 0, z, 'dark_oak_planks');
    p.box(-width, 1, z, width, 4, z, 'spruce_planks');
    if (width > 2) p.box(-width + 1, 2, z, width - 1, 4, z, 'air');
    p.box(-width, 5, z, width, 5, z, 'spruce_planks');
    p.block(-width, 6, z, 'dark_oak_fence'); p.block(width, 6, z, 'dark_oak_fence');
  }
  p.box(-4, 6, 9, 4, 10, 15, 'dark_oak_planks');
  p.box(-3, 6, 10, 3, 9, 14, 'air');
  p.door(0, 6, 9, 'dark_oak');
  p.box(-2, 8, 15, 2, 8, 15, 'glass_pane');
  p.chest(2, 6, 13, 'chests/shipwrecktreasure');
  p.block(-2, 6, 13, 'cartography_table');
  p.block(-2, 7, 13, 'lantern');
  p.bed(-2, 6, 10);
  for (const z of [-8, 4]) {
    p.box(0, 5, z, 0, 23, z, 'spruce_log');
    p.box(-7, 21, z, 7, 21, z, 'spruce_log', { pillar_axis: 'x' });
    for (let y = 12; y <= 20; y++) {
      const w = y < 14 || y > 18 ? 5 : 6;
      p.box(-w, y, z - 1, w, y, z - 1, pirate && z === 4 ? 'black_wool' : 'white_wool');
    }
  }
  p.box(-1, 15, 3, 1, 17, 3, 'white_wool');
  p.block(0, 14, 3, 'white_wool');
  p.box(-2, 5, -2, -1, 5, 0, 'air');
  p.box(-2, 2, 0, -2, 5, 0, 'ladder', { facing_direction: 2 });
  p.chest(2, 2, -7, 'chests/shipwrecksupply');
  p.chest(-2, 2, 5, 'chests/shipwreck');
  // Boarding ladder at the port rail, reachable from an ordinary rowing boat.
  p.box(-6, 1, 0, -6, 5, 0, 'spruce_planks');
  p.box(-7, 2, 0, -7, 6, 0, 'ladder', { facing_direction: 4 });
  p.mob(-9, 4, 2, 'boat');
  if (pirate) { p.mob(3, 6, -7, 'pillager', 'Deckhand'); p.mob(-3, 6, 7, 'pillager', 'Quartermaster'); }
}

export function trialEntrance(p) {
  p.box(-4, -3, -4, 4, 0, 4, 'tuff_bricks');
  p.box(-3, 1, -3, 3, 4, 3, 'chiseled_tuff_bricks');
  p.box(-2, 1, -2, 2, 3, 2, 'air');
  p.box(-1, 1, -3, 1, 2, -3, 'air');
  p.block(0, 3, 0, 'lantern', { hanging: true });
  // Shaft ends beside the chamber's placement origin, with a lit landing.
  const bottom = -26 - p.y;
  p.box(0, bottom, 0, 0, 0, 0, 'air');
  p.box(1, bottom, 0, 1, -1, 0, 'tuff_bricks');
  p.box(0, bottom, 0, 0, 0, 0, 'ladder', { facing_direction: 4 });
  p.box(-3, bottom - 1, -3, 3, bottom - 1, 3, 'tuff_bricks');
  p.box(-3, bottom, -3, 0, bottom + 3, 3, 'air');
  p.block(-2, bottom, -2, 'lantern');
}
