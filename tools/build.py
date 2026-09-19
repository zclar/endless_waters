"""Generate native worldgen definitions and reproducible importable packs."""
import json
from pathlib import Path
import zipfile
from nbt import structure

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'behavior_packs/endless_waters'
RESOURCE = ROOT / 'resource_packs/endless_waters'

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def feature(name, kind, **values):
    save(PACK / 'features' / (name + '.json'), {
        'format_version': '1.21.40',
        'minecraft:' + kind: {'description': {'identifier': 'endless:' + name}, **values}
    })

def selector(low, high):
    if low == high: return 'endless:column_' + str(low)
    middle = (low + high) // 2
    name = f'select_{low}_{high}'
    left, right = selector(low, middle), selector(middle + 1, high)
    feature(name, 'conditional_list', early_out_scheme='condition_success', conditional_features=[
        {'places_feature': left, 'condition': f'v.ew_height <= {middle}'},
        {'places_feature': right, 'condition': '1'}
    ])
    return 'endless:' + name

def generate():
    # Stable biome replacement supplies actual ocean spawning and a navigable,
    # unfrozen sea. Cave biomes, the Nether, and the End are not replacement targets.
    surface_biomes = '''bamboo_jungle bamboo_jungle_hills beach birch_forest birch_forest_hills
birch_forest_hills_mutated birch_forest_mutated cherry_grove cold_beach cold_ocean cold_taiga
cold_taiga_hills cold_taiga_mutated dappled_forest deep_cold_ocean deep_frozen_ocean
deep_lukewarm_ocean deep_ocean deep_warm_ocean desert desert_hills desert_mutated extreme_hills
extreme_hills_edge extreme_hills_mutated extreme_hills_plus_trees extreme_hills_plus_trees_mutated
flower_forest forest forest_hills frozen_ocean frozen_peaks frozen_river grove ice_mountains
ice_plains ice_plains_spikes jagged_peaks jungle jungle_edge jungle_edge_mutated jungle_hills
jungle_mutated legacy_frozen_ocean lukewarm_ocean mangrove_swamp meadow mega_taiga mega_taiga_hills
mesa mesa_bryce mesa_plateau mesa_plateau_mutated mesa_plateau_stone mesa_plateau_stone_mutated
mushroom_island mushroom_island_shore ocean pale_garden plains redwood_taiga_hills_mutated
redwood_taiga_mutated river roofed_forest roofed_forest_mutated savanna savanna_mutated
savanna_plateau savanna_plateau_mutated snowy_slopes stone_beach stony_peaks sunflower_plains
swampland swampland_mutated taiga taiga_hills taiga_mutated warm_ocean'''.split()
    save(PACK / 'biomes/archipelago_ocean.biome.json', {
        'format_version': '1.26.30',
        'minecraft:biome': {
            'description': {'identifier': 'endless:archipelago_ocean'},
            'components': {
                'minecraft:climate': {'temperature': 0.8, 'downfall': 0.6, 'snow_accumulation': [0, 0]},
                'minecraft:tags': {'tags': ['overworld', 'ocean', 'lukewarm', 'animal', 'monster']},
                'minecraft:surface_builder': {'builder': {'type': 'minecraft:overworld',
                    'sea_floor_depth': 4, 'sea_floor_material': 'minecraft:sand',
                    'foundation_material': 'minecraft:stone', 'mid_material': 'minecraft:dirt',
                    'top_material': 'minecraft:grass_block', 'sea_material': 'minecraft:water'}},
                'minecraft:replace_biomes': {'replacements': [{'dimension': 'minecraft:overworld',
                    'targets': ['minecraft:' + b for b in surface_biomes], 'amount': 1.0, 'noise_frequency_scale': 1.0}]}
            }
        }
    })
    ocean = []
    for x in range(16):
        for y in range(24, 320):
            for z in range(16):
                ocean.append('air' if y > 62 else 'water' if y > 31 else 'sand' if y == 31 else 'sandstone' if y > 27 else 'stone')
    path = PACK / 'structures/endless/ocean_chunk.mcstructure'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(structure((16, 296, 16), ocean))
    feature('ocean_chunk', 'structure_template_feature', structure_name='endless:ocean_chunk',
            adjustment_radius=0, facing_direction='north', constraints={})
    save(PACK / 'feature_rules/ocean.json', {
        'format_version': '1.21.40',
        'minecraft:feature_rules': {
            'description': {'identifier': 'endless:ocean', 'places_feature': 'endless:ocean_chunk'},
            'conditions': {'placement_pass': 'after_surface_pass',
                'minecraft:biome_filter': [{'test': 'has_biome_tag', 'operator': '==', 'value': 'overworld'}]},
            'distribution': {'iterations': 1, 'x': 0, 'y': 24, 'z': 0}
        }
    })
    for height in range(28, 86):
        blocks = []
        for y in range(24, 86):
            if y > max(height, 62): block = 'air'
            elif y > height: block = 'water'
            elif y == height: block = 'sand' if height <= 65 else 'grass_block'
            elif y >= height - 3: block = 'sandstone' if height <= 65 else 'dirt'
            else: block = 'stone'
            blocks.append(block)
        path = PACK / 'structures/endless' / f'column_{height}.mcstructure'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(structure((1, 62, 1), blocks))
        feature(f'column_{height}', 'structure_template_feature',
                structure_name=f'endless:column_{height}', adjustment_radius=0,
                facing_direction='north', constraints={})

    # Every column is entirely within its owning chunk. No neighboring chunk can
    # erase an island edge; native generation runs once, before players arrive.
    root = selector(28, 85)
    expression = (
        'v.ew_cx=math.floor(v.worldx/224);v.ew_cz=math.floor(v.worldz/224);'
        'v.ew_s=173;'
        'v.ew_dx=v.worldx-(v.ew_cx*224+112);v.ew_dz=v.worldz-(v.ew_cz*224+112);'
        'v.ew_radius=66+10*query.noise(v.ew_cx*7+v.ew_s,v.ew_cz*7+91);'
        'v.ew_d=math.sqrt(v.ew_dx*v.ew_dx+v.ew_dz*v.ew_dz)/v.ew_radius;'
        'v.ew_present=query.noise(v.ew_cx*13+37,v.ew_cz*13+v.ew_s)>-0.52;'
        'v.ew_present=(v.ew_cx==0 && v.ew_cz==0)?1:v.ew_present;'
        'v.ew_height=math.floor(math.clamp(31+v.ew_present*47*math.max(0,1-math.pow(v.ew_d,4))'
        '+3*query.noise(v.worldx/24+v.ew_s,v.worldz/24),28,85));return v.ew_present && v.ew_d<1;'
    )
    feature('terrain_column', 'conditional_list', early_out_scheme='condition_success', conditional_features=[
        {'places_feature': root, 'condition': expression}
    ])
    save(PACK / 'feature_rules/archipelago.json', {
        'format_version': '1.21.40',
        'minecraft:feature_rules': {
            'description': {'identifier': 'endless:archipelago', 'places_feature': 'endless:terrain_column'},
            'conditions': {'placement_pass': 'final_pass',
                           'minecraft:biome_filter': [{'test': 'has_biome_tag', 'operator': '==', 'value': 'overworld'}]},
            'distribution': {'iterations': 256, 'coordinate_eval_order': 'xzy',
                             'x': {'distribution': 'fixed_grid', 'extent': [0, 15], 'step_size': 1},
                             'z': {'distribution': 'fixed_grid', 'extent': [0, 15], 'step_size': 1}, 'y': 24}
        }
    })

def package():
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    outputs = [
        ('Endless_Waters.mcaddon', [(PACK, 'Endless_Waters_BP/'), (RESOURCE, 'Endless_Waters_RP/')]),
        ('Endless_Waters_BP.mcpack', [(PACK, '')]),
        ('Endless_Waters_RP.mcpack', [(RESOURCE, '')])
    ]
    for filename, packs in outputs:
        path = dist / filename
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for pack, prefix in packs:
                for source in sorted(pack.rglob('*')):
                    if not source.is_file(): continue
                    info = zipfile.ZipInfo(prefix + source.relative_to(pack).as_posix(), (2026, 9, 19, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o644 << 16
                    archive.writestr(info, source.read_bytes())
        print(f'{path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)')

if __name__ == '__main__':
    generate()
    package()
