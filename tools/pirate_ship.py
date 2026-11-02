"""Original Dreadwake galleon: build data and review-only Bedrock templates.

No world-generation hooks and no dependency on downloaded structure code.
Coordinates: X across the beam, Z bow to stern, Y up. Water surface is Y=8.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import random
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/structure_previews/dreadwake'
CENTER = 24
SIZE = (49, 76, 116)
WATER = 8
VARIANTS = ('new', 'tattered', 'abandoned')


@dataclass(frozen=True)
class Block:
    name: str
    states: tuple = ()

    def state(self, name, default=None):
        return dict(self.states).get(name, default)


def b(name, **states):
    return Block(name, tuple(sorted(states.items())))


AIR = b('air')
HULL = b('dark_oak_planks')
DECK = b('spruce_planks')
BEAM = b('stripped_spruce_log', pillar_axis='z')
GOLD = b('yellow_terracotta')
FENCE = b('dark_oak_fence')
ROPE = b('oak_fence')


def slab(name='spruce', top=False):
    return Block(name + '_slab', (('minecraft:vertical_half', 'top' if top else 'bottom'),))


def stair(name='spruce', facing=0, upside=False):
    return b(name + '_stairs', weirdo_direction=facing, upside_down_bit=upside)


class Ship:
    def __init__(self, variant):
        self.variant = variant
        self.blocks = {}
        self.zones = {}
        self.crew = []

    def put(self, x, y, z, block):
        pos = (round(x), round(y), round(z))
        assert all(0 <= v < s for v, s in zip(pos, SIZE)), pos
        self.blocks[pos] = block

    def box(self, x0, y0, z0, x1, y1, z1, block):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    self.put(x, y, z, block)

    def line(self, p, q, block):
        steps = max(abs(q[i] - p[i]) for i in range(3)) * 3
        previous = None
        for n in range(int(steps) + 1):
            t = n / max(1, steps)
            point = [round(p[i] + t * (q[i] - p[i])) for i in range(3)]
            if block == ROPE and previous is not None:
                # Face-connected steps keep diagonal ropes from floating apart.
                walk = previous.copy()
                for axis in [0, 2, 1]:
                    while walk[axis] != point[axis]:
                        walk[axis] += 1 if walk[axis] < point[axis] else -1
                        self.put(*walk, block)
            self.put(*point, block)
            previous = point

    def lantern(self, x, y, z, lit=True):
        self.put(x, y + 1, z, b('chain', pillar_axis='y'))
        self.put(x, y, z, b('lantern', hanging=True) if lit else FENCE)

    def barrel(self, x, y, z):
        self.put(x, y, z, b('barrel', facing_direction=1, open_bit=False))

    def rail(self, z0, z1, y, width_fn):
        for z in range(z0, z1 + 1):
            for side in [-1, 1]:
                x = CENTER + side * width_fn(z)
                self.put(x, y, z, FENCE)
                if z % 7 == 0:
                    self.put(x, y, z, b('dark_oak_log', pillar_axis='y'))
                    self.put(x, y + 1, z, slab('dark_oak'))
                    if z % 14 == 0:
                        self.lantern(x, y + 2, z)


PROFILE = [(12, 1), (18, 5), (28, 10), (42, 14), (65, 15),
           (80, 14), (91, 12), (101, 10), (105, 8)]


def beam(z):
    for (z0, w0), (z1, w1) in zip(PROFILE, PROFILE[1:]):
        if z0 <= z <= z1:
            return round(w0 + (w1 - w0) * (z - z0) / (z1 - z0))
    return 0


def hull_width(z, y):
    # Rounded bilge, narrower keel and slight tumblehome at the upper rail.
    factor = [0.12, .25, .40, .53, .65, .76, .85, .91, .96, 1, 1, 1, 1, .98, .96][y]
    return max(0, round(beam(z) * factor))


def hull(s):
    for z in range(12, 106):
        for y in range(15):
            w = hull_width(z, y)
            for x in range(CENTER - w, CENTER + w + 1):
                # End caps, keel, and all changes in width form a sealed hull.
                outside = (y == 0 or z in [12, 105] or abs(x - CENTER) == w or
                           abs(x - CENTER) > hull_width(z, max(0, y - 1)) or
                           abs(x - CENTER) > hull_width(z - 1, y) or
                           abs(x - CENTER) > hull_width(z + 1, y))
                if outside:
                    mat = HULL if y not in [3, 8, 13] else BEAM
                    if y == 11:
                        mat = b('red_terracotta')
                    if y == 12:
                        mat = GOLD
                    s.put(x, y, z, mat)
                elif y in [4, 9, 14]:
                    s.put(x, y, z, b('oak_planks') if x % 5 == 0 else DECK)
                else:
                    s.put(x, y, z, AIR)
    # External ribs and copper-colored fastening strips, all above the bilge.
    for z in range(24, 100, 6):
        for y in range(5, 14):
            w = hull_width(z, y)
            for side in [-1, 1]:
                s.put(CENTER + side * w, y, z, b('dark_oak_log', pillar_axis='y'))
                if y in [6, 12]:
                    s.put(CENTER + side * (w + 1), y, z,
                          b('dark_oak_button', facing_direction=4 if side < 0 else 5, button_pressed_bit=False))
    s.rail(28, 83, 15, lambda z: hull_width(z, 14))
    # Gunports are above the waterline; decorative cannons occupy the lower deck.
    for z in range(34, 82, 8):
        w = hull_width(z, 10)
        for side in [-1, 1]:
            edge = CENTER + side * w
            for zz in [z, z + 1]:
                s.put(edge, 10, zz, AIR)
                s.put(edge, 11, zz, AIR)
                s.put(edge + side, 12, zz, slab('dark_oak'))
            s.box(min(edge - side * 4, edge - side * 2), 10, z,
                  max(edge - side * 4, edge - side * 2), 10, z + 1, HULL)
            s.line((edge - side * 3, 11, z), (edge + side * 2, 11, z), b('polished_blackstone_wall'))
            s.put(edge - side * 4, 11, z, b('polished_blackstone'))
            for zz in [z - 1, z + 2]:
                s.put(edge - side * 3, 10, zz, b('grindstone', attachment='standing', direction=0))


def platforms(s):
    # Raised forecastle and aft accommodation; the main deck stays open amidships.
    for z0, z1, y in [(14, 30, 18), (84, 104, 21)]:
        for z in range(z0, z1 + 1):
            w = max(1, beam(z) - (1 if y == 21 else 0))
            for x in range(CENTER - w, CENTER + w + 1):
                s.put(x, y, z, DECK if x % 5 else b('oak_planks'))
            if y == 18:
                for yy in range(15, 18):
                    for side in [-1, 1]:
                        s.put(CENTER + side * w, yy, z, HULL)
        s.rail(z0, z1, y + 1, lambda z: max(1, beam(z) - (1 if y == 21 else 0)))
    # Paired stairs around each raised deck leave a central route through the ship.
    for side in [-1, 1]:
        for k in range(4):
            z, y = 34 - k, 15 + k
            s.box(CENTER + side * 6 - 1, y, z, CENTER + side * 6 + 1, y, z, stair(facing=3))
        for k in range(7):
            z, y = 77 + k, 15 + k
            s.box(CENTER + side * 9 - 1, y, z, CENTER + side * 9 + 1, y, z, stair(facing=2))
    # Forward bowsprit with a double stay, ornamental figurehead and catheads.
    s.line((CENTER, 19, 24), (CENTER, 24, 0), b('spruce_log', pillar_axis='z'))
    s.line((CENTER, 20, 19), (CENTER, 13, 11), GOLD)
    s.line((CENTER, 17, 16), (CENTER, 22, 9), GOLD)
    for side in [-1, 1]:
        s.line((CENTER, 21, 12), (CENTER + side * 3, 22, 14), GOLD)
        s.line((CENTER + side * 5, 18, 20), (CENTER + side * 10, 18, 17), BEAM)
        s.line((CENTER + side * 9, 18, 17), (CENTER + side * 9, 10, 17), b('chain', pillar_axis='y'))
        s.line((CENTER + side * 9, 11, 17), (CENTER + side * 9, 9, 20), b('polished_blackstone_wall'))
        s.line((CENTER + side * 9, 11, 17), (CENTER + side * 9, 9, 14), b('polished_blackstone_wall'))
    # Functional boarding ladders lead up to gaps in the side rails.
    for side in [-1, 1]:
        edge = CENTER + side * (beam(57) + 1)
        for y in range(7, 15):
            s.put(edge - side, y, 57, b('stripped_spruce_log', pillar_axis='y'))
        for y in range(8, 15):
            s.put(edge, y, 57, b('ladder', facing_direction=4 if side < 0 else 5))
        for xx in [edge - side, CENTER + side * hull_width(57, 14)]:
            s.put(xx, 15, 57, AIR)
            s.put(xx, 16, 57, AIR)


def cabin(s):
    # Five-window transom, side galleries, inset trim and a curved crown.
    s.box(14, 15, 85, 34, 20, 103, AIR)
    for y in range(15, 21):
        for z in range(85, 104):
            w = min(11, beam(z))
            for side in [-1, 1]:
                s.put(CENTER + side * w, y, z, b('red_terracotta') if y in [16, 19] else HULL)
                if z % 4 == 0:
                    s.put(CENTER + side * w, y, z, b('stripped_dark_oak_log', pillar_axis='y'))
                elif y in [17, 18]:
                    s.put(CENTER + side * w, y, z, b('light_blue_stained_glass'))
        s.box(14, y, 85, 34, y, 85, HULL)
        s.box(16, y, 104, 32, y, 104, HULL)
        if y in [16, 17, 18, 19]:
            for x in [18, 21, 24, 27, 30]:
                s.put(x, y, 104, b('light_blue_stained_glass') if y in [17, 18] else GOLD)
    s.box(23, 15, 85, 25, 18, 85, AIR)
    for x in [21, 27]:
        s.lantern(x, 18, 84)
    for z in range(90, 107):
        w = min(11, beam(min(105, z))) + 2
        for side in [-1, 1]:
            for dx in [0, 1]:
                s.put(CENTER + side * (w - dx), 16, z, slab('dark_oak', True))
            s.put(CENTER + side * w, 17, z, FENCE)
            if z % 4 == 0:
                s.put(CENTER + side * w, 15, z, stair('dark_oak', 0 if side < 0 else 1, True))
    s.box(13, 16, 105, 35, 16, 107, slab('dark_oak', True))
    s.box(13, 17, 107, 35, 17, 107, FENCE)
    for x in range(15, 34):
        y = 22 + round(3 * math.sin((x - 15) / 18 * math.pi))
        s.put(x, y, 104, GOLD)
        if x % 3 == 0:
            s.put(x, y - 1, 104, b('red_terracotta'))
    for x in [14, 34]:
        s.box(x, 18, 104, x, 22, 104, FENCE)
        s.lantern(x, 21, 105)
    # Keep cabin lighting and the shell; the owner will furnish the room.
    for x in [18, 30]:
        s.lantern(x, 19, 91)
        s.lantern(x, 19, 99)
    # Raised wheel housing on the quarterdeck; its wheel is decorative blocks.
    s.put(24, 22, 95, FENCE)
    s.put(24, 23, 95, b('stripped_oak_log', pillar_axis='z'))
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        s.put(24 + dx, 23 + dy, 95, ROPE)
    s.put(24, 22, 93, b('composter'))


def deck_structure(s):
    # Longitudinal beams, support posts, deckhead lanterns and clear center aisles.
    for z in range(28, 101, 8):
        for level in [5, 10]:
            w = hull_width(z, level) - 1
            s.box(CENTER - w, level + 3, z, CENTER + w, level + 3, z, BEAM)
            for x in [CENTER - min(7, w), CENTER + min(7, w)]:
                s.box(x, level, z, x, level + 2, z, b('stripped_spruce_log', pillar_axis='y'))
            if 32 <= z <= 96:
                s.lantern(CENTER + 3, level + 2, z)
    # Two stairs link all three main decks. Keep the full headroom open.
    for x0, z0 in [(23, 59), (23, 86)]:
        for floor in [4, 9]:
            for step in range(5):
                y, z = floor + 1 + step, z0 + step
                s.box(x0, y, z, x0 + 2, y + 3, z, AIR)
                s.box(x0, y, z, x0 + 2, y, z, stair(facing=2))
            s.box(x0, floor + 5, z0 + 5, x0 + 2, floor + 7, z0 + 6, AIR)
    # Main deck cargo hatch, grating, capstan and tethered skiff.
    s.box(19, 14, 48, 29, 14, 53, HULL)
    for x in range(20, 29):
        for z in range(49, 53):
            s.put(x, 14, z, b('iron_bars') if x % 2 == 0 else AIR)
    s.box(23, 15, 35, 25, 15, 37, HULL)
    s.put(24, 16, 36, b('stripped_spruce_log', pillar_axis='y'))
    s.line((20, 17, 36), (28, 17, 36), ROPE)
    s.line((24, 17, 33), (24, 17, 39), ROPE)
    for x, z in [(14, 46), (33, 46), (15, 73), (32, 72), (18, 80)]:
        s.barrel(x, 15, z)
        s.barrel(x + 1, 15, z)
        s.barrel(x, 16, z)
    # A six-block dinghy stowed beside the mainmast.
    for z in range(65, 74):
        w = 1 if z in [65, 73] else 2
        for x in range(32 - w, 33 + w):
            s.put(x, 15, z, slab('oak'))
            if abs(x - 32) == w:
                s.put(x, 16, z, stair('oak', 0 if x < 32 else 1))
        if z in [67, 70, 72]:
            s.box(31, 16, z, 33, 16, z, slab('oak'))
    s.zones = {'unfurnished_lower_hold': [5, 8], 'unfurnished_gun_deck': [10, 13],
               'main_deck_empty_cabin': [15, 20], 'quarterdeck': [22, 25]}


def sail(s, mast_z, top, bottom, half_width, color, seed):
    rng = random.Random(seed)
    tears = [(rng.randint(-half_width + 2, half_width - 2), rng.randint(bottom + 1, top - 2),
              rng.randint(2, 4), rng.randint(2, 4)) for _ in range(4 if s.variant == 'tattered' else 9)]
    for y in range(bottom, top + 1):
        t = (y - bottom) / (top - bottom)
        width = round(half_width * (.78 + .22 * t))
        for dx in range(-width, width + 1):
            # Billed-out cloth has depth; the foot curves up toward the corners.
            foot = bottom + round(2 * (abs(dx) / half_width) ** 2)
            if y < foot:
                continue
            if s.variant != 'new':
                if any(((dx - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1 for cx, cy, rx, ry in tears):
                    continue
                if s.variant == 'abandoned' and y < top - 3 - (dx * dx % 5):
                    continue
                if y <= foot + 1 and (dx + seed) % 5 in [0, 1]:
                    continue
            z = mast_z - 1 - round(3 * math.sin(math.pi * t) * (1 - (dx / (half_width + 1)) ** 2))
            name = color
            if abs(dx) >= width - 1 or y in [top, top - 1]:
                name = 'red_wool'
            elif s.variant != 'new' and (dx * 17 + y * 13 + seed) % 31 < 4:
                name = 'brown_wool' if color == 'black_wool' else 'light_gray_wool'
            s.put(CENTER + dx, y, z, b(name))
    s.line((CENTER - half_width - 1, top + 1, mast_z),
           (CENTER + half_width + 1, top + 1, mast_z), b('spruce_log', pillar_axis='x'))
    for side in [-1, 1]:
        s.line((CENTER + side * (half_width + 1), top + 1, mast_z),
               (CENTER + side * round(half_width * .8), bottom, mast_z - 1), ROPE)


SKULL = [
    '  #####  ',
    ' ####### ',
    '##  #  ##',
    '##  #  ##',
    ' ### ### ',
    '  #####  ',
    '  # # #  ',
    ' #     # ',
    '#       #',
]


def rig(s):
    for mz, height, spread in [(37, 62, 16), (66, 73, 20), (91, 63, 13)]:
        actual = (64 if mz == 66 else 44 if mz == 91 else height) if s.variant == 'abandoned' else height
        for y in range(5, actual + 1):
            radius = 1 if y < 39 else 0
            for dx in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    s.put(CENTER + dx, y, mz + dz, b('spruce_log', pillar_axis='y'))
            s.put(CENTER + (2 if y < 39 else 1), y, mz, b('ladder', facing_direction=5))
        # Crow's nest and its walkable floor, handrail, and access opening.
        nest_y = min(height - 19, actual - 2)
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                if abs(dx) + abs(dz) <= 5:
                    s.put(CENTER + dx, nest_y, mz + dz, slab('dark_oak', True))
                    if abs(dx) == 3 or abs(dz) == 3:
                        s.put(CENTER + dx, nest_y + 1, mz + dz, FENCE)
        s.put(CENTER + 2, nest_y, mz, AIR)
        # Shrouds and spaced ratlines, with stays linking the mastheads.
        for side in [-1, 1]:
            foot_x = CENTER + side * min(beam(mz), 13)
            for dz in [-5, 0, 5]:
                s.line((foot_x, 16 if mz < 84 else 22, mz + dz), (CENTER + side * 2, nest_y + 2, mz), ROPE)
            for y in range(20 if mz < 84 else 25, nest_y, 3):
                start_y = 16 if mz < 84 else 22
                t = (y - start_y) / (nest_y + 2 - start_y)
                xx = foot_x + (CENTER + side * 2 - foot_x) * t
                half = round(5 * (1 - t))
                s.line((xx, y, mz - half), (xx, y, mz + half), ROPE)
        if s.variant != 'abandoned' or mz != 91:
            sail(s, mz, height - 23, height - 39, spread, 'black_wool' if mz == 66 else 'white_wool', mz)
            if s.variant != 'abandoned' or mz != 66:
                sail(s, mz, height - 5, height - 17, spread - 5, 'white_wool', mz + 4)
            else:
                s.line((14, 16, 72), (33, 19, 80), b('spruce_log', pillar_axis='x'))
        else:
            s.line((14, 26, 88), (34, 29, 99), b('spruce_log', pillar_axis='x'))
        if mz == 66 and s.variant != 'abandoned':
            # Skull is drawn onto the actual main course, follows its curvature.
            for row, line in enumerate(SKULL):
                y = height - 27 - row
                t = (y - (height - 39)) / 16
                for col, pixel in enumerate(line):
                    if pixel == '#':
                        dx = col - 4
                        z = mz - 1 - round(3 * math.sin(math.pi * t) * (1 - (dx / 21) ** 2))
                        if s.blocks.get((CENTER + dx, y, z), AIR) != AIR:
                            s.put(CENTER + dx, y, z, b('white_wool'))
        # Forked pennants at each masthead.
        if s.variant != 'abandoned':
            for dz in range(1, 9):
                for y in range(height - 3, height + 1):
                    if dz < 6 or y not in [height - 2, height - 1]:
                        s.put(CENTER, y, mz + dz, b('black_wool' if mz == 66 else 'red_wool'))
    s.line((CENTER, 62, 37), (CENTER, 24, 0), ROPE)
    s.line((CENTER, 73 if s.variant != 'abandoned' else 64, 66), (CENTER, 62, 37), ROPE)
    s.line((CENTER, 73 if s.variant != 'abandoned' else 64, 66), (CENTER, 44 if s.variant == 'abandoned' else 63, 91), ROPE)
    s.line((CENTER, 44 if s.variant == 'abandoned' else 63, 91), (CENTER, 22, 106), ROPE)
    # Two triangular headsails set beneath the fore stay.
    if s.variant != 'abandoned':
        for z0, z1, top in [(2, 19, 40), (19, 33, 51)]:
            for z in range(z0, z1 + 1):
                max_y = 25 + round((top - 25) * (z - z0) / (z1 - z0))
                for y in range(25, max_y + 1):
                    if s.variant == 'tattered' and (y + z * 3) % 17 < 3:
                        continue
                    s.put(CENTER - 1, y, z, b('white_wool'))


def age(s):
    if s.variant == 'new':
        return
    rng = random.Random(983 if s.variant == 'tattered' else 1163)
    # Weather follows use: patched railings and damaged bulwarks, not random hull holes.
    for pos, block in list(s.blocks.items()):
        x, y, z = pos
        if block.name == 'spruce_planks' and rng.random() < (.08 if s.variant == 'tattered' else .24):
            s.blocks[pos] = b('oak_planks' if s.variant == 'tattered' else 'dark_oak_planks')
        if s.variant == 'abandoned' and block.name == 'lantern':
            s.blocks[pos] = AIR
    for side, z0, z1 in [(1, 43, 47), (-1, 71, 75)]:
        for z in range(z0, z1 + 1):
            x = CENTER + side * hull_width(z, 14)
            s.put(x, 15, z, AIR)
            if s.variant == 'tattered':
                s.put(x - side, 15, z, b('oak_fence'))
    if s.variant == 'abandoned':
        # Localized impact damage above the waterline keeps the derelict afloat.
        for x in range(10, 18):
            for z in range(65, 73):
                if ((x - 14) / 4) ** 2 + ((z - 69) / 4) ** 2 < 1:
                    s.put(x, 14, z, AIR)
        s.line((12, 15, 65), (17, 16, 76), BEAM)
        s.line((30, 15, 41), (38, 18, 53), b('spruce_log', pillar_axis='z'))
        # Moss on exposed boards and rotted cabin windows; sparse hanging growth.
        for x, z in [(17, 39), (33, 43), (16, 74), (29, 78)]:
            for dx in range(-2, 3):
                for dz in range(-3, 4):
                    pos = (x + dx, 15, z + dz)
                    if s.blocks.get(pos, AIR) == AIR and s.blocks.get((pos[0], 14, pos[2]), AIR) != AIR and rng.random() < .68:
                        s.put(*pos, b('moss_carpet'))
        for pos, block in list(s.blocks.items()):
            if block.name == 'light_blue_stained_glass' and rng.random() < .45:
                s.blocks[pos] = AIR
        for z in [90, 94, 99, 103]:
            for y in range(12, 15):
                # Attach each vine to the actual curved hull, facing west.
                s.put(CENTER + hull_width(z, y) + 1, y, z, b('vine', vine_direction_bits=2))


def build_ship(variant):
    s = Ship(variant)
    hull(s)
    platforms(s)
    cabin(s)
    deck_structure(s)
    rig(s)
    ship_hardware(s)
    age(s)
    secure_attachments(s)
    positions = [(20, 15, 42), (28, 15, 44), (21, 15, 71), (27, 15, 76),
                 (20, 19, 24), (28, 19, 25), (20, 22, 88), (27, 22, 99),
                 (20, 15, 90), (24, 10, 41), (24, 10, 74), (24, 10, 95)]
    s.crew = positions[:12 if variant == 'new' else 8 if variant == 'tattered' else 0]
    return s


def ship_hardware(s):
    """Exterior working-ship details, leaving the interior available to build in."""
    # Sternpost and a broad wooden rudder below the gallery, joined to the hull.
    s.box(CENTER, 1, 106, CENTER, 10, 106, b('stripped_dark_oak_log', pillar_axis='y'))
    for y in range(1, 10):
        tip = 109 if y in [1, 9] else 110
        s.box(CENTER, y, 107, CENTER, y, tip, HULL)
    for y in [3, 7]:
        s.box(CENTER, y, 106, CENTER, y, 109, b('polished_blackstone'))
    # Paired mooring bitts on the forecastle and quarterdeck, clear of stairs.
    for z, y in [(26, 19), (99, 22)]:
        for x in [17, 31]:
            for zz in [z, z + 2]:
                s.put(x, y, zz, b('stripped_dark_oak_log', pillar_axis='y'))
            s.box(x, y + 1, z - 1, x, y + 1, z + 3, BEAM)
    # A vanilla bell can be rung on the forecastle, next to the bow access.
    s.put(24, 19, 28, b('stripped_dark_oak_log', pillar_axis='y'))
    s.put(24, 20, 28, b('bell'))


def secure_attachments(s):
    # Stays meet mastheads; the solid timber still needs to support the ladder.
    for (x, y, z), block in list(s.blocks.items()):
        if block.name == 'ladder' and x in [25, 26]:
            support = (x - 1, y, z)
            if s.blocks.get(support, AIR).name == 'oak_fence':
                s.put(*support, b('spruce_log', pillar_axis='y'))
        if block.name.endswith('_carpet'):
            below = s.blocks.get((x, y - 1, z), AIR)
            if below == AIR or below.name == 'ladder':
                s.put(x, y, z, AIR)


# Small self-contained little-endian NBT encoder: Bedrock block states need byte
# booleans, unlike the terrain writer's integer-only palette. No engine code runs.
def nbt_string(value):
    data = value.encode('utf8')
    return struct.pack('<H', len(data)) + data


def payload(kind, value):
    if kind in [1, 3]:
        return struct.pack('<b' if kind == 1 else '<i', value)
    if kind == 8:
        return nbt_string(value)
    if kind == 9:
        subtype, items = value
        return bytes([subtype]) + struct.pack('<i', len(items)) + b''.join(payload(subtype, i) for i in items)
    if kind == 10:
        return b''.join(bytes([tag]) + nbt_string(key) + payload(tag, val)
                        for key, (tag, val) in value.items()) + b'\0'
    raise ValueError(kind)


def encode_piece(s, z0, z1):
    blocks = [s.blocks.get((x, y, z)) for x in range(SIZE[0]) for y in range(SIZE[1]) for z in range(z0, z1)]
    palette = list(dict.fromkeys(block for block in blocks if block is not None))
    ids = {block: i for i, block in enumerate(palette)}
    data = {
        'format_version': (3, 1), 'size': (9, (3, [SIZE[0], SIZE[1], z1 - z0])),
        'structure_world_origin': (9, (3, [0, 0, z0])),
        'structure': (10, {
            'block_indices': (9, (9, [(3, [ids[v] if v is not None else -1 for v in blocks]), (3, [-1] * len(blocks))])),
            'entities': (9, (10, [])),
            'palette': (10, {'default': (10, {
                'block_palette': (9, (10, [{
                    'name': (8, 'minecraft:' + block.name),
                    'version': (3, 18168865),
                    'states': (10, {k: (1 if isinstance(v, bool) else 3 if isinstance(v, int) else 8, v) for k, v in block.states})
                } for block in palette])),
                'block_position_data': (10, {})
            })})
        })
    }
    return b'\x0a\0\0' + payload(10, data)


def write_assets():
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = {'name': 'Dreadwake', 'size': SIZE, 'water_surface_y': WATER,
               'status': 'review only; not integrated into Endless Waters', 'variants': {}}
    for variant in VARIANTS:
        ship = build_ship(variant)
        folder = OUT / 'templates' / variant
        folder.mkdir(parents=True, exist_ok=True)
        parts = []
        for i, (z0, z1) in enumerate([(0, 58), (58, SIZE[2])]):
            data = encode_piece(ship, z0, z1)
            name = f'dreadwake_{variant}_{i}.mcstructure'
            (folder / name).write_bytes(data)
            parts.append({'file': f'templates/{variant}/{name}', 'offset': [0, 0, z0],
                          'size': [SIZE[0], SIZE[1], z1 - z0], 'sha256': hashlib.sha256(data).hexdigest()})
        palette = list(dict.fromkeys(ship.blocks.values()))
        idx = {block: i for i, block in enumerate(palette)}
        (OUT / f'{variant}.json').write_text(json.dumps({
            'size': SIZE, 'palette': [{'name': p.name, 'states': dict(p.states)} for p in palette],
            'blocks': [[*p, idx[b]] for p, b in ship.blocks.items()], 'crew': ship.crew,
        }, separators=(',', ':')))
        catalog['variants'][variant] = {
            'solid_blocks': sum(v != AIR for v in ship.blocks.values()),
            'actual_block_bounds': [[min(p[i] for p, b in ship.blocks.items() if b != AIR),
                                     max(p[i] for p, b in ship.blocks.items() if b != AIR)] for i in range(3)],
            'palette_entries': len(palette), 'planned_pillagers': len(ship.crew),
            'crew_positions': ship.crew, 'parts': parts, 'rooms': ship.zones,
        }
    (OUT / 'catalog.json').write_text(json.dumps(catalog, indent=2) + '\n')
    print(json.dumps({v: {k: d[k] for k in ['solid_blocks', 'palette_entries', 'planned_pillagers']} for v, d in catalog['variants'].items()}, indent=2))


if __name__ == '__main__':
    write_assets()
