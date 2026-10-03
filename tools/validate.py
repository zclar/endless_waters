"""Check cave protection, climate coverage and release packaging invariants."""
from pathlib import Path
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from nbt import loads

out = ROOT / 'dist'
bp = ROOT / 'behavior_packs/endless_waters'
rp = ROOT / 'resource_packs/endless_waters'

manifest = json.loads((bp / 'manifest.json').read_text())
resource_manifest = json.loads((rp / 'manifest.json').read_text())
assert manifest['header']['version'] == resource_manifest['header']['version'] == [0, 3, 0]
assert manifest['header']['uuid'] == 'f64cd68d-5d41-4a25-b91b-36d5d8f33543'
assert resource_manifest['header']['uuid'] == 'c2f260cf-3759-4ffd-b20d-a4fe8c0c45d3'
assert manifest['dependencies'] == [{'uuid': resource_manifest['header']['uuid'], 'version': [0, 3, 0]}]
assert len(list((bp / 'structures/endless').glob('column_*.mcstructure'))) == 59

for path in (bp / 'structures/endless').glob('column_*.mcstructure'):
    data = loads(path.read_bytes())
    depth = int(path.stem.split('_')[-1])
    floor = 62 - depth
    palette = data['structure']['palette']['default']['block_palette']
    column = [palette[i]['name'] if i >= 0 else None
              for i in data['structure']['block_indices'][0]]
    assert data['size'] == [1, 63, 1]
    assert all(b is None for b in column[:floor - 3]), path
    assert column[floor] == 'minecraft:sand', path
    assert column[floor + 1:] == ['minecraft:water'] * depth, path
    assert not any('ice' in b or 'snow' in b for b in column if b), path

definitions = {}
references = set()
for path in (bp / 'features').glob('*.json'):
    data = json.loads(path.read_text())
    body = next(v for k, v in data.items() if k.startswith('minecraft:'))
    definitions[body['description']['identifier']] = body
    if 'places_feature' in body:
        references.add(body['places_feature'])
    references.update(body.get('features', []))
    references.update(c['places_feature'] for c in body.get('conditional_features', []))
    if 'minecraft:scatter_feature' in data:
        assert 'distribution' in body, path
assert references <= definitions.keys(), references - definitions.keys()

rule = json.loads((bp / 'feature_rules/converted_ocean.json').read_text())['minecraft:feature_rules']
assert rule['distribution']['y'] == 62, 'Must sample the surface biome, not a cave biome'
assert rule['conditions']['placement_pass'] == 'before_surface_pass', 'Allow native ocean vegetation afterward'
assert definitions['endless:to_floor']['distribution']['y'] == -62
assert definitions['endless:exposed_only']['conditional_features'][0]['condition'].endswith('>62')
assert definitions['endless:clear_above']['distribution']['y'] == 63
assert definitions['endless:air_column']['distribution']['y']['extent'][0] == 0

targets = []
for path in (bp / 'biomes').glob('*.json'):
    data = json.loads(path.read_text())['minecraft:biome']
    components = data['components']
    assert components['minecraft:climate']['temperature'] >= 0.5
    assert components['minecraft:climate']['snow_accumulation'] == [0, 0]
    assert 'frozen' not in components['minecraft:tags']['tags']
    assert components['minecraft:surface_builder']['builder']['type'] == 'minecraft:overworld'
    if data['description']['identifier'].startswith('endless:converted_'):
        assert components['minecraft:surface_builder']['builder']['top_material'] == 'minecraft:sand'
    targets += components['minecraft:replace_biomes']['replacements'][0]['targets']
    client = rp / 'biomes' / path.name.replace('.biome.', '.client_biome.')
    assert json.loads(client.read_text())['minecraft:client_biome']['description'] == data['description']
expected = set(json.loads((ROOT / 'tools/overworld_biomes.json').read_text())) - {'lush_caves', 'dripstone_caves', 'deep_dark'}
assert len(targets) == len(set(targets))
assert {t.removeprefix('minecraft:') for t in targets} == expected

with zipfile.ZipFile(out / 'Endless_Waters.mcaddon') as archive:
    assert archive.testzip() is None
    for pack, prefix in [(bp, 'Endless_Waters_BP'), (rp, 'Endless_Waters_RP')]:
        for path in pack.rglob('*'):
            if path.is_file():
                assert archive.read(prefix + '/' + path.relative_to(pack).as_posix()) == path.read_bytes()
print('Release validation passed: cave-preserving columns, feature graph, ice-free climates and archive.')
