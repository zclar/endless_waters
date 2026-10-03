"""Craftable diving equipment and decorative blocks from Ocean Overhaul (MIT)."""
from pathlib import Path
import shutil
from sea_life import save, SOURCE

ROOT = Path(__file__).resolve().parents[1]
BLOCKS = {
    'driftwood_plank': ('Driftwood Planks', 'wood', 2),
    'sea_glass': ('Sea Glass', 'glass', .3),
    'polished_prismarine_bricks': ('Polished Prismarine Bricks', 'stone', 1.5),
    'pearl_lantern': ('Pearl Lantern', 'glass', .3),
}
GEAR = {
    'deep_sea_helmet': ('Deep-Sea Helmet', 'head', 'helmet', 143, 1),
    'oxygen_tank': ('Oxygen Tank', 'chest', 'chestplate', 208, 3),
    'flippers': ('Flippers', 'feet', 'boots', 169, 1),
}


def build(bp, rp):
    terrain = {}; items = {}; sounds = {'format_version': [1,1,0]}
    translations = []
    def texture(name, kind):
        dst = rp / f'textures/{"blocks" if kind=="block" else "items"}/endless/{name}.png'
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(SOURCE / f'src/main/resources/assets/oceanoverhaul/textures/{kind}/{name}.png',dst)
        return str(dst.relative_to(rp).with_suffix(''))

    def recipe(name, pattern, key, count=1):
        save(bp / f'recipes/{name}.json', {'format_version':'1.20.10','minecraft:recipe_shaped':{
            'description':{'identifier':'endless:'+name},'tags':['crafting_table'],
            'pattern':pattern,'key':{k:{'item':v} for k,v in key.items()},
            'unlock':[{'item':next(iter(key.values()))}],
            'result':{'item':'endless:'+name,'count':count}}})

    for name,(title,sound,seconds) in BLOCKS.items():
        key='endless_'+name
        terrain[key]={'textures':texture(name,'block')}
        components={
            'minecraft:display_name':f'tile.endless:{name}.name',
            'minecraft:geometry':'minecraft:geometry.full_block',
            'minecraft:material_instances':{'*':{'texture':key,'render_method':'blend' if name=='sea_glass' else 'opaque'}},
            'minecraft:destructible_by_mining':{'seconds_to_destroy':seconds},
            'minecraft:destructible_by_explosion':{'explosion_resistance':3 if name=='driftwood_plank' else 6 if name=='polished_prismarine_bricks' else .3},
            'minecraft:loot':f'loot_tables/blocks/{name}.json',
        }
        if name=='sea_glass':components['minecraft:light_dampening']=0
        if name=='pearl_lantern':components['minecraft:light_emission']=15
        if name=='driftwood_plank':components['minecraft:flammable']={'catch_chance_modifier':5,'destroy_chance_modifier':20}
        save(bp/f'blocks/{name}.json',{'format_version':'1.26.0','minecraft:block':{
            'description':{'identifier':'endless:'+name,'menu_category':{'category':'construction'}},'components':components}})
        save(bp/f'loot_tables/blocks/{name}.json',{'pools':[{'rolls':1,'entries':[{'type':'item','name':'endless:'+name}]}]})
        sounds['endless:'+name]={'sound':sound}
        translations.append(f'tile.endless:{name}.name={title}')
    save(rp/'textures/terrain_texture.json',{'resource_pack_name':'endless_waters','texture_name':'atlas.terrain','padding':8,'num_mip_levels':4,'texture_data':terrain})
    save(rp/'blocks.json',sounds)

    for name,(title,slot,geometry,durability,protection) in GEAR.items():
        icon='endless_'+name;items[icon]={'textures':texture(name,'item')}
        save(bp/f'items/{name}.json',{'format_version':'1.26.30','minecraft:item':{
            'description':{'identifier':'endless:'+name,'menu_category':{'category':'equipment'}},
            'components':{
                'minecraft:display_name':{'value':f'item.endless:{name}.name'},
                'minecraft:icon':{'textures':{'default':icon}},
                'minecraft:max_stack_size':1,
                'minecraft:wearable':{'slot':'slot.armor.'+slot,'protection':protection},
                'minecraft:durability':{'max_durability':durability},
                'minecraft:repairable':{'repair_items':[{'items':['minecraft:iron_ingot'],'repair_amount':50}]},
            }}})
        save(rp/f'attachables/{name}.json',{'format_version':'1.10.0','minecraft:attachable':{'description':{
            'identifier':'endless:'+name,
            'materials':{'default':'armor','enchanted':'armor_enchanted'},
            'textures':{'default':'textures/models/armor/endless_diving_1','enchanted':'textures/misc/enchanted_actor_glint'},
            'geometry':{'default':'geometry.humanoid.armor.'+geometry},
            'scripts':{'parent_setup':f'variable.{"boot" if slot=="feet" else slot if slot=="chest" else geometry}_layer_visible = 0.0;'},
            'render_controllers':['controller.render.armor']}}})
        translations.append(f'item.endless:{name}.name={title}')
    save(rp/'textures/item_texture.json',{'resource_pack_name':'endless_waters','texture_name':'atlas.items','texture_data':items})
    dst=rp/'textures/models/armor/endless_diving_1.png';dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(SOURCE/'src/main/resources/assets/oceanoverhaul/textures/models/armor/diving_layer_1.png',dst)
    with (rp/'texts/en_US.lang').open('a') as f:f.write('\n'.join(translations)+'\n')
    recipe('driftwood_plank',['PP','PK'],{'P':'minecraft:oak_planks','K':'minecraft:dried_kelp'},3)
    recipe('sea_glass',['GGG','GPG','GGG'],{'G':'minecraft:glass','P':'minecraft:prismarine_shard'},8)
    recipe('polished_prismarine_bricks',['PP','PP'],{'P':'minecraft:prismarine_bricks'},4)
    recipe('pearl_lantern',[' P ','PLP',' P '],{'P':'minecraft:prismarine_crystals','L':'minecraft:sea_lantern'})
    recipe('deep_sea_helmet',['III','G G',' P '],{'I':'minecraft:iron_ingot','G':'endless:sea_glass','P':'minecraft:prismarine_shard'})
    recipe('oxygen_tank',['I I','IGI','III'],{'I':'minecraft:iron_ingot','G':'endless:sea_glass'})
    recipe('flippers',['K K','I I','K K'],{'K':'minecraft:dried_kelp','I':'minecraft:iron_ingot'})
    (bp/'scripts').mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'scripts/diving_gear.js',bp/'scripts/diving_gear.js')
