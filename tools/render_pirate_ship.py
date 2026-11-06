"""Render the real ship block layouts, including partial-block geometry.

Approximate material colors, not Minecraft textures or in-engine screenshots.
No AI-generated concept art is substituted for a build.
"""
from pathlib import Path
import json
import math
import re
from functools import lru_cache
import zipfile
from PIL import Image, ImageDraw, ImageFont
from pirate_ship import OUT, SIZE, WATER, VARIANTS, AIR, Block, build_ship

BOX = (0, 0, 0, 1, 1, 1)


@lru_cache(None)
def custom_boxes(block):
    root = Path(__file__).resolve().parents[1]
    path = root / 'behavior_packs/endless_waters/blocks/decor' / (block.name.split(':')[-1] + '.json')
    if not path.exists(): return [BOX]
    data = json.loads(path.read_text())['minecraft:block']
    components = dict(data['components'])
    for permutation in data.get('permutations', []):
        match = re.fullmatch(r"q.block_state\('([^']+)'\) == (.+)", permutation['condition'])
        if match:
            state, value = match.groups()
            value = value.strip("'") if value.startswith("'") else int(value)
            default = data['description'].get('states', {}).get(state, [0])[0]
            if block.state(state, default) == value: components.update(permutation['components'])
    identifier = components['minecraft:geometry']
    if isinstance(identifier, dict): identifier = identifier['identifier']
    geometry = geometry_index()[identifier]
    angle = math.radians(components.get('minecraft:transformation', {}).get('rotation', [0,0,0])[1])
    result = []
    for bone in geometry['bones']:
        for cube in bone.get('cubes', []):
            origin, size = cube['origin'], cube['size']
            corners = []
            for x in [origin[0],origin[0]+size[0]]:
                for z in [origin[2],origin[2]+size[2]]:
                    corners.append((.5+(x*math.cos(angle)+z*math.sin(angle))/16,
                                    .5+(-x*math.sin(angle)+z*math.cos(angle))/16))
            result.append((min(p[0] for p in corners),origin[1]/16,min(p[1] for p in corners),
                           max(p[0] for p in corners),(origin[1]+size[1])/16,max(p[1] for p in corners)))
    return result or [BOX]


@lru_cache(None)
def geometry_index():
    root = Path(__file__).resolve().parents[1] / 'resource_packs/endless_waters/models/blocks'
    return {g['description']['identifier']:g for p in root.rglob('*.json')
            for g in json.loads(p.read_text()).get('minecraft:geometry',[])}


def boxes(block, neighbors):
    if block.name.startswith('endless:decor_'): return custom_boxes(block)
    n = block.name
    if n == 'air':
        return []
    if n.endswith('_slab'):
        return [(0, .5 if block.state('minecraft:vertical_half') == 'top' else 0, 0,
                 1, 1 if block.state('minecraft:vertical_half') == 'top' else .5, 1)]
    if n.endswith('_carpet'):
        return [(0, 0, 0, 1, .0625, 1)]
    if n.endswith('_stairs'):
        upside = block.state('upside_down_bit', False)
        y0, y1 = (0, .5) if upside else (.5, 1)
        direction = block.state('weirdo_direction', 0)
        step = [(0.5, y0, 0, 1, y1, 1), (0, y0, 0, .5, y1, 1),
                (0, y0, .5, 1, y1, 1), (0, y0, 0, 1, y1, .5)][direction]
        return [(0, .5 if upside else 0, 0, 1, 1 if upside else .5, 1), step]
    if n.endswith('_fence') or n in ['iron_bars', 'polished_blackstone_wall']:
        radius = .125 if n.endswith('fence') else .07 if n == 'iron_bars' else .25
        result = [(.5 - radius, 0, .5 - radius, .5 + radius, 1, .5 + radius)]
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            other = neighbors(dx, 0, dz)
            if other is None or other == AIR or other.name in ['chain', 'lantern', 'vine', 'web']:
                continue
            for y in [.35, .75] if n.endswith('fence') else [.3, .7]:
                result.append((0 if dx < 0 else .43, y, 0 if dz < 0 else .43,
                               1 if dx > 0 else .57, y + .13, 1 if dz > 0 else .57))
        return result
    if n == 'chain':
        return [(.44, 0, .44, .56, 1, .56)]
    if n == 'lantern':
        return [(.25, .15, .25, .75, .75, .75), (.35, .75, .35, .65, 1, .65)]
    if n == 'ladder':
        d = block.state('facing_direction', 2)
        if d in [4, 5]:
            lo, hi = (.86, 1) if d == 4 else (0, .14)
            return [(lo, 0, .15, hi, 1, .25), (lo, 0, .75, hi, 1, .85)] + [(lo, y, .15, hi, y + .08, .85) for y in [.15, .45, .75]]
        lo, hi = (.86, 1) if d == 2 else (0, .14)
        return [(.15, 0, lo, .25, 1, hi), (.75, 0, lo, .85, 1, hi)] + [(.15, y, lo, .85, y + .08, hi) for y in [.15, .45, .75]]
    if n.endswith('_button'):
        return [(0, .35, .35, .15, .65, .65)] if block.state('facing_direction') == 4 else [(.85, .35, .35, 1, .65, .65)]
    if n == 'chest':
        return [(.06, 0, .06, .94, .86, .94)]
    if n == 'grindstone':
        return [(.3, 0, .3, .7, .4, .7), (.15, .4, .2, .85, 1, .8)]
    if n == 'anvil':
        return [(.15, 0, .15, .85, .25, .85), (.3, .25, .3, .7, .75, .7), (0, .75, .15, 1, 1, .85)]
    if n == 'lectern':
        return [(0, 0, 0, 1, .12, 1), (.3, .12, .3, .7, .75, .7), (.05, .75, 0, .95, 1, 1)]
    if n in ['vine', 'web']:
        return [(0, 0, .45, 1, 1, .55), (.45, 0, 0, .55, 1, 1)]
    if n in ['cauldron', 'composter']:
        return [(0, 0, 0, 1, .2, 1), (0, .2, 0, .15, 1, 1), (.85, .2, 0, 1, 1, 1),
                (.15, .2, 0, .85, 1, .15), (.15, .2, .85, .85, 1, 1)]
    return [BOX]


def color(block):
    n = block.name
    colors = {'white_wool': (223, 218, 192), 'white_carpet': (226, 220, 199),
              'black_wool': (42, 44, 43), 'red_wool': (142, 43, 37), 'red_carpet': (141, 40, 37),
              'brown_wool': (101, 77, 54), 'light_gray_wool': (159, 155, 139),
              'red_terracotta': (128, 60, 43), 'yellow_terracotta': (186, 133, 56),
              'light_blue_stained_glass': (83, 157, 164), 'lantern': (244, 182, 67),
              'chain': (62, 69, 72), 'iron_bars': (72, 83, 84), 'barrel': (133, 97, 56),
              'chest': (157, 100, 42), 'bookshelf': (131, 99, 64), 'web': (172, 175, 160),
              'moss_carpet': (72, 105, 58), 'vine': (62, 94, 50), 'air': (0, 0, 0)}
    if n in colors:
        return colors[n]
    if 'polished_blackstone' in n:
        return (49, 53, 57)
    if n.startswith('stripped_spruce'):
        return (121, 86, 49)
    if 'dark_oak' in n:
        return (79, 54, 35) if 'stripped' not in n else (102, 70, 42)
    if 'spruce' in n:
        return (145, 106, 63) if 'planks' in n or 'slab' in n else (93, 66, 41)
    if 'oak' in n:
        return (176, 141, 83)
    if n in ['anvil', 'cauldron', 'furnace', 'smoker', 'grindstone', 'stone_brick_slab']:
        return (84, 89, 89)
    return (133, 101, 64)


FACES = [
    ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
    ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
    ((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
    ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
    ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
    ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
]


def mesh(ship, cut=None):
    blocks = {p: b for p, b in ship.blocks.items() if b != AIR and
              (cut is None or (p[0] <= 24 if cut == 'section' else p[1] < cut))}
    shapes = {p: boxes(b, lambda dx, dy, dz: blocks.get((p[0] + dx, p[1] + dy, p[2] + dz))) for p, b in blocks.items()}
    faces = []
    for pos, block in blocks.items():
        x, y, z = pos
        for shape in shapes[pos]:
            x0, y0, z0, x1, y1, z1 = shape
            for normal, vertices in FACES:
                if shape == BOX and shapes.get((x + normal[0], y + normal[1], z + normal[2])) == [BOX]:
                    continue
                points = [(x + x0 + a * (x1 - x0), y + y0 + b * (y1 - y0), z + z0 + c * (z1 - z0)) for a, b, c in vertices]
                c = color(block)
                variation = .96 + ((x * 31 + y * 17 + z * 13) % 11) * .008
                c = tuple(min(255, int(channel * variation)) for channel in c)
                faces.append((points, normal, c, block.name))
    return faces


def font(size, bold=False):
    return ImageFont.truetype('DejaVuSans' + ('-Bold' if bold else '') + '.ttf', size)


def render(ship, name, camera=(1.5, .95, -1.3), cut=None):
    faces = mesh(ship, cut)
    length = math.sqrt(sum(v * v for v in camera))
    eye = tuple(v / length for v in camera)
    horiz = math.hypot(eye[0], eye[2])
    right = (eye[2] / horiz, 0, -eye[0] / horiz)
    up = (-eye[0] * eye[1] / horiz, horiz, -eye[2] * eye[1] / horiz)
    def dot(p, q):
        return sum(a * b for a, b in zip(p, q))
    visible = [(points, normal, c, n) for points, normal, c, n in faces if dot(normal, eye) > .001]
    extents = [(dot(p, right), dot(p, up)) for points, _, _, _ in visible for p in points]
    xmin, xmax = min(p[0] for p in extents), max(p[0] for p in extents)
    ymin, ymax = min(p[1] for p in extents), max(p[1] for p in extents)
    width, height = 2200, 1700 if cut is None else 1400
    scale = min((width - 180) / (xmax - xmin), (height - 310) / (ymax - ymin))
    dx = (width - (xmax - xmin) * scale) / 2
    dy = 165 + ((height - 310) - (ymax - ymin) * scale) / 2
    def project(p):
        return (dx + (dot(p, right) - xmin) * scale, dy + (ymax - dot(p, up)) * scale)
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / height
        draw.line((0, y, width, y), fill=(int(221 - 27 * t), int(235 - 17 * t), int(232 - 9 * t)))
    # Sea reference plane only; the actual block hull below it receives a blue tint.
    sea = [(0, WATER, -2), (49, WATER, -2), (49, WATER, 116), (0, WATER, 116)]
    draw.polygon([project(p) for p in sea], fill=(134, 184, 187))
    for z in range(0, 116, 8):
        draw.line([project((0, WATER, z)), project((49, WATER, z))], fill=(153, 196, 196), width=1)
    visible.sort(key=lambda f: dot(tuple(sum(p[i] for p in f[0]) / 4 for i in range(3)), eye))
    for points, normal, col, material in visible:
        shade = .72 + .28 * max(0, dot(normal, (.35, .84, -.4)))
        c = tuple(int(v * shade) for v in col)
        if max(p[1] for p in points) <= WATER and cut is None:
            c = tuple(int(a * .7 + b * .3) for a, b in zip(c, (87, 143, 151)))
        p = [project(v) for v in points]
        outline = tuple(max(0, int(v * .84)) for v in c)
        draw.polygon(p, fill=c, outline=outline)
        # Subtle board joints and barrel hoops, not copied game textures.
        if material == 'barrel' and normal[1] == 0:
            for t in [.18, .78]:
                a = tuple(points[0][i] * (1 - t) + points[1][i] * t for i in range(3))
                bb = tuple(points[3][i] * (1 - t) + points[2][i] * t for i in range(3))
                draw.line([project(a), project(bb)], fill=(70, 65, 53), width=1)
    title = 'THE DREADWAKE'
    draw.text((65, 37), title, font=font(42, True), fill=(29, 54, 57))
    label = ship.variant.upper() + {None: '', 'section': ' / INTERIOR SECTION', 14: ' / GUN DECK',
                                    9: ' / LOWER HOLD', 21: ' / MAIN DECK + CABIN'}[cut]
    draw.text((67, 91), label, font=font(21), fill=(59, 92, 93))
    draw.text((width - 660, 47), 'ORIGINAL BEDROCK BUILD · REVIEW 01', font=font(22), fill=(53, 88, 90))
    draw.text((65, height - 100), f'116-block build envelope  /  three masts  /  {len(ship.crew)} planned pillagers', font=font(23), fill=(29, 59, 63))
    draw.text((65, height - 61), 'Rendered from the structure blocks. Approximate materials; not a Minecraft screenshot.', font=font(20), fill=(70, 98, 100))
    image.save(OUT / name)
    print(name, len(faces), 'faces')


def write_viewer(ships):
    # Offline WebGL viewer: actual boxes, a depth buffer, orbit/zoom and deck cuts.
    template = (Path(__file__).parent / 'ship_viewer.html').read_text()
    data = {}
    for ship in ships:
        palette = list(dict.fromkeys(ship.blocks.values()))
        ids = {v: i for i, v in enumerate(palette)}
        data[ship.variant] = {'blocks': [[*p, ids[v]] for p, v in ship.blocks.items() if v != AIR],
                             'palette': [{'name': b.name, 'states': dict(b.states), 'color': color(b), **({'boxes': custom_boxes(b)} if b.name.startswith('endless:decor_') else {})} for b in palette],
                             'crew': ship.crew}
    (OUT / 'VIEW_SHIP.html').write_text(template.replace('/*SHIP_DATA*/{}', json.dumps(data, separators=(',', ':'))))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ships = [build_ship(v) for v in VARIANTS]
    for ship in ships:
        render(ship, ship.variant + '.png')
        render(ship, ship.variant + '_stern.png', (-1.8, .85, 1.1))
    render(ships[0], 'interior_section.png', (2, 1, -.6), 'section')
    render(ships[0], 'gun_deck.png', (1, 2, -.8), 14)
    render(ships[0], 'lower_hold.png', (1, 2, -.8), 9)
    render(ships[0], 'main_deck.png', (1, 2, -.8), 21)
    thumbs = Image.new('RGB', (1800, 464), '#d7e8e6')
    for i, variant in enumerate(VARIANTS):
        im = Image.open(OUT / (variant + '.png'))
        im.thumbnail((600, 635))
        thumbs.paste(im, (i * 600, 0))
    thumbs.save(OUT / 'comparison.png')
    write_viewer(ships)
    archive = OUT.parents[2] / 'dist/Dreadwake_Ship_Previews.zip'
    archive.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(OUT.glob('*.png')) + [OUT / 'VIEW_SHIP.html', OUT / 'README.md']:
            bundle.write(path, path.name)
    print('Preview bundle:', archive)


if __name__ == '__main__':
    main()
