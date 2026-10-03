import json
from pathlib import Path
import zipfile
from nbt import loads

root = Path(__file__).resolve().parents[1]
pack = root / 'behavior_packs/endless_waters'
resources = root / 'resource_packs/endless_waters'
manifest = json.loads((pack / 'manifest.json').read_text())
assert manifest['header']['version'] == [0, 2, 1]
for folder in [pack, resources]:
    for path in folder.rglob('*.json'): json.loads(path.read_text())

for path in (pack / 'structures/endless').glob('column_*.mcstructure'):
    template = loads(path.read_bytes())
    assert template['size'] == [1, 63, 1]
    palette = template['structure']['palette']['default']['block_palette']
    column = [palette[i]['name'] if i != -1 else None for i in template['structure']['block_indices'][0]]
    assert len(column) == 63
    depth = int(path.stem.split('_')[-1])
    floor_y = 62 - depth
    assert column[floor_y] == 'minecraft:sandstone'
    assert column[floor_y + 1:] == ['minecraft:water'] * depth
    assert all(b is None for b in column[:max(0, floor_y-4)])
    assert not any('ice' in b or 'snow' in b for b in column if b is not None)

gate = json.loads((pack / 'features/land_gate.json').read_text())['minecraft:single_block_feature']
assert gate['places_block'] == 'minecraft:water'
assert 'minecraft:water' not in gate['may_replace']
assert not {'minecraft:chest', 'minecraft:prismarine', 'minecraft:oak_planks'} & set(gate['may_replace'])

for category, depths in [('shallow', range(16, 31)), ('deep', range(31, 60))]:
    selector = json.loads((pack / f'features/depth_selector_{category}.json').read_text())['minecraft:conditional_list']
    entries = selector['conditional_features']
    assert entries[-1]['condition'] == '1'
    assert [e['places_feature'] for e in entries] == [f'endless:land_{d}' for d in depths]
    rule = json.loads((pack / f'feature_rules/endless_water_{category}.json').read_text())['minecraft:feature_rules']
    assert rule['distribution']['y'] == 62
    assert rule['conditions']['placement_pass'] == 'after_surface_pass'
    assert rule['distribution']['iterations'] == 256
    assert rule['description']['places_feature'] == f'endless:depth_selector_{category}'

for name, height in [('lower', 128), ('upper', 129)]:
    template = loads((pack / f'structures/endless/air_{name}.mcstructure').read_bytes())
    assert template['size'] == [1, height, 1]
    assert template['structure']['palette']['default']['block_palette'][0]['name'] == 'minecraft:air'

targets = []
for path in (pack / 'biomes').glob('*.json'):
    biome = json.loads(path.read_text())['minecraft:biome']['components']
    assert biome['minecraft:climate']['temperature'] >= 0.5
    assert biome['minecraft:climate']['snow_accumulation'] == [0, 0]
    assert biome['minecraft:surface_builder']['builder']['type'] == 'minecraft:overworld'
    assert not {'frozen', 'ice_plains'} & set(biome['minecraft:tags']['tags'])
    replacement = biome['minecraft:replace_biomes']['replacements'][0]
    assert replacement['amount'] == 1
    assert replacement['dimension'] == 'minecraft:overworld'
    targets.extend(target.removeprefix('minecraft:') for target in replacement['targets'])
    assert (resources / 'biomes' / path.name.replace('.biome.json', '.client_biome.json')).is_file()
assert len(targets) == len(set(targets))
assert set(targets) == set(json.loads((root / 'tools/overworld_biomes.json').read_text())) - {'deep_dark', 'dripstone_caves', 'lush_caves'}
assert {'frozen_ocean', 'deep_frozen_ocean', 'legacy_frozen_ocean', 'frozen_river', 'ice_plains', 'frozen_peaks'} <= set(targets)
assert not {'hell', 'the_end'} & set(targets)
resource_manifest = json.loads((resources / 'manifest.json').read_text())
assert manifest['dependencies'][0]['uuid'] == resource_manifest['header']['uuid']
assert manifest['dependencies'][0]['version'] == resource_manifest['header']['version']
archive = root / 'dist/Endless_Waters.mcaddon'
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for folder, prefix in [(pack, 'Endless_Waters_BP'), (resources, 'Endless_Waters_RP')]:
        for path in folder.rglob('*'):
            if path.is_file(): assert z.read(prefix + '/' + path.relative_to(folder).as_posix()) == path.read_bytes()
print(f'Validated 44 depths, 6 ice-free biomes, {len(targets)} replacements, and {archive.stat().st_size:,} byte package.')
