"""Validate client references, source attribution and unchanged ocean generation."""
from pathlib import Path
import hashlib
import json
import math
import struct

ROOT = Path(__file__).resolve().parents[1]


def validate():
    bp = ROOT / 'behavior_packs/endless_waters'
    rp = ROOT / 'resource_packs/endless_waters'
    source = ROOT / 'third_party/ocean_overhaul'
    upstream = json.loads((source / 'UPSTREAM.json').read_text())
    for record in upstream['files']:
        assert hashlib.sha256((source / record['path']).read_bytes()).hexdigest() == record['sha256']
    for pack in [bp, rp]:
        assert (pack / 'licenses/Ocean_Overhaul_MIT.txt').read_bytes() == (source / 'LICENSE').read_bytes()
        assert upstream['commit'] in (pack / 'licenses/Ocean_Overhaul_NOTICE.txt').read_text()
    baseline = json.loads((ROOT / 'experiments/sea_life/terrain_baseline_040.json').read_text())
    actual = {}
    for folder in ['biomes','features','feature_rules','structures']:
        for path in (bp / folder).rglob('*'):
            if path.is_file(): actual[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for path in (rp / 'biomes').glob('*.json'):
        actual[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == baseline['files'], 'Ocean generation changed from approved v0.4.0'

    lang = (rp / 'texts/en_US.lang').read_text()
    for species in ['jellyfish','seahorse']:
        entity = json.loads((bp / f'entities/{species}.json').read_text())['minecraft:entity']
        client = json.loads((rp / f'entity/{species}.entity.json').read_text())['minecraft:client_entity']['description']
        spawn = json.loads((bp / f'spawn_rules/{species}.json').read_text())['minecraft:spawn_rules']
        assert entity['description']['identifier'] == client['identifier'] == spawn['description']['identifier']
        assert f'entity.endless:{species}.name=' in lang
        assert f'item.spawn_egg.entity.endless:{species}.name=' in lang
        c = entity['components']
        assert c['minecraft:breathable']['breathes_water'] and not c['minecraft:breathable']['breathes_air']
        assert not c['minecraft:navigation.generic']['can_breach']
        assert 'minecraft:attack' not in c
        assert not any('target' in key or 'attack' in key for key in c)
        assert (bp / c['minecraft:loot']['table']).is_file()
        groups = entity['component_groups']
        def event_refs(value):
            if isinstance(value, dict):
                for k,v in value.items():
                    if k == 'component_groups': assert set(v) <= groups.keys()
                    else: event_refs(v)
            elif isinstance(value, list):
                for v in value: event_refs(v)
        event_refs(entity['events'])
        assert c['minecraft:nameable']['default_trigger']['event'] in entity['events']
        for i in range(5):
            assert groups[f'endless:color_{i}']['minecraft:variant']['value'] == i
        for condition in spawn['conditions']:
            assert 'minecraft:spawns_underwater' in condition
            assert condition['minecraft:height_filter']['max'] <= 62
            assert condition['minecraft:density_limit']['surface'] <= 4
            assert 'ocean' in json.dumps(condition['minecraft:biome_filter'])
        g = json.loads((rp / f'models/entity/{species}.geo.json').read_text())['minecraft:geometry'][0]
        assert client['geometry']['default'] == g['description']['identifier']
        bone_names = {b['name'] for b in g['bones']}
        assert len(bone_names) == len(g['bones'])
        ancestors = {}
        for bone in g['bones']:
            parent = bone.get('parent')
            assert parent is None or parent in ancestors, 'Missing or cyclic bone parent'
            ancestors[bone['name']] = parent
            for cube in bone.get('cubes',[]):
                x,y,z = cube['size'];u,v = cube['uv']
                assert min(x,y,z) >= 0
                assert 0 <= u and u+2*(x+z) <= 32
                assert 0 <= v and v+y+z <= 32
                assert all(math.isfinite(n) for n in cube['origin'])
        animations = json.loads((rp / f'animations/{species}.animation.json').read_text())['animations']
        for animation_id in client['animations'].values():
            assert set(animations[animation_id]['bones']) <= bone_names
        assert set(client['scripts']['animate']) <= client['animations'].keys()
        controllers = json.loads((rp / f'render_controllers/{species}.render_controllers.json').read_text())['render_controllers']
        for name in client['render_controllers']:
            controller = controllers[name]
            refs = controller['arrays']['textures']['Array.colors']
            assert len(refs) == 5
            assert {x.removeprefix('Texture.') for x in refs} == client['textures'].keys()
        assert client['materials']['default'] in ['entity_alphablend','entity_alphatest']
        for path in client['textures'].values():
            texture = rp / (path + '.png');data = texture.read_bytes()
            assert data[:8] == b'\x89PNG\r\n\x1a\n'
            assert struct.unpack('>II',data[16:24]) == (32,32)
            original = source / 'src/main/resources/assets/oceanoverhaul/textures/entity' / texture.name
            assert data == original.read_bytes()
    print('Sea-life validation passed: models, textures, events, licenses and unchanged v0.4.0 terrain.')


if __name__ == '__main__':
    validate()
