"""Check decoration references, recipe isolation and source integrity."""
import hashlib
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
bp=ROOT/'behavior_packs/endless_waters'
rp=ROOT/'resource_packs/endless_waters'
read=lambda p:json.loads(p.read_text())
ids=[]
for kind,key in [('blocks','minecraft:block'),('items','minecraft:item')]:
    ids += [read(p)[key]['description']['identifier'] for p in (bp/kind).rglob('*.json')]
assert len(ids)==len(set(ids)), 'Duplicate block/item identifiers'
catalog=read(ROOT/'experiments/decor/catalog.json')['entries']
assert len(catalog)==len({e['id'] for e in catalog})==174
assert {e['id'] for e in catalog} <= set(ids)
geometries={g['description']['identifier']:g for p in (rp/'models').rglob('*.json') for g in read(p).get('minecraft:geometry',[])}
atlas=read(rp/'textures/terrain_texture.json')['texture_data']
for p in (bp/'blocks/decor').glob('*.json'):
    block=read(p)['minecraft:block']
    for components in [block['components']]+[v['components'] for v in block.get('permutations',[])]:
        geometry=components.get('minecraft:geometry')
        if geometry:
            identifier=geometry if isinstance(geometry,str) else geometry['identifier']
            assert identifier in geometries,(p,identifier)
        for material in components.get('minecraft:material_instances',{}).values():
            assert material['texture'] in atlas,(p,material)
for kind in ['terrain','item']:
    for key,value in read(rp/f'textures/{kind}_texture.json')['texture_data'].items():
        assert key.startswith('endless_'),key
        textures=value['textures']
        for texture in textures if isinstance(textures,list) else [textures]:
            if isinstance(texture,dict):texture=texture['path']
            assert (rp/(texture+'.png')).exists(),texture
recipes=[];shapeless={}
for p in (bp/'recipes').rglob('*.json'):
    value=read(p);key=next(k for k in value if k.startswith('minecraft:recipe_'));recipe=value[key]
    recipes.append(recipe['description']['identifier'])
    result=recipe['result'];result=result[0] if isinstance(result,list) else result
    if result['item'].startswith('endless:'):assert result['item'] in ids,(p,result)
    ingredients=recipe.get('ingredients',list(recipe.get('key',{}).values()))
    for ingredient in ingredients:
        item=ingredient.get('item','')
        if item.startswith('endless:'):assert item in ids,(p,item)
    if key=='minecraft:recipe_shapeless' and 'stonecutter' not in recipe['tags']:
        signature=tuple(sorted(json.dumps(i,sort_keys=True) for i in ingredients))
        assert signature not in shapeless,(p,shapeless.get(signature))
        shapeless[signature]=str(p)
assert len(recipes)==len(set(recipes)), 'Duplicate recipe identifiers'
for receipt in (ROOT/'third_party').glob('*/decor_source.json'):
    for name,digest in read(receipt)['files'].items():
        assert hashlib.sha256((receipt.parent/name).read_bytes()).hexdigest()==digest,(receipt,name)
for pack in [bp,rp]:
    for filename in ['FURNIDECO_LICENSE.txt','FARMERS_DELIGHT_LICENSE.txt','DECOR_ATTRIBUTION.txt']:
        assert (pack/filename).stat().st_size>100
print(f'Decor validation passed: {len(catalog)} entries, unique identifiers/recipes, model/texture references and source hashes.')
