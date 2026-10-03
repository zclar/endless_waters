from pathlib import Path
import json
import shutil
import zipfile
from nbt import structure

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'behavior_packs/endless_waters'
RESOURCES = ROOT / 'resource_packs/endless_waters'
DIST = ROOT / 'dist'
VERSION = [0, 2, 1]

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def feature(name, structure_name):
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
    save(PACK / 'features' / (name + '.json'), body)

def depth_selector(name, depths):
    conditions = []
    for index, depth in enumerate(depths):
        conditions.append({
            'places_feature': f'endless:land_{depth}',
            'condition': '1' if depth == depths[-1] else f'(query.noise(variable.worldx/192,variable.worldz/192)+1)/2 < {(index + 1)/len(depths):.9f}'
        })
    save(PACK / f'features/{name}.json', {
        'format_version': '1.21.40',
        'minecraft:conditional_list': {
            'description': {'identifier': f'endless:{name}'},
            'early_out_scheme': 'condition_success',
            'conditional_features': conditions
        }
    })

def ocean_biome(name, targets):
    deep = name.startswith('deep_')
    warm = name.removeprefix('deep_') == 'warm_ocean'
    climate = ('warm' if warm else 'lukewarm' if 'lukewarm' in name else 'cold' if 'cold' in name else 'medium')
    fog = name.removeprefix('deep_')
    tags = ['overworld', 'ocean', 'monster', 'fast_fishing', 'high_seas', 'temperate_ocean', climate]
    if deep: tags.append('deep')
    save(PACK / f'biomes/{name}.biome.json', {
        'format_version': '1.21.110',
        'minecraft:biome': {
            'description': {'identifier': f'minecraft:{name}'},
            'components': {
                'minecraft:climate': {
                    'temperature': 0.8 if warm else 0.5,
                    'downfall': 0.5, 'snow_accumulation': [0.0, 0.0]
                },
                'minecraft:surface_builder': {'builder': {
                    'type': 'minecraft:overworld', 'sea_floor_depth': 3,
                    'sea_floor_material': 'minecraft:sandstone',
                    'foundation_material': 'minecraft:stone',
                    'mid_material': 'minecraft:sandstone',
                    'top_material': 'minecraft:sandstone',
                    'sea_material': 'minecraft:water'
                }},
                'minecraft:overworld_height': {'noise_type': 'deep_ocean' if deep else 'ocean'},
                'minecraft:tags': {'tags': tags},
                'minecraft:replace_biomes': {'replacements': [{
                    'dimension': 'minecraft:overworld', 'targets': ['minecraft:' + target for target in targets],
                    'amount': 1.0, 'noise_frequency_scale': 1.0
                }]}
            }
        }
    })
    save(RESOURCES / f'biomes/{name}.client_biome.json', {
        'format_version': '1.21.110',
        'minecraft:client_biome': {
            'description': {'identifier': f'minecraft:{name}'},
            'components': {
                'minecraft:fog_appearance': {'fog_identifier': f'minecraft:fog_{fog}'},
                'minecraft:water_appearance': {'surface_color': '#02B0E5' if warm else '#0D96DB'},
                'minecraft:biome_music': {'underwater_music': True},
                'minecraft:ambient_sounds': {'underwater_loop': 'ambient.underwater.loop'}
            }
        }
    })

def main():
    if PACK.exists(): shutil.rmtree(PACK)
    if RESOURCES.exists(): shutil.rmtree(RESOURCES)
    if DIST.exists(): shutil.rmtree(DIST)
    (PACK / 'structures/endless').mkdir(parents=True)

    # Only reshape exposed terrain. Existing ocean floors and underwater
    # structures remain intact; -1 template entries preserve caves and ores
    # below the new seabed. Small templates avoid full-height placement.
    depths = list(range(16, 60))
    for depth in depths:
        floor_y = 62 - depth
        blocks = []
        for y in range(0, 63):
            if y <= floor_y - 5: block = None
            elif y <= floor_y: block = 'sandstone'
            elif y <= 62: block = 'water'
            blocks.append(block)
        (PACK / f'structures/endless/column_{depth}.mcstructure').write_bytes(
            structure((1, 63, 1), blocks))
        feature(f'column_{depth}', f'column_{depth}')
        save(PACK / f'features/reshape_{depth}.json', {
            'format_version': '1.21.40',
            'minecraft:aggregate_feature': {
                'description': {'identifier': f'endless:reshape_{depth}'},
                'features': [f'endless:column_{depth}', 'endless:clear_lower', 'endless:clear_upper'],
                'early_out': 'none'
            }
        })
        save(PACK / f'features/downshift_{depth}.json', {
            'format_version': '1.21.40',
            'minecraft:scatter_feature': {
                'description': {'identifier': f'endless:downshift_{depth}'},
                'places_feature': f'endless:reshape_{depth}',
                'distribution': {'iterations': 1, 'x': 0, 'y': -62, 'z': 0}
            }
        })
        save(PACK / f'features/land_{depth}.json', {
            'format_version': '1.21.40',
            'minecraft:sequence_feature': {
                'description': {'identifier': f'endless:land_{depth}'},
                'features': ['endless:land_gate', f'endless:downshift_{depth}']
            }
        })
    # Gate at the waterline: an already-water ocean column is skipped, so
    # shipwrecks, ruins, monuments, reefs, and native seabeds are not rewritten.
    save(PACK / 'features/land_gate.json', {
        'format_version': '1.21.40',
        'minecraft:single_block_feature': {
            'description': {'identifier': 'endless:land_gate'},
            'places_block': 'minecraft:water',
            'enforce_placement_rules': False, 'enforce_survivability_rules': False,
            'may_replace': ['minecraft:' + b for b in [
                'air', 'stone', 'deepslate', 'dirt', 'grass_block', 'sand', 'sandstone',
                'red_sand', 'red_sandstone', 'gravel', 'clay', 'mud', 'packed_mud',
                'granite', 'diorite', 'andesite', 'tuff', 'calcite', 'moss_block',
                'hardened_clay', 'snow', 'snow_layer', 'ice', 'packed_ice', 'blue_ice',
                'powder_snow', 'mycelium', 'podzol', 'dirt_with_roots',
                'coal_ore', 'iron_ore', 'copper_ore', 'gold_ore', 'emerald_ore',
                'white_terracotta', 'orange_terracotta', 'yellow_terracotta',
                'red_terracotta', 'brown_terracotta', 'light_gray_terracotta'
            ]]
        }
    })
    for name, y, height in [('lower', 63, 128), ('upper', 191, 129)]:
        (PACK / f'structures/endless/air_{name}.mcstructure').write_bytes(structure((1, height, 1), ['air'] * height))
        feature(f'air_{name}', f'air_{name}')
        save(PACK / f'features/clear_{name}.json', {
            'format_version': '1.21.40',
            'minecraft:scatter_feature': {
                'description': {'identifier': f'endless:clear_{name}'},
                'places_feature': f'endless:air_{name}',
                'distribution': {'iterations': 1, 'x': 0, 'y': y, 'z': 0}
            }
        })

    # A single feature is selected for every 1x1 position. The column's depth
    # is derived from coordinate noise, so exploration remains seed-stable and
    # does not repeat on a fixed finite map.
    depth_selector('depth_selector_shallow', list(range(16, 31)))
    depth_selector('depth_selector_deep', list(range(31, 60)))
    for category in ['shallow', 'deep']:
        save(PACK / f'feature_rules/endless_water_{category}.json', {
            'format_version': '1.21.40',
            'minecraft:feature_rules': {
                'description': {
                    'identifier': f'endless:endless_water_{category}',
                    'places_feature': f'endless:depth_selector_{category}'
                },
                'conditions': {
                    'placement_pass': 'after_surface_pass',
                    'minecraft:biome_filter': {'all_of': [
                        {'test': 'has_biome_tag', 'operator': '==', 'value': 'overworld'},
                        {'test': 'has_biome_tag', 'operator': '==' if category == 'deep' else '!=', 'value': 'deep'}
                    ]}
                },
                'distribution': {
                    'iterations': 256,
                    'coordinate_eval_order': 'xzy',
                    'x': {'distribution': 'fixed_grid', 'extent': [0, 15], 'step_size': 1},
                    'y': 62,
                    'z': {'distribution': 'fixed_grid', 'extent': [0, 15], 'step_size': 1}
                }
            }
        })
    # Terrain replacement alone leaves frozen vanilla climates behind.
    # Replace surface biomes and rivers. Keep native cave biomes so their
    # vegetation and biome-dependent underground structures can still spawn.
    targets = json.loads((ROOT / 'tools/overworld_biomes.json').read_text())
    groups = {name: [] for name in ['warm_ocean', 'lukewarm_ocean', 'deep_ocean', 'deep_cold_ocean', 'deep_warm_ocean', 'deep_lukewarm_ocean']}
    for target in targets:
        if target in ['deep_dark', 'dripstone_caves', 'lush_caves']: continue
        if target in ['deep_ocean', 'deep_cold_ocean', 'deep_warm_ocean', 'deep_lukewarm_ocean']:
            group = target
        elif target == 'deep_frozen_ocean':
            group = 'deep_cold_ocean'
        elif target in ['desert_hills', 'desert_mutated', 'jungle_hills', 'savanna', 'savanna_plateau', 'mesa_plateau', 'mesa_plateau_stone']:
            # Bedrock defines deep warm ocean but does not normally select it.
            # Give it real procedural regions rather than an unused JSON file.
            group = 'deep_warm_ocean'
        elif target == 'warm_ocean' or target.startswith(('desert', 'jungle', 'bamboo', 'savanna', 'mesa')):
            group = 'warm_ocean'
        else:
            group = 'lukewarm_ocean'
        groups[group].append(target)
    for name, biome_targets in groups.items(): ocean_biome(name, biome_targets)
    save(PACK / 'manifest.json', {
        'format_version': 2,
        'header': {
            'name': 'Endless Waters — Depths',
            'description': 'Ice-free warm and lukewarm oceans with shallow and deep variants.',
            'uuid': 'f64cd68d-5d41-4a25-b91b-36d5d8f33543',
            'version': VERSION,
            'min_engine_version': [1, 26, 50]
        },
        'modules': [{
            'type': 'data',
            'uuid': '2bc3df21-7c46-45b2-8c8d-bb3b2b8f3c0d',
            'version': VERSION
        }],
        'dependencies': [{'uuid': 'c2f260cf-3759-4ffd-b20d-a4fe8c0c45d3', 'version': VERSION}],
        'metadata': {'authors': ['zclar'], 'license': 'Apache-2.0'}
    })
    save(RESOURCES / 'manifest.json', {
        'format_version': 2,
        'header': {
            'name': 'Endless Waters — Ocean Appearance',
            'description': 'Vanilla ocean water and fog for the ice-free ocean biome.',
            'uuid': 'c2f260cf-3759-4ffd-b20d-a4fe8c0c45d3',
            'version': VERSION, 'min_engine_version': [1, 26, 50]
        },
        'modules': [{'type': 'resources', 'uuid': '84c04ce8-1b59-4c59-ae4a-d24e0b6ca727', 'version': VERSION}]
    })
    DIST.mkdir()
    with zipfile.ZipFile(DIST / 'Endless_Waters.mcaddon', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for folder, prefix in [(PACK, 'Endless_Waters_BP'), (RESOURCES, 'Endless_Waters_RP')]:
            for source in sorted(folder.rglob('*')):
                if source.is_file(): archive.write(source, prefix + '/' + source.relative_to(folder).as_posix())
    print(DIST / 'Endless_Waters.mcaddon')

if __name__ == '__main__': main()
