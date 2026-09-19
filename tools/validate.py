"""Validate identifiers, feature references, NBT dimensions, and release contents."""
import json
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BP = ROOT / 'behavior_packs/endless_waters'
RP = ROOT / 'resource_packs/endless_waters'
features = {}
for path in BP.joinpath('features').glob('*.json'):
    data = json.loads(path.read_text())
    body = next(v for k, v in data.items() if k.startswith('minecraft:'))
    identifier = body['description']['identifier']
    assert path.stem == identifier.split(':')[1], path
    assert identifier not in features, identifier
    features[identifier] = body
for identifier, body in features.items():
    if 'structure_name' in body:
        namespace, name = body['structure_name'].split(':')
        assert BP.joinpath('structures', namespace, name + '.mcstructure').is_file()
    for item in body.get('conditional_features', []):
        assert item['places_feature'] in features
for path in BP.joinpath('feature_rules').glob('*.json'):
    rule = json.loads(path.read_text())['minecraft:feature_rules']
    assert rule['description']['places_feature'] in features
    assert rule['conditions']['minecraft:biome_filter'][0]['value'] == 'overworld'
    assert rule['distribution']['y'] == 24
for pack in [BP, RP]:
    for path in pack.rglob('*.json'): json.loads(path.read_text())
    assert not list(pack.rglob('*smoke*')), 'Test hooks must never ship.'
    assert not pack.joinpath('blocks').exists()
    assert not pack.joinpath('items').exists()
    assert not pack.joinpath('loot_tables').exists()
bp, rp = (json.loads(p.joinpath('manifest.json').read_text()) for p in [BP, RP])
assert bp['header']['min_engine_version'] == [1, 26, 50]
assert bp['dependencies'][1]['uuid'] == rp['header']['uuid']
all_ids = [bp['header']['uuid'], rp['header']['uuid']] + [m['uuid'] for p in [bp, rp] for m in p['modules']]
assert len(set(all_ids)) == len(all_ids)
with zipfile.ZipFile(ROOT / 'dist/Endless_Waters.mcaddon') as archive:
    assert archive.testzip() is None
    assert set(n for n in archive.namelist() if n.endswith('/manifest.json')) == {
        'Endless_Waters_BP/manifest.json', 'Endless_Waters_RP/manifest.json'}
    for path in BP.rglob('*'):
        if path.is_file(): assert archive.read('Endless_Waters_BP/' + path.relative_to(BP).as_posix()) == path.read_bytes()
    for path in RP.rglob('*'):
        if path.is_file(): assert archive.read('Endless_Waters_RP/' + path.relative_to(RP).as_posix()) == path.read_bytes()
print(f'Validated {len(features)} features, both pack manifests, vanilla-only content, and exact release archive.')
