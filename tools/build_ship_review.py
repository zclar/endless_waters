"""Prepare an isolated BDS builder, then package its saved vanilla flat world.

Run prepare against a stopped official server with worlds/metadata-seed/level.dat.
Start the server, wait for DREADWAKE_READY, stop/restart to verify persistence,
stop it again, then run package. The temporary builder pack is never shipped.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil
import zipfile
from bedrock_world import read_level, write_level
from pirate_ship import ROOT, VARIANTS, SIZE, AIR, build_ship, encode_piece

REVIEW = ROOT / 'experiments/ship_review'
WORLD = 'Dreadwake Shipyard'
PACK_ID = '0ed1764c-c80a-48fa-8e1d-d417df3d9aea'
MODULE_ID = '94751ecf-b27b-47c3-8f63-2057c0242114'
DATA_ID = '53306d6a-de17-4f16-8a4b-6c6827ce091c'
ORIGINS = {'new': [0, -60, 0], 'tattered': [96, -60, 0], 'abandoned': [192, -60, 0]}


def provisions(variant):
    rng = random.Random({'new': 1706, 'tattered': 2791, 'abandoned': 8842}[variant])
    roles = [
        ([17, 15, 101], 'captain'), ([32, 15, 89], 'navigation'),
        ([18, 10, 93], 'armory'), ([30, 10, 93], 'workshop'),
        ([17, 10, 33], 'pantry'), ([31, 10, 35], 'pantry'),
        ([18, 6, 63], 'cargo'), ([29, 7, 64], 'cargo'),
        ([17, 7, 72], 'cargo'), ([30, 6, 73], 'cargo'),
        ([18, 6, 81], 'cargo'), ([29, 7, 83], 'cargo'),
        ([29, 5, 99], 'hidden'),
    ]
    choices = {
        'captain': [('emerald', 3, 7), ('gold_ingot', 2, 5), ('amethyst_shard', 2, 5), ('diamond', 1, 1)],
        'navigation': [('compass', 1, 1), ('spyglass', 1, 1), ('paper', 5, 12), ('book', 1, 3)],
        'armory': [('crossbow', 1, 1), ('arrow', 12, 24), ('iron_ingot', 2, 5), ('gunpowder', 3, 8)],
        'workshop': [('iron_ingot', 2, 6), ('copper_ingot', 3, 8), ('coal', 4, 10), ('iron_axe', 1, 1)],
        'pantry': [('cooked_cod', 3, 8), ('bread', 3, 6), ('dried_kelp', 4, 10), ('carrot', 2, 5)],
        'cargo': [('spruce_planks', 6, 14), ('string', 3, 8), ('coal', 2, 5), ('iron_nugget', 3, 8)],
        'hidden': [('emerald', 1, 3), ('gold_nugget', 4, 9), ('amethyst_shard', 1, 3)],
    }
    loot = []
    for index, (position, role) in enumerate(roles):
        if variant == 'abandoned' and index not in [0, 1, 3, 8, 12]:
            continue
        items = []
        for name, lo, hi in choices[role]:
            if variant != 'new' and name == 'diamond':
                continue
            amount = rng.randint(lo, hi)
            if variant != 'new':
                amount = max(1, amount // 2)
            if variant == 'abandoned' and name in ['iron_axe', 'coal']:
                name = 'bone' if name == 'iron_axe' else 'rotten_flesh'
            items.append({'name': name, 'amount': amount})
        loot.append({'position': position, 'role': role, 'items': items})
    return loot


def prepare(server, world_name):
    REVIEW.mkdir(parents=True, exist_ok=True)
    pack = server / 'development_behavior_packs/dreadwake_builder'
    (pack / 'structures/dreadwake').mkdir(parents=True, exist_ok=True)
    (pack / 'scripts').mkdir(exist_ok=True)
    manifest = {
        'format_version': 2,
        'header': {'name': 'Dreadwake isolated world builder', 'description': 'Local build and diagnostics only',
                   'uuid': PACK_ID, 'version': [1, 0, 0], 'min_engine_version': [1, 26, 60]},
        'modules': [{'type': 'data', 'uuid': DATA_ID, 'version': [1, 0, 0]},
                    {'type': 'script', 'language': 'javascript', 'uuid': MODULE_ID,
                     'version': [1, 0, 0], 'entry': 'scripts/main.js'}],
        'dependencies': [{'module_name': '@minecraft/server', 'version': '2.10.0'}],
    }
    (pack / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    data = {}
    for variant in VARIANTS:
        ship = build_ship(variant)
        palette = list(dict.fromkeys(ship.blocks.values()))
        ids = {block: i for i, block in enumerate(palette)}
        for index, (z0, z1) in enumerate([(0, 58), (58, 116)]):
            (pack / f'structures/dreadwake/{variant}_{index}.mcstructure').write_bytes(encode_piece(ship, z0, z1))
        loot = provisions(variant)
        for container in loot:
            assert ship.blocks[tuple(container['position'])].name in ['chest', 'barrel'], container
        data[variant] = {'origin': ORIGINS[variant], 'crew': ship.crew, 'loot': loot,
                         'palette': [{'name': b.name, 'states': dict(b.states)} for b in palette],
                         'blocks': [[*p, ids[b]] for p, b in ship.blocks.items()],
                         'size': SIZE}
    (pack / 'scripts/data.js').write_text('export const SHIPS = ' + json.dumps(data, separators=(',', ':')) + ';\n')
    shutil.copy2(REVIEW / 'build_world.js', pack / 'scripts/main.js')
    (REVIEW / 'contents.json').write_text(json.dumps({v: {k: d[k] for k in ['origin', 'crew', 'loot']} for v, d in data.items()}, indent=2) + '\n')
    world = server / 'worlds' / world_name
    if not (world / 'level.dat').exists():
        world.mkdir(parents=True, exist_ok=True)
        version, name, metadata = read_level(server / 'worlds/metadata-seed/level.dat')
        metadata.update({'Generator': (3, 2), 'LevelName': (8, WORLD), 'GameType': (3, 1),
                         'SpawnX': (3, 120), 'SpawnY': (3, -51), 'SpawnZ': (3, -10),
                         'spawnradius': (3, 0), 'domobspawning': (1, 0), 'spawnMobs': (1, 0),
                         'dodaylightcycle': (1, 0), 'doweathercycle': (1, 0), 'Time': (4, 6000),
                         'showcoordinates': (1, 1), 'commandsEnabled': (1, 1),
                         'doimmediaterespawn': (1, 1)})
        write_level(world / 'level.dat', version, name, metadata)
        (world / 'levelname.txt').write_text(WORLD)
    (world / 'world_behavior_packs.json').write_text(json.dumps([{'pack_id': PACK_ID, 'version': [1, 0, 0]}]))
    props = server / 'server.properties'
    lines = [f'level-name={world_name}' if s.startswith('level-name=') else s for s in props.read_text().splitlines()]
    props.write_text('\n'.join(lines) + '\n')
    print('Prepared', world, 'with isolated builder pack')


def package(server, world_name):
    world = server / 'worlds' / world_name
    reports = []
    for log in sorted(server.glob('ContentLog*.txt')):
        for line in log.read_text(errors='replace').splitlines():
            if 'DREADWAKE_REPORT ' in line:
                reports.append(json.loads(line.split('DREADWAKE_REPORT ', 1)[1]))
    assert any(r['phase'] == 'built' and r['passed'] for r in reports), 'Missing successful build report'
    assert reports[-1]['phase'] == 'reload' and reports[-1]['passed'], 'Missing successful reload report'
    version, name, metadata = read_level(world / 'level.dat')
    assert metadata['Generator'] == (3, 2)
    metadata.update({'LevelName': (8, WORLD), 'GameType': (3, 1), 'ForceGameType': (1, 0),
                     'SpawnX': (3, 120), 'SpawnY': (3, -51), 'SpawnZ': (3, -10),
                     'spawnradius': (3, 0), 'showcoordinates': (1, 1), 'commandsEnabled': (1, 1),
                     'MultiplayerGame': (1, 0), 'MultiplayerGameIntent': (1, 0)})
    temp_level = server / 'shipyard-export-level.dat'
    write_level(temp_level, version, name, metadata)
    archive = ROOT / 'dist/Dreadwake_Shipyard.mcworld'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(temp_level, 'level.dat')
        z.writestr('levelname.txt', WORLD)
        z.writestr('world_behavior_packs.json', '[]')
        z.writestr('world_resource_packs.json', '[]')
        for p in sorted((world / 'db').iterdir()):
            if p.is_file() and p.name != 'LOCK':
                z.write(p, 'db/' + p.name)
        # Android displays this native-sized thumbnail in the world list.
        from PIL import Image
        from io import BytesIO
        icon = Image.open(ROOT / 'experiments/structure_previews/dreadwake/new.png').convert('RGB')
        icon.thumbnail((455, 256))
        canvas = Image.new('RGB', (455, 256), '#d6e7e5')
        canvas.paste(icon, ((455 - icon.width) // 2, (256 - icon.height) // 2))
        output = BytesIO(); canvas.save(output, format='JPEG', quality=88)
        z.writestr('world_icon.jpeg', output.getvalue())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert not any(n.startswith(('behavior_packs/', 'resource_packs/')) for n in z.namelist())
    result = {'bedrock_version': '1.26.61.1', 'minimum_client': metadata['MinimumCompatibleClientVersion'][1][1],
              'checks': reports[-2:], 'archive_bytes': archive.stat().st_size,
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'runtime_packs_included': False, 'world_generator': 'flat', 'game_mode': 'creative'}
    (REVIEW / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'package'])
    parser.add_argument('--server-dir', type=Path, required=True)
    parser.add_argument('--world', default='dreadwake-review')
    args = parser.parse_args()
    (prepare if args.action == 'prepare' else package)(args.server_dir, args.world)
