"""Bedrock adaptations of Ocean Overhaul's MIT-licensed jellyfish/seahorse.

Model dimensions, UV coordinates, color textures and animation timing derive
from the pinned Java sources in third_party/ocean_overhaul. No Java is executed.
"""
from pathlib import Path
import json
import math
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'third_party/ocean_overhaul'
COLORS = {
    'jellyfish': ['green', 'blue', 'pink', 'red', 'orange'],
    'seahorse': ['yellow', 'orange', 'red', 'teal', 'purple'],
}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def geometry(species):
    # Java model Y grows down from 24; Bedrock model Y grows up from 0.
    bones = [{'name': 'root', 'pivot': [0, 0, 0]}]
    pivots = {'root': [0, 0, 0]}

    def part(name, parent, pivot, origin, size, uv, pitch=0):
        absolute = [a + b for a, b in zip(pivots[parent], pivot)]
        pivots[name] = absolute
        x, y, z = [a + b for a, b in zip(absolute, origin)]
        bone = {'name': name, 'parent': parent,
                'pivot': [absolute[0], 24-absolute[1], absolute[2]],
                'cubes': [{'origin': [x, 24-y-size[1], z], 'size': list(size), 'uv': list(uv)}]}
        if pitch:
            bone['rotation'] = [-math.degrees(pitch), 0, 0]
        bones.append(bone)

    if species == 'jellyfish':
        part('bell', 'root', (0,18,0), (-3,-3,-3), (6,4,6), (0,0))
        for i, (x,z) in enumerate([(-2,-2),(2,-2),(-2,2),(2,2)]):
            part(f'tentacle_{i}', 'bell', (x,1,z), (-.5,0,-.5), (1,5,1), (4*i,11))
    else:
        part('body', 'root', (0,18,0), (-1,-2,-1), (2,4,2), (0,0))
        part('head', 'body', (0,-2,0), (-1,-2,-2), (2,2,2), (8,0), .4363)
        part('snout', 'head', (0,0,0), (-.5,-1,-4), (1,1,2), (16,0))
        part('tail', 'body', (0,2,0), (-.5,0,-.5), (1,3,1), (0,8))
        part('tail_tip', 'tail', (0,3,0), (-.5,0,-2), (1,1,2), (4,8), .7854)
        part('fin', 'body', (0,0,1), (0,-2,0), (0,3,2), (24,0))
    return {'format_version': '1.12.0', 'minecraft:geometry': [{
        'description': {'identifier': f'geometry.endless.{species}',
                        'texture_width': 32, 'texture_height': 32,
                        'visible_bounds_width': 2, 'visible_bounds_height': 2,
                        'visible_bounds_offset': [0,.5,0]}, 'bones': bones}]}


def build(bp, rp):
    for pack in [bp, rp]:
        (pack / 'licenses').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / 'LICENSE', pack / 'licenses/Ocean_Overhaul_MIT.txt')
        (pack / 'licenses/Ocean_Overhaul_NOTICE.txt').write_text(
            'Jellyfish/seahorse models, textures, animation designs, diving-kit designs,\n'
            'equipment textures and four decorative-block textures adapted from\n'
            'Ocean Overhaul by tinyclaw / VoX. Copyright (c) 2026 tinyclaw / VoX.\n'
            'https://github.com/VoX/ocean-overhaul\n'
            'Source commit: c92b8faddec30aa6cc3664b2a3727e2dfee64440\n'
            'Licensed under MIT; see Ocean_Overhaul_MIT.txt.\n'
            'Bedrock behavior, geometry conversion and packaging adapted for Endless Waters.\n'
            'This is an unofficial adaptation, not the original Java mod.\n')
    translations = []
    for species, colors in COLORS.items():
        ident = f'endless:{species}'
        jelly = species == 'jellyfish'
        groups = {f'endless:color_{i}': {'minecraft:variant': {'value': i}} for i in range(5)}
        groups['endless:wild'] = {'minecraft:despawn': {'despawn_from_distance': {
            'min_distance': 48, 'max_distance': 64}}}
        groups['endless:pet'] = {'minecraft:persistent': {}}
        events = {
            'minecraft:entity_spawned': {'sequence': [
                {'add': {'component_groups': ['endless:wild']}},
                {'randomize': [{'weight': 1, 'add': {'component_groups': [f'endless:color_{i}']}}
                               for i in range(5)]}]},
            'endless:keep': {'remove': {'component_groups': ['endless:wild']},
                             'add': {'component_groups': ['endless:pet']}},
        }
        for i in range(5):
            events[f'endless:color_{i}'] = {
                'remove': {'component_groups': [f'endless:color_{j}' for j in range(5)]},
                'add': {'component_groups': [f'endless:color_{i}']}}
        speed = .065 if jelly else .09
        components = {
            'minecraft:type_family': {'family': [species, 'aquatic', 'mob']},
            'minecraft:variant': {'value': 0},
            'minecraft:health': {'value': 4 if jelly else 3, 'max': 4 if jelly else 3},
            'minecraft:collision_box': {'width': .45 if jelly else .25, 'height': .6 if jelly else .7},
            'minecraft:physics': {'has_gravity': False, 'has_collision': True},
            'minecraft:pushable': {'is_pushable': True, 'is_pushable_by_piston': True},
            'minecraft:movement': {'value': speed},
            'minecraft:underwater_movement': {'value': speed},
            'minecraft:movement.sway': {'sway_amplitude': 0},
            'minecraft:navigation.generic': {'can_swim': True, 'can_walk': False,
                'can_breach': False, 'can_path_over_water': False, 'can_sink': False,
                'is_amphibious': False},
            'minecraft:breathable': {'breathes_air': False, 'breathes_water': True,
                'total_supply': 15, 'suffocate_time': 0},
            'minecraft:behavior.random_swim': {'priority': 2, 'speed_multiplier': 1,
                'interval': 2, 'xz_dist': 6, 'y_dist': 3},
            'minecraft:behavior.swim_wander': {'priority': 3, 'interval': .2, 'look_ahead': 2},
            'minecraft:behavior.swim_idle': {'priority': 4},
            'minecraft:nameable': {'default_trigger': {'event': 'endless:keep', 'target': 'self'}},
            'minecraft:loot': {'table': f'loot_tables/entities/{species}.json'},
        }
        save(bp / f'entities/{species}.json', {'format_version': '1.26.0', 'minecraft:entity': {
            'description': {'identifier': ident, 'is_spawnable': True, 'is_summonable': True,
                            'is_experimental': False, 'spawn_category': 'water_ambient'},
            'component_groups': groups, 'components': components, 'events': events}})
        biome_filter = {'all_of': [{'test': 'has_biome_tag', 'value': 'ocean'},
                                  {'test': 'has_biome_tag', 'value': 'overworld'}]}
        if not jelly:
            biome_filter['all_of'].append({'any_of': [
                {'test': 'has_biome_tag', 'value': 'warm'},
                {'test': 'has_biome_tag', 'value': 'lukewarm'}]})
        save(bp / f'spawn_rules/{species}.json', {'format_version': '1.8.0', 'minecraft:spawn_rules': {
            'description': {'identifier': ident, 'population_control': 'water_animal'},
            'conditions': [{'minecraft:spawns_on_surface': {}, 'minecraft:spawns_underwater': {},
                'minecraft:weight': {'default': 6 if jelly else 4},
                'minecraft:height_filter': {'min': 20 if jelly else 38, 'max': 60},
                'minecraft:distance_filter': {'min': 12, 'max': 32},
                'minecraft:density_limit': {'surface': 4 if jelly else 3},
                'minecraft:herd': {'min_size': 1, 'max_size': 3 if jelly else 1},
                'minecraft:biome_filter': biome_filter}]}})
        entry = {'type': 'item', 'name': 'minecraft:slime_ball' if jelly else 'minecraft:bone_meal'}
        pool = {'rolls': 1, 'entries': [entry]}
        if jelly:
            entry['functions'] = [{'function': 'set_count', 'count': {'min': 0, 'max': 1}}]
        else:
            pool['conditions'] = [{'condition': 'random_chance', 'chance': .05}]
        save(bp / f'loot_tables/entities/{species}.json', {'pools': [pool]})
        save(rp / f'models/entity/{species}.geo.json', geometry(species))
        for color in colors:
            destination = rp / f'textures/entity/endless/{species}_{color}.png'
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / f'src/main/resources/assets/oceanoverhaul/textures/entity/{species}_{color}.png', destination)
        animation_id = f'animation.endless.{species}.swim'
        # Molang trigonometry uses degrees; Java used radians and ticks.
        if jelly:
            animated = {'bell': {'position': [0, '-math.cos(query.life_time * 171.887) * 0.5', 0]}}
            for i in range(4):
                animated[f'tentacle_{i}'] = {'rotation': [f'-math.cos(query.life_time * 114.592 + {i*57.296}) * 14.324',0,0]}
        else:
            animated = {
                'body': {'rotation': ['-math.sin(query.life_time * 114.592) * 3.438',0,0]},
                'tail': {'rotation': ['-11.459 - math.sin(query.life_time * 171.887) * 5.73',0,0]},
                'fin': {'rotation': [0,'math.cos(query.life_time * 1031.324) * 28.648',0]},
            }
        save(rp / f'animations/{species}.animation.json', {'format_version': '1.8.0',
            'animations': {animation_id: {'loop': True, 'bones': animated}}})
        controller = f'controller.render.endless.{species}'
        save(rp / f'render_controllers/{species}.render_controllers.json', {
            'format_version': '1.8.0', 'render_controllers': {controller: {
                'arrays': {'textures': {'Array.colors': [f'Texture.{c}' for c in colors]}},
                'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}],
                'textures': ['Array.colors[math.clamp(query.variant, 0, 4)]']}}})
        save(rp / f'entity/{species}.entity.json', {'format_version': '1.10.0', 'minecraft:client_entity': {
            'description': {'identifier': ident,
                'materials': {'default': 'entity_alphablend' if jelly else 'entity_alphatest'},
                'textures': {c: f'textures/entity/endless/{species}_{c}' for c in colors},
                'geometry': {'default': f'geometry.endless.{species}'},
                'animations': {'swim': animation_id}, 'scripts': {'animate': ['swim']},
                'render_controllers': [controller],
                'spawn_egg': {'base_color': '#5DDBCA' if jelly else '#ECC350',
                              'overlay_color': '#EF8DDD' if jelly else '#A76837'}}}})
        translations += [f'entity.{ident}.name={species.title()}',
                         f'item.spawn_egg.entity.{ident}.name={species.title()} Spawn Egg']
    save(rp / 'texts/languages.json', ['en_US'])
    (rp / 'texts/en_US.lang').write_text('\n'.join(translations) + '\n')
