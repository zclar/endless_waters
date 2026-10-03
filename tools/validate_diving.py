"""Check survival recipe dependencies, equipment assets and visual-pack isolation."""
from pathlib import Path
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]


def validate():
    bp = ROOT / 'behavior_packs/endless_waters'
    rp = ROOT / 'resource_packs/endless_waters'
    read = lambda p: json.loads(p.read_text())
    definitions = {}
    for kind, key in [('blocks', 'minecraft:block'), ('items', 'minecraft:item')]:
        for path in (bp / kind).glob('*.json'):
            body = read(path)[key]
            definitions[body['description']['identifier']] = body
    assert len(definitions) == 7
    recipes = {}
    for path in (bp / 'recipes').glob('*.json'):
        body = read(path)['minecraft:recipe_shaped']
        result = body['result']['item']
        assert result in definitions and result not in recipes
        assert 1 <= body['result']['count'] <= 64
        assert body['tags'] == ['crafting_table']
        pattern = body['pattern']
        assert 1 <= len(pattern) <= 3 and 1 <= len(pattern[0]) <= 3
        assert len({len(row) for row in pattern}) == 1
        assert set(''.join(pattern)) - {' '} == body['key'].keys()
        recipes[result] = {v['item'] for v in body['key'].values()}
        assert all(v.startswith('minecraft:') or v in definitions for v in recipes[result])
    assert recipes.keys() == definitions.keys()

    def vanilla_leaves(item, visiting):
        if item.startswith('minecraft:'):
            return {item}
        assert item not in visiting, 'Circular survival crafting dependency'
        return set().union(*(vanilla_leaves(v, visiting | {item}) for v in recipes[item]))
    for item in recipes:
        assert vanilla_leaves(item, set())
    suit = ['endless:deep_sea_helmet', 'endless:oxygen_tank', 'endless:flippers']
    assert all(not any('prismarine' in ingredient or ingredient == 'minecraft:sea_lantern'
                       for ingredient in vanilla_leaves(item, set())) for item in suit)
    sea_glass = read(bp / 'recipes/sea_glass.json')['minecraft:recipe_shaped']
    assert sea_glass['pattern'] == ['GGG', 'GAI', 'GGG']
    assert Counter(sea_glass['key'][symbol]['item'] for row in sea_glass['pattern'] for symbol in row) == Counter({
        'minecraft:glass': 7, 'minecraft:amethyst_shard': 1, 'minecraft:ink_sac': 1})
    assert sea_glass['result']['count'] == 8
    helmet = read(bp / 'recipes/deep_sea_helmet.json')['minecraft:recipe_shaped']
    assert 'minecraft:amethyst_shard' in {v['item'] for v in helmet['key'].values()}

    atlas = read(rp / 'textures/terrain_texture.json')['texture_data']
    item_atlas = read(rp / 'textures/item_texture.json')['texture_data']
    for name, body in definitions.items():
        c = body['components']
        if 'minecraft:wearable' in c:
            icon = c['minecraft:icon']['textures']['default']
            assert (rp / (item_atlas[icon]['textures'] + '.png')).is_file()
            a = read(rp / ('attachables/' + name.split(':')[1] + '.json'))['minecraft:attachable']['description']
            assert a['identifier'] == name
            assert (rp / (a['textures']['default'] + '.png')).is_file()
            assert c['minecraft:max_stack_size'] == 1
        else:
            assert c['minecraft:geometry'] == 'minecraft:geometry.full_block'
            t = c['minecraft:material_instances']['*']['texture']
            assert (rp / (atlas[t]['textures'] + '.png')).is_file()
            loot = read(bp / c['minecraft:loot'])
            assert loot['pools'][0]['entries'][0]['name'] == name
    assert (bp / 'scripts/diving_gear.js').read_bytes() == (ROOT / 'scripts/diving_gear.js').read_bytes()
    assert read(rp / 'manifest.json')['capabilities'] == ['pbr']
    textures = list((rp / 'textures').rglob('*.png'))
    sets = list((rp / 'textures').rglob('*.texture_set.json'))
    assert len(textures) == len(sets) == 18
    for path in sets:
        value = read(path)['minecraft:texture_set']
        assert (path.parent / (value['color'] + '.png')).is_file()
        mer = value['metalness_emissive_roughness']
        assert len(mer) == 3 and all(isinstance(n, int) and 0 <= n <= 255 for n in mer)
    # Keep Prizma and other visual packs in control of their own world effects.
    for directory in ['water', 'lighting', 'atmospherics', 'color_grading', 'fogs', 'materials', 'shaders']:
        assert not (rp / directory).exists()
    assert all(key.startswith('endless_') for key in atlas.keys() | item_atlas.keys())
    print('Diving validation passed: seven craftable items/blocks, assets, script and isolated PBR materials.')


if __name__ == '__main__':
    validate()
