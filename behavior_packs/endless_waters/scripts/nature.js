import { hash } from './layout.js';

const TREES = {
  oak: ['oak_log', 'oak_leaves'], tropical: ['jungle_log', 'jungle_leaves'],
  taiga: ['spruce_log', 'spruce_leaves'], cherry: ['cherry_log', 'cherry_leaves'],
  autumn: ['poplar_log', 'orange_poplar_leaves']
};

export function decorate(p, site, seed, ground) {
  for (let i = 0; i < 130; i++) {
    const x = Math.floor(hash(i, site.cx, seed ^ 3001) * 110) - 55;
    const z = Math.floor(hash(i, site.cz, seed ^ 3002) * 110) - 55;
    // Keep the settlement, trial entrance, and dock approach clear.
    if (site.kind !== 'wild' && Math.abs(x) < 30 && Math.abs(z) < 31) continue;
    if (Math.abs(x) < 7 && z > 15) continue;
    if (site.trial && Math.abs(x - 30) < 9 && Math.abs(z + 23) < 9) continue;
    const surface = ground(x, z);
    if (surface < 66 || surface > 85) continue;
    const y = surface - p.y;
    const theme = x < 0 ? site.primary : site.secondary;
    if (theme === 'desert') {
      p.box(x - 2, y - 1, z - 2, x + 2, y, z + 2, 'sand');
      if (i % 4 === 0) p.box(x, y + 1, z, x, y + 3, z, 'cactus');
      continue;
    }
    if (i % 3 !== 0) {
      p.block(x, y + 1, z, theme === 'autumn' ? 'red_shrub' : theme === 'cherry' ? 'pink_petals' : 'short_grass');
      continue;
    }
    const [log, leaves] = TREES[theme];
    const height = theme === 'tropical' ? 8 : theme === 'taiga' ? 9 : 5 + Math.floor(hash(i, seed) * 3);
    p.box(x, y + 1, z, x, y + height, z, log);
    if (theme === 'taiga') {
      for (let h = 3; h <= height + 1; h++) {
        const radius = Math.max(0, Math.floor((height + 1 - h) / 3));
        p.box(x - radius, y + h, z - radius, x + radius, y + h, z + radius, leaves, { persistent_bit: false });
      }
      p.box(x, y + 1, z, x, y + height, z, log);
    } else {
      const leaf = theme === 'autumn' ? ['orange_poplar_leaves', 'red_poplar_leaves', 'yellow_poplar_leaves'][i % 3] : leaves;
      p.box(x - 2, y + height - 2, z - 2, x + 2, y + height, z + 2, leaf, { persistent_bit: false });
      p.box(x - 1, y + height + 1, z - 1, x + 1, y + height + 1, z + 1, leaf, { persistent_bit: false });
      p.box(x, y + 1, z, x, y + height, z, log);
    }
  }
  for (const [dx, dz, mob] of [[-32, 0, 'sheep'], [-30, 3, 'sheep'], [30, 2, 'cow'], [33, 2, 'cow'], [0, -33, 'chicken'], [3, -32, 'chicken']]) {
    const y = ground(dx, dz);
    if (y > 65 && y < 86) p.mob(dx, y - p.y + 1, dz, mob);
  }
  // Sugar cane beside the water is a renewable route to paper and maps.
  for (let z = 40; z <= 65; z++) {
    const h = ground(-10, z);
    if (h === 62 || h === 63) {
      p.block(-10, h - p.y, z, 'sand');
      p.block(-11, h - p.y, z, 'water');
      p.box(-10, h - p.y + 1, z, -10, h - p.y + 2, z, 'reeds');
      break;
    }
  }
}
