// Pure layout decisions. No Minecraft imports: these are also used by the tests.
export const CELL = 224;
export const SEA = 62;
export const THEMES = ['tropical', 'oak', 'autumn', 'taiga', 'desert', 'cherry'];

export function hash(x, z, salt = 0) {
  let n = Math.imul(x | 0, 374761393) ^ Math.imul(z | 0, 668265263) ^ salt;
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  return ((n ^ (n >>> 16)) >>> 0) / 4294967296;
}

export function seedNumber(text) {
  let n = 2166136261;
  for (const c of String(text)) n = Math.imul(n ^ c.charCodeAt(0), 16777619);
  return n >>> 0;
}

export function siteAt(cx, cz, seed) {
  const starter = cx === 0 && cz === 0;
  const choice = hash(cx, cz, seed);
  const kind = starter ? 'harbor' : choice < .29 ? 'wild' : choice < .51 ? 'harbor' :
    choice < .69 ? 'pirate' : choice < .81 ? 'outpost' : choice < .91 ? 'camp' : 'estate';
  const primary = starter ? 'oak' : THEMES[Math.floor(hash(cx, cz, seed ^ 31) * THEMES.length)];
  const secondary = !starter && hash(cx, cz, seed ^ 97) < .42
    ? THEMES[(THEMES.indexOf(primary) + 1 + Math.floor(hash(cx, cz, seed ^ 109) * 5)) % 6] : primary;
  return { cx, cz, x: cx * CELL + 112, z: cz * CELL + 112, kind, primary, secondary,
    trial: !starter && hash(cx, cz, seed ^ 713) < .2,
    ship: starter || hash(cx, cz, seed ^ 991) < .42,
    rotation: Math.floor(hash(cx, cz, seed ^ 313) * 4), starter };
}

export function regionKey(cx, cz) { return `endless:site_${cx}_${cz}`; }

export function terrainHeight(x, z, noise) {
  const cx = Math.floor(x / CELL), cz = Math.floor(z / CELL);
  const dx = x - (cx * CELL + 112), dz = z - (cz * CELL + 112);
  const radius = 66 + 10 * noise(cx * 7 + 173, cz * 7 + 91);
  const d = Math.hypot(dx, dz) / radius;
  const present = (cx === 0 && cz === 0) || noise(cx * 13 + 37, cz * 13 + 173) > -.52;
  return Math.floor(Math.max(28, Math.min(85,
    31 + Number(present) * 47 * Math.max(0, 1 - d ** 4) + 3 * noise(x / 24 + 173, z / 24))));
}
