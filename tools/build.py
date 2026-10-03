"""Build Endless Waters 0.3.0 from the tested procedural seabed generator."""
from pathlib import Path
import json
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from nbt import structure

OUT = ROOT / 'dist'
BP = ROOT / 'behavior_packs/endless_waters'
RP = ROOT / 'resource_packs/endless_waters'
VERSION = [0, 3, 0]


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def feature(name, kind, **body):
    save(BP / f'features/{name}.json', {
        'format_version': '1.26.10',
        'minecraft:' + kind: {
            'description': {'identifier': 'endless:' + name}, **body
        }
    })


def ocean_biome(name, targets):
    deep = name.startswith('deep_')
    warm = name.removeprefix('deep_') == 'warm_ocean'
    climate = ('warm' if warm else 'lukewarm' if 'lukewarm' in name else 'cold' if 'cold' in name else 'medium')
    fog = name.removeprefix('deep_')
    tags = ['overworld', 'ocean', 'monster', 'fast_fishing', 'high_seas', 'temperate_ocean', climate]
    if deep: tags.append('deep')
    save(BP / f'biomes/{name}.biome.json', {
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
    save(RP / f'biomes/{name}.client_biome.json', {
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
    OUT.mkdir(exist_ok=True)
    # These two directories are generated outputs owned by this builder.
    for target in [BP, RP]:
        if target.exists():
            shutil.rmtree(target)
        (target / 'biomes').mkdir(parents=True)
    for folder in ['features', 'feature_rules', 'structures/endless']:
        (BP / folder).mkdir(parents=True)
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

    # Distinguish real ocean regions from land that receives an ocean biome.
    # Native ocean regions keep their engine-generated floors and vegetation.
    for path in list((BP / 'biomes').glob('*.json')):
        data = json.loads(path.read_text())
        components = data['minecraft:biome']['components']
        builder = components['minecraft:surface_builder']['builder']
        builder.update(top_material='minecraft:grass_block',
                       mid_material='minecraft:dirt',
                       sea_floor_material=('minecraft:sand' if 'warm' in path.stem
                                           else 'minecraft:gravel'))
        targets = components['minecraft:replace_biomes']['replacements'][0]['targets']
        native = [t for t in targets if 'ocean' in t]
        land = [t for t in targets if 'ocean' not in t]
        if native:
            components['minecraft:replace_biomes']['replacements'][0]['targets'] = native
            save(path, data)
        else:
            path.unlink()
        if land:
            converted = json.loads(json.dumps(data))
            identifier = 'endless:converted_' + path.stem.removesuffix('.biome')
            converted['minecraft:biome']['description']['identifier'] = identifier
            cc = converted['minecraft:biome']['components']
            # Dry depressions can begin below sea level. Give them ocean soil
            # from the surface pass itself, including ledges below overhangs.
            cc['minecraft:surface_builder']['builder']['top_material'] = 'minecraft:sand'
            cc['minecraft:replace_biomes']['replacements'][0]['targets'] = land
            cc['minecraft:tags']['tags'].append('endless_converted_land')
            save(BP / 'biomes' / ('converted_' + path.name), converted)
            client = json.loads((RP / 'biomes' / path.name.replace('.biome.', '.client_biome.')).read_text())
            client['minecraft:client_biome']['description']['identifier'] = identifier
            save(RP / 'biomes' / ('converted_' + path.name.replace('.biome.', '.client_biome.')), client)

    # Select depth using the seed-dependent original terrain. The shoreline
    # tends toward shallow water; former hills become broad underwater basins.
    # One formula across all converted biomes avoids depth jumps at their edges.
    height = 'math.max(0,query.heightmap(variable.worldx,variable.worldz)-62)'
    depth = f'(1+58*({height})/(({height})+40))'
    choices = []
    for d in range(1, 60):
        floor = 62 - d
        blocks = [None if y < floor - 3 else 'sandstone' if y == floor - 3
                  else 'sand' if y <= floor else 'water' for y in range(63)]
        (BP / f'structures/endless/column_{d}.mcstructure').write_bytes(
            structure((1, 63, 1), blocks))
        feature(f'column_{d}', 'structure_template_feature',
                structure_name=f'endless:column_{d}', adjustment_radius=0,
                facing_direction='north', constraints={})
        feature(f'reshape_{d}', 'aggregate_feature',
                features=[f'endless:column_{d}', 'endless:clear_above'],
                early_out='none')
        choices.append({'places_feature': f'endless:reshape_{d}',
                        'condition': '1' if d == 59 else f'{depth} < {d+1}'})
    feature('air', 'single_block_feature', places_block='minecraft:air',
            enforce_placement_rules=False, enforce_survivability_rules=False)
    # Clear only as high as the old surface; avoid rewriting hundreds of
    # already-air blocks per column. Calculate the bound once before clearing.
    feature('clear_above', 'scatter_feature', places_feature='endless:air_column',
            distribution={'iterations': 1, 'x': 0, 'y': 63, 'z': 0})
    feature('air_column', 'scatter_feature', places_feature='endless:air',
            distribution={
                'iterations': 'v.endless_clear_count=math.max(0,math.min(320,query.heightmap(variable.worldx,variable.worldz))-63);return v.endless_clear_count;',
                'x': 0, 'z': 0,
                'y': {'distribution': 'fixed_grid', 'step_size': 1,
                      'extent': [0, 'v.endless_clear_count-1']}})
    feature('height_selector', 'conditional_list', early_out_scheme='condition_success',
            conditional_features=choices)
    # A low surface is not necessarily wet: inland depressions may contain
    # air below sea level. Fill only that air above their highest solid block.
    feature('water', 'single_block_feature', places_block='minecraft:water',
            enforce_placement_rules=False, enforce_survivability_rules=False,
            may_replace=['minecraft:air'])
    feature('low_water_start', 'scatter_feature', places_feature='endless:low_water_column',
            distribution={'iterations': 1, 'x': 0, 'z': 0,
                          'y': 'v.endless_low_y=math.max(0,query.above_top_solid(variable.worldx,variable.worldz));return v.endless_low_y;'})
    feature('low_water_column', 'scatter_feature', places_feature='endless:water',
            distribution={'iterations': 'math.max(0,63-v.endless_low_y)', 'x': 0, 'z': 0,
                          'y': {'distribution': 'fixed_grid', 'step_size': 1,
                                'extent': [0, 'math.max(0,62-v.endless_low_y)']}})
    feature('low_surface', 'single_block_feature', places_block='minecraft:sand',
            enforce_placement_rules=False, enforce_survivability_rules=False,
            may_replace=['minecraft:grass_block', 'minecraft:dirt', 'minecraft:coarse_dirt',
                         'minecraft:podzol', 'minecraft:mycelium'])
    feature('low_surface_start', 'scatter_feature', places_feature='endless:low_surface',
            distribution={'iterations': 1, 'x': 0, 'z': 0,
                          'y': 'math.max(0,query.above_top_solid(variable.worldx,variable.worldz)-1)'})
    feature('flood_low', 'aggregate_feature',
            features=['endless:low_water_start', 'endless:low_surface_start'], early_out='none')
    # Keep every already-submerged floor, including rivers through continents.
    # This also avoids filling a shallow lake over a deeper native cave mouth.
    feature('exposed_only', 'conditional_list', early_out_scheme='condition_success',
            conditional_features=[{'places_feature': 'endless:height_selector',
                                   'condition': 'query.above_top_solid(variable.worldx,variable.worldz)>62'},
                                  {'places_feature': 'endless:flood_low', 'condition': '1'}])
    feature('to_floor', 'scatter_feature', places_feature='endless:exposed_only',
            distribution={'iterations': 1, 'x': 0, 'y': -62, 'z': 0})
    save(BP / 'feature_rules/converted_ocean.json', {
        'format_version': '1.26.10', 'minecraft:feature_rules': {
            'description': {'identifier': 'endless:converted_ocean',
                            'places_feature': 'endless:to_floor'},
            'conditions': {'placement_pass': 'before_surface_pass',
                           'minecraft:biome_filter': {'test': 'has_biome_tag',
                                                     'operator': '==',
                                                     'value': 'overworld'}},
            # Evaluate the SURFACE biome. At Y=0, cave biomes can prevent this
            # rule from firing and leave entire patches of original land.
            'distribution': {'iterations': 256, 'coordinate_eval_order': 'xzy',
                             'x': {'distribution': 'fixed_grid', 'extent': [0, 15], 'step_size': 1},
                             'y': 62,
                             'z': {'distribution': 'fixed_grid', 'extent': [0, 15], 'step_size': 1}}
        }
    })
    # Preserve the installed pack identities so imports upgrade v0.2.1.
    bp_id = 'f64cd68d-5d41-4a25-b91b-36d5d8f33543'
    rp_id = 'c2f260cf-3759-4ffd-b20d-a4fe8c0c45d3'
    for pack, name, ident, module in [
        (BP, 'Endless Waters — Depths', bp_id, '2bc3df21-7c46-45b2-8c8d-bb3b2b8f3c0d'),
        (RP, 'Endless Waters — Ocean Appearance', rp_id, '84c04ce8-1b59-4c59-ae4a-d24e0b6ca727')
    ]:
        data = {
            'format_version': 2,
            'header': {'name': name, 'uuid': ident, 'version': VERSION,
                       'min_engine_version': [1, 26, 50],
                       'description': 'Procedural ice-free oceans, native seabeds and caves.'},
            'modules': [{'type': 'data' if pack == BP else 'resources',
                         'uuid': module, 'version': VERSION}]
        }
        if pack == BP:
            data['metadata'] = {'authors': ['zclar'], 'license': 'Apache-2.0'}
        if pack == BP:
            data['dependencies'] = [{'uuid': rp_id, 'version': [0, 3, 0]}]
        save(pack / 'manifest.json', data)
    archive = OUT / 'Endless_Waters.mcaddon'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for pack, prefix in [(BP, 'Endless_Waters_BP'), (RP, 'Endless_Waters_RP')]:
            for path in sorted(pack.rglob('*')):
                if path.is_file():
                    z.write(path, prefix + '/' + path.relative_to(pack).as_posix())
    print(archive)


if __name__ == '__main__':
    main()
