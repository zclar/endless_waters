"""Prepare an isolated BDS builder, then package its saved vanilla flat world.

Run prepare against a stopped official server with worlds/metadata-seed/level.dat.
Start the server, wait for DREADWAKE_READY, stop/restart to verify persistence,
stop it again, then run package. The temporary builder pack is never shipped.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from bedrock_world import read_level, write_level
from pirate_ship import ROOT, VARIANTS, SIZE, build_ship, encode_piece

REVIEW = ROOT / 'experiments/ship_review'
WORLD = 'Dreadwake Shipyard - Furnished Edition'
DECOR_BP = 'd642ff49-c715-4238-9407-10eff54a3cd5'
DECOR_RP = '7a70e36c-ccec-420e-861a-17a2b44a55fe'
DECOR_VERSION = [0, 6, 0]
PACK_ID = '0ed1764c-c80a-48fa-8e1d-d417df3d9aea'
MODULE_ID = '94751ecf-b27b-47c3-8f63-2057c0242114'
DATA_ID = '53306d6a-de17-4f16-8a4b-6c6827ce091c'
ORIGINS = {'new': [0, -60, 0], 'tattered': [96, -60, 0], 'abandoned': [192, -60, 0]}


def review_packs(server):
    bp=server/'development_behavior_packs/dreadwake_decor'
    rp=server/'development_resource_packs/dreadwake_decor'
    for target in [bp,rp]:
        if target.exists():shutil.rmtree(target)
        target.mkdir(parents=True)
    for folder in ['blocks','items','recipes','loot_tables']:
        shutil.copytree(ROOT/'behavior_packs/endless_waters'/folder,bp/folder)
    shutil.copytree(ROOT/'resource_packs/endless_waters',rp,dirs_exist_ok=True)
    (bp/'scripts').mkdir(exist_ok=True)
    for script in ['decor.js','decor_logic.js','harpoon.js']:
        shutil.copy2(ROOT/'scripts'/script,bp/'scripts'/script)
    (bp/'entities').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'behavior_packs/endless_waters/entities/harpoon.json',bp/'entities/harpoon.json')
    for source in (ROOT/'behavior_packs/endless_waters').glob('*.txt'):shutil.copy2(source,bp/source.name)
    for target,uuid,module in [(bp,DECOR_BP,'2db8d35a-0234-4460-964f-28be9fd53d60'),(rp,DECOR_RP,'e6b3a965-d34d-4673-9fa3-3e96f58beb12')]:
        manifest={'format_version':2,'header':{'name':'Dreadwake Review Decorations','description':'Furnishings for the isolated ship review world','uuid':uuid,'version':DECOR_VERSION,'min_engine_version':[1,26,60]},
                  'modules':[{'type':'data' if target==bp else 'resources','uuid':module,'version':DECOR_VERSION}]}
        if target==bp:
            manifest['dependencies']=[{'uuid':DECOR_RP,'version':DECOR_VERSION},{'module_name':'@minecraft/server','version':'2.10.0'}]
            manifest['modules'].append({'type':'script','language':'javascript','uuid':'7b18c2a8-456c-4e6d-a79c-577b20bc25e3','version':DECOR_VERSION,'entry':'scripts/decor.js'})
        else:manifest['capabilities']=['pbr']
        (target/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return bp,rp


def prepare(server, world_name):
    REVIEW.mkdir(parents=True, exist_ok=True)
    review_packs(server)
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
        'dependencies': [{'module_name': '@minecraft/server', 'version': '2.10.0'}, {'uuid': DECOR_BP, 'version': DECOR_VERSION}],
    }
    (pack / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    data = {}
    for variant in VARIANTS:
        ship = build_ship(variant)
        palette = list(dict.fromkeys(ship.blocks.values()))
        ids = {block: i for i, block in enumerate(palette)}
        for index, (z0, z1) in enumerate([(0, 58), (58, 116)]):
            (pack / f'structures/dreadwake/{variant}_{index}.mcstructure').write_bytes(encode_piece(ship, z0, z1))
        data[variant] = {'origin': ORIGINS[variant], 'crew': ship.crew, 'loot': ship.loot,
                         'palette': [{'name': b.name, 'states': dict(b.states)} for b in palette],
                         'blocks': [[*p, ids[b]] for p, b in ship.blocks.items()],
                         'size': SIZE}
    definitions=[]
    for path in sorted((ROOT/'behavior_packs/endless_waters/blocks/decor').glob('*.json')):
        block=json.loads(path.read_text())['minecraft:block']
        definitions.append({'id':block['description']['identifier'],'states':block['description'].get('states',{}),
                            'interaction':block['components'].get('endless:decor_interact')})
    probe=build_ship('new')
    from pirate_ship import b
    probe.blocks={(0,0,0):b('chest',facing_direction=2)}
    probe.loot=[{'position':[0,0,0],'table':'loot_tables/ships/new_vault.json'}]
    (pack/'structures/dreadwake/loot_probe.mcstructure').write_bytes(encode_piece(probe,0,58))
    serialized = json.dumps(data, separators=(',', ':'))
    build_id = hashlib.sha256(serialized.encode() + (REVIEW / 'build_world.js').read_bytes()).hexdigest()
    (pack / 'scripts/data.js').write_text('export const SHIPS = ' + serialized + ';\n' +
                                        'export const BUILD_ID = ' + json.dumps(build_id) + ';\n' +
                                        'export const DECOR = ' + json.dumps(definitions) + ';\n' +
                                        'export const ITEMS = ' + json.dumps([e['id'] for e in json.loads((ROOT/'experiments/decor/catalog.json').read_text())['entries']]) + ';\n')
    shutil.copy2(REVIEW / 'build_world.js', pack / 'scripts/main.js')
    shutil.copy2(ROOT/'scripts/decor_logic.js',pack/'scripts/decor_logic.js')
    contents = {'build_id': build_id, 'interiors': 'fully furnished', 'loot': 'native tables, randomized on first access',
                'variants': {v: {k: d[k] for k in ['origin', 'crew', 'loot']} for v, d in data.items()}}
    (REVIEW / 'contents.json').write_text(json.dumps(contents, indent=2) + '\n')
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
    (world / 'world_behavior_packs.json').write_text(json.dumps([{'pack_id': PACK_ID, 'version': [1, 0, 0]}, {'pack_id': DECOR_BP, 'version': DECOR_VERSION}]))
    (world / 'world_resource_packs.json').write_text(json.dumps([{'pack_id': DECOR_RP, 'version': DECOR_VERSION}]))
    props = server / 'server.properties'
    lines = [f'level-name={world_name}' if s.startswith('level-name=') else s for s in props.read_text().splitlines()]
    props.write_text('\n'.join(lines) + '\n')
    print('Prepared', world, 'with isolated builder pack')


def package(server, world_name):
    world = server / 'worlds' / world_name
    build_id = json.loads((REVIEW / 'contents.json').read_text())['build_id']
    reports = []
    decor_reports = []
    for log in sorted(server.glob('ContentLog*.txt')):
        for line in log.read_text(errors='replace').splitlines():
            if 'DREADWAKE_DECOR_REPORT ' in line:
                decor_reports.append(json.loads(line.split('DREADWAKE_DECOR_REPORT ', 1)[1]))
            if 'DREADWAKE_REPORT ' in line:
                report = json.loads(line.split('DREADWAKE_REPORT ', 1)[1])
                if report.get('buildId') == build_id:
                    reports.append(report)
    assert len(reports) >= 2 and reports[-2]['phase'] == 'built' and reports[-2]['passed'], 'Missing successful current build report'
    assert reports[-1]['phase'] == 'reload' and reports[-1]['passed'], 'Missing successful current reload report'
    assert decor_reports and decor_reports[-1]['passed'], 'Missing decoration validation'
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
        z.writestr('world_behavior_packs.json', json.dumps([{'pack_id': DECOR_BP, 'version': DECOR_VERSION}]))
        z.writestr('world_resource_packs.json', json.dumps([{'pack_id': DECOR_RP, 'version': DECOR_VERSION}]))
        for kind in ['behavior','resource']:
            pack=server/f'development_{kind}_packs/dreadwake_decor'
            for asset in sorted(pack.rglob('*')):
                if asset.is_file():z.write(asset,f'{kind}_packs/dreadwake_decor/'+asset.relative_to(pack).as_posix())
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
        assert not any('dreadwake_builder' in n for n in z.namelist())
    result = {'bedrock_version': '1.26.63.1', 'minimum_client': metadata['MinimumCompatibleClientVersion'][1][1],
              'checks': reports[-2:], 'decor_checks': decor_reports[-1], 'archive_bytes': archive.stat().st_size,
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'runtime_packs_included': True, 'world_generator': 'flat', 'game_mode': 'creative'}
    (REVIEW / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'package'])
    parser.add_argument('--server-dir', type=Path, required=True)
    parser.add_argument('--world', default='dreadwake-furnished-04')
    args = parser.parse_args()
    (prepare if args.action == 'prepare' else package)(args.server_dir, args.world)
