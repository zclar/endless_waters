from pathlib import Path
import json
import shutil
import zipfile
from nbt import structure

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'behavior_packs/endless_waters'
DIST = ROOT / 'dist'

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def feature(name, structure_name, condition=None):
    body = {
        'format_version': '1.21.40',
        'minecraft:structure_template_feature': {
            'description': {'identifier': 'endless:' + name},
            'structure_name': 'endless:' + structure_name,
            'adjustment_radius': 0,
            'facing_direction': 'north',
            'constraints': {}
        }
    }
    if condition is not None:
        body['minecraft:conditional_list'] = None
    save(PACK / 'features' / (name + '.json'), body)

def main():
    if PACK.exists(): shutil.rmtree(PACK)
    if DIST.exists(): shutil.rmtree(DIST)
    (PACK / 'structures/endless').mkdir(parents=True)

    # Y=-64..320. The surface is always water at Y=62. The deterministic
    # selected seabed is 16..59 blocks below the waterline.
    depths = list(range(16, 60))
    for depth in depths:
        floor_y = 62 - depth
        blocks = []
        for y in range(-64, 321):
            if y <= floor_y - 5: block = 'stone'
            elif y <= floor_y: block = 'sandstone'
            elif y <= 62: block = 'water'
            else: block = 'air'
            blocks.append(block)
        (PACK / f'structures/endless/column_{depth}.mcstructure').write_bytes(
            structure((1, 385, 1), blocks))
        feature(f'column_{depth}', f'column_{depth}')

    # A single feature is selected for every 1x1 position. The column's depth
    # is derived from coordinate noise, so exploration remains seed-stable and
    # does not repeat on a fixed finite map.
    conditions = []
    for depth in depths:
        threshold = (depth - 16) / len(depths)
        conditions.append({
            'places_feature': f'endless:column_{depth}',
            'condition': f'(query.noise(variable.worldx/192,variable.worldz/192)+1)/2 >= {threshold:.6f} && (query.noise(variable.worldx/192,variable.worldz/192)+1)/2 < {threshold + 1/len(depths):.6f}'
        })
    save(PACK / 'features/depth_selector.json', {
        'format_version': '1.21.40',
        'minecraft:conditional_list': {
            'description': {'identifier': 'endless:depth_selector'},
            'early_out_scheme': 'condition_success',
            'conditional_features': conditions
        }
    })
    save(PACK / 'feature_rules/endless_water.json', {
        'format_version': '1.21.40',
        'minecraft:feature_rules': {
            'description': {'identifier': 'endless:endless_water', 'places_feature': 'endless:depth_selector'},
            'conditions': {
                'placement_pass': 'final_pass',
                'minecraft:biome_filter': [{'test': 'has_biome_tag', 'operator': '==', 'value': 'overworld'}]
            },
            'distribution': {
                'iterations': 256,
                'coordinate_eval_order': 'xzy',
                'x': {'distribution': 'fixed_grid', 'extent': [0, 15], 'step_size': 1},
                'y': 0,
                'z': {'distribution': 'fixed_grid', 'extent': [0, 15], 'step_size': 1}
            }
        }
    })
    save(PACK / 'manifest.json', {
        'format_version': 2,
        'header': {
            'name': 'Endless Waters — Depths',
            'description': 'Endless Overworld water with procedural shallow, ocean, deep-ocean, and trench depths.',
            'uuid': 'f64cd68d-5d41-4a25-b91b-36d5d8f33543',
            'version': [0, 2, 0],
            'min_engine_version': [1, 26, 50]
        },
        'modules': [{
            'type': 'data',
            'uuid': '2bc3df21-7c46-45b2-8c8d-bb3b2b8f3c0d',
            'version': [0, 2, 0]
        }],
        'metadata': {'authors': ['zclar'], 'license': 'Apache-2.0'}
    })
    DIST.mkdir()
    with zipfile.ZipFile(DIST / 'Endless_Waters.mcpack', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sorted(PACK.rglob('*')):
            if source.is_file(): archive.write(source, source.relative_to(PACK).as_posix())
    print(DIST / 'Endless_Waters.mcpack')

if __name__ == '__main__': main()
