"""Rebuild licensed decoration assets into current Bedrock definitions.

Source scripts are never executed. Generated identifiers are isolated from the
original packs, and existing Endless Waters blocks and diving gear are reused.
"""
from pathlib import Path
import copy, json, re, shutil
from sea_life import save
ROOT = Path(__file__).resolve().parents[1]
FURN = ROOT/'third_party/furnideco'
OCEAN = ROOT/'third_party/ocean_overhaul/src/main/resources/assets/oceanoverhaul'
FARM = ROOT/'third_party/farmers_delight/src/main/resources/assets/farmersdelight'
FARM_GEN = ROOT/'third_party/farmers_delight/src/generated/resources/assets/farmersdelight'


def read(p):
    # JSONC used by the source texture atlas; remove comments outside strings.
    text = re.sub(r'("(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/)',
                  lambda m: m[0] if m[0].startswith('"') else '', p.read_text())
    return json.loads(re.sub(r',\s*([}\]])', r'\1', text))


def ident(name):
    return name if ':' in name else 'endless:'+name


class Decor:
    def __init__(self,bp,rp):
        self.bp,self.rp=bp,rp
        self.atlas=read(rp/'textures/terrain_texture.json')
        self.items=read(rp/'textures/item_texture.json')
        self.sounds=read(rp/'blocks.json')
        self.catalog=[];self.lang=[];self.ids=set()
        for kind in ['blocks','items']:
            for p in (bp/kind).rglob('*.json'):
                d=read(p);body=d.get('minecraft:block',d.get('minecraft:item'))
                self.ids.add(body['description']['identifier'])

    def texture(self,key,source):
        assert source.is_file(), source
        dst=self.rp/f'textures/blocks/decor/{key}.png'
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dst)
        self.atlas['texture_data'][key]={'textures':str(dst.relative_to(self.rp).with_suffix(''))}
        return key

    def geometry(self,name,bones,width=16,height=16):
        geometry={'description':{'identifier':'geometry.endless.'+name,'texture_width':width,'texture_height':height,
                                'visible_bounds_width':4,'visible_bounds_height':4,'visible_bounds_offset':[0,1,0]},'bones':bones}
        save(self.rp/f'models/blocks/decor/{name}.geo.json',{'format_version':'1.12.0','minecraft:geometry':[geometry]})
        return 'geometry.endless.'+name

    def block(self,name,title,geometry,materials,collision=None,perms=None,states=None,extra=None,ingredient='endless:driftwood_plank',source='original',behavior='decorative'):
        full=ident(name);assert full not in self.ids, full;self.ids.add(full)
        c={'minecraft:display_name':'tile.'+full+'.name','minecraft:geometry':geometry,
           'minecraft:material_instances':materials,'minecraft:destructible_by_mining':{'seconds_to_destroy':1.2},
           'minecraft:destructible_by_explosion':{'explosion_resistance':4},'minecraft:light_dampening':0,
           'minecraft:loot':f'loot_tables/decor/{name}.json',
           'minecraft:collision_box':collision if collision is not None else True,
           'minecraft:selection_box':collision if collision else {'origin':[-8,0,-8],'size':[16,16,16]}}
        c.update(extra or {})
        desc={'identifier':full,'menu_category':{'category':'construction'},
              'traits':{'minecraft:placement_direction':{'enabled_states':['minecraft:cardinal_direction'],'y_rotation_offset':180}}}
        if states:desc['states']=states
        p=[{'condition':f"q.block_state('minecraft:cardinal_direction') == '{d}'",'components':{'minecraft:transformation':{'rotation':[0,r,0]}}}
           for d,r in [('north',0),('east',270),('south',180),('west',90)]]+(perms or [])
        save(self.bp/f'blocks/decor/{name}.json',{'format_version':'1.26.0','minecraft:block':{'description':desc,'components':c,'permutations':p}})
        save(self.bp/f'loot_tables/decor/{name}.json',{'pools':[{'rolls':1,'entries':[{'type':'item','name':full}]}]})
        # Stonecutter output selection prevents identical shaped recipes competing.
        save(self.bp/f'recipes/decor/{name}.json',{'format_version':'1.20.10','minecraft:recipe_shapeless':{
            'description':{'identifier':full},'tags':['stonecutter'],'ingredients':[{'item':ingredient}],
            'unlock':[{'item':ingredient}],'result':{'item':full,'count':1}}})
        self.sounds[full]={'sound':'wood'};self.lang.append(f'tile.{full}.name={title}')
        self.catalog.append({'id':full,'name':title,'source':source,'ingredient':ingredient,'behavior':behavior})

    def furniture(self):
        textures=read(FURN/'RP/textures/terrain_texture.json')['texture_data']
        for key,entry in textures.items():
            path=entry['textures']; assert isinstance(path,str), path
            self.texture('fd_'+key.replace('.','_'),FURN/'RP'/ (path+'.png'))
        geos={}
        for path in (FURN/'RP/models').rglob('*.json'):
            for g in read(path).get('minecraft:geometry',[]):
                old=g['description']['identifier'];new='geometry.endless.fd_'+old.removeprefix('geometry.').replace('.','_')
                geos[old]=new;g=copy.deepcopy(g);g['description']['identifier']=new
                save(self.rp/f'models/blocks/decor/{new.split(".")[-1]}.geo.json',{'format_version':'1.12.0','minecraft:geometry':[g]})
        def material(key):
            if key not in textures and key+'.color_0' in textures:key += '.color_0'
            assert key in textures,key
            return {'texture':'fd_'+key.replace('.','_'),'render_method':'alpha_test','ambient_occlusion':False}
        for path in sorted((FURN/'BP/blocks').rglob('*.json')):
            body=read(path)['minecraft:block'];old=body['description']['identifier'].split(':')[1];c=body['components'];a=c['furnideco:attributes']
            name='decor_'+old.replace('.','_');states={};perms=[];interaction={}
            geo=a.get('geometry');collision=a.get('collision',{}).get('block',[-8,0,-8,16,16,16])
            mats=copy.deepcopy(c.get('minecraft:material_instances',{'*':{'texture':old}}))
            mats={k:material(v['texture']) for k,v in mats.items()}
            if 'furnideco:mixed_geometries' in c:
                mixed=c['furnideco:mixed_geometries'];options=mixed['geometries'];geo=mixed['name']+'.'+options[0]['name']
                states['endless:style']=list(range(len(options)));interaction['styles']=len(options)
                collision=options[0].get('collision',{}).get('block',collision)
                for i,v in enumerate(options):
                    perms.append({'condition':f"q.block_state('endless:style') == {i}",'components':{'minecraft:geometry':geos['geometry.'+mixed['name']+'.'+v['name']]}})
            if 'furnideco:connectable' in c and not geo:
                options=c['furnideco:connectable'].get('geometries',[])
                if options:
                    # Expose junction shapes through interaction, avoiding background scans.
                    names=list(dict.fromkeys(o['name'] for o in options));geo=names[0]
                    states['endless:style']=list(range(len(names)));interaction['styles']=len(names)
                    for i,n in enumerate(names):
                        perms.append({'condition':f"q.block_state('endless:style') == {i}",'components':{'minecraft:geometry':geos['geometry.'+n]}})
            if 'furnideco:plantable' in c:
                plant=c['furnideco:plantable'];geo=plant['geometry']+'.empty'
                names=[plant['geometry']+'.'+v['geometry'] for v in plant['plants']]
                states['endless:style']=list(range(len(names)));interaction['styles']=len(names)
                for i,n in enumerate(names):perms.append({'condition':f"q.block_state('endless:style') == {i}",'components':{'minecraft:geometry':geos['geometry.'+n]}})
            if 'furnideco:facing' in c:
                names=[v['name'] for v in c['furnideco:facing']['faces']];geo=names[1]
                names=[geo]+[n for n in names if n!=geo];states['endless:style']=list(range(len(names)));interaction['styles']=len(names)
                for i,n in enumerate(names):perms.append({'condition':f"q.block_state('endless:style') == {i}",'components':{'minecraft:geometry':geos['geometry.'+n]}})
            if 'furnideco:paintable' in c:
                paint=c['furnideco:paintable'];states['endless:color']=list(range(paint['colors']));interaction['colors']=paint['colors']
                if 'base' in paint:mats['*']=material(paint['base'])
                part=paint.get('part','*')
                mats[part]=material(paint['texture']+'.color_0')
                for i in range(paint['colors']):
                    m=copy.deepcopy(mats);m[part]=material(paint['texture']+'.color_'+str(i))
                    perms.append({'condition':f"q.block_state('endless:color') == {i}",'components':{'minecraft:material_instances':m}})
            extra={}
            if 'furnideco:lightable' in c:
                light=c['furnideco:lightable'];states['endless:lit']=[False,True];interaction['light']=True
                extra['minecraft:light_emission']=0
                perms.append({'condition':"q.block_state('endless:lit')",'components':{'minecraft:light_emission':round(light['emission']*15)}})
            if interaction:extra['endless:decor_interact']=interaction
            if isinstance(collision,list):collision={'origin':collision[:3],'size':collision[3:]}
            assert geo and 'geometry.'+geo in geos,(name,geo)
            self.block(name,old.replace('rustic.','').replace('.',' ').replace('_',' ').title(),geos['geometry.'+geo],mats,
                       collision,perms,states,extra,source='FurniDeco',behavior='decorative; interact to change style/light, sneak to change color' if interaction else 'decorative')

    def java_model(self,source,modelname):
        root=OCEAN if source=='ocean' else FARM
        def model(path):
            p=root/'models'/ (path+'.json')
            if not p.exists() and source=='farm':p=FARM_GEN/'models'/(path+'.json')
            return read(p)
        m=model('block/'+modelname); textures={};elements=None
        while True:
            textures={**m.get('textures',{}),**textures}
            if elements is None:elements=m.get('elements')
            parent=m.get('parent','')
            if not parent or parent.startswith('minecraft:') or ':' not in parent:break
            m=model(parent.split(':')[-1])
        if elements is None:
            kind=parent.split('/')[-1]
            cube=lambda a,b:{'from':a,'to':b,'faces':{f:{'texture':'#'+('all' if 'all' in textures else f if f in textures else 'side')} for f in ['north','south','east','west','up','down']}}
            if kind in ['slab','slab_top']:elements=[cube([0,8 if kind=='slab_top' else 0,0],[16,16 if kind=='slab_top' else 8,16])]
            elif kind in ['stairs','inner_stairs','outer_stairs']:elements=[cube([0,0,0],[16,8,16]),cube([0,8,8],[16,16,16])]
            elif 'wall' in kind or 'fence' in kind:elements=[cube([6,0,6],[10,16,10]),cube([0,5,7],[16,8,9]),cube([0,12,7],[16,15,9])]
            elif 'trapdoor' in kind:elements=[cube([0,0,0],[16,3,16])]
            else:elements=[cube([0,0,0],[16,16,16])]
        def tex(key):
            seen=set()
            while key.startswith('#'):
                key=key[1:];assert key not in seen,(modelname,key);seen.add(key)
                key=textures.get(key,textures.get('all',textures.get('side',textures.get('texture',textures.get('particle',next(iter(textures.values()),''))))))
            assert key,(modelname,textures)
            return key
        mats={};bones=[]
        for i,e in enumerate(elements):
            a,z=e['from'],e['to'];size=[z[j]-a[j] for j in range(3)];uv={}
            for face,f in e.get('faces',{}).items():
                texture=tex(f['texture']);key=source+'_'+texture.split(':')[-1].replace('/','_')
                file=root/'textures'/(texture.split(':')[-1]+'.png')
                if texture.startswith('minecraft:'):
                    # Source models only use this fallback for plain timber details.
                    file=OCEAN/'textures/block/driftwood_plank.png'
                if key not in self.atlas['texture_data']:self.texture(key,file)
                mats[key]={'texture':key,'render_method':'alpha_test'}
                coords=f.get('uv',[a[0],16-z[1],z[0],16-a[1]])
                if face in ['up','down'] and 'uv' not in f:coords=[a[0],a[2],z[0],z[2]]
                if face in ['east','west'] and 'uv' not in f:coords=[a[2],16-z[1],z[2],16-a[1]]
                uv[face]={'uv':coords[:2],'uv_size':[coords[2]-coords[0],coords[3]-coords[1]],'material_instance':key}
            cube={'origin':[a[0]-8,a[1],a[2]-8],'size':size,'uv':uv}
            bone={'name':'part_'+str(i),'pivot':[0,0,0],'cubes':[cube]}
            if 'rotation' in e:
                r=e['rotation'];bone['pivot']=[r['origin'][0]-8,r['origin'][1],r['origin'][2]-8];bone['rotation']=[0,0,0];bone['rotation']['xyz'.index(r['axis'])]=r['angle']
            bones.append(bone)
        mats['*']=next(iter(mats.values()))
        return self.geometry(source+'_'+modelname,bones),mats

    def java_blocks(self):
        ocean=['anchor','ships_wheel','rope','tattered_sail','aquarium','abyssal_coral_block','living_abyssal_coral_block','barnacle_block','crushed_coral_block','salt_block','abyssal_pearl_block','glowing_plankton_block','abyssal_vent','giant_clam','prismarine_crystal_block','chiseled_prismarine_tiles','pearl_block']
        for base in ['driftwood_plank','sea_glass','polished_prismarine_bricks','chiseled_prismarine_tiles','pearl_block']:
            ocean += [base+'_slab',base+'_stairs']
            if base!='sea_glass':ocean.append(base+'_wall_inventory')
        ocean += ['driftwood_plank_fence_inventory','driftwood_fence_gate','driftwood_trapdoor_bottom']
        farm=['stove','cooking_pot','cutting_board','skillet','wooden_basket','bamboo_basket','carrot_crate','potato_crate','beetroot_crate','rice_bag','straw_bale','canvas_rug','safety_net','rope_fence_inventory','rope_fence_gate']
        farm += [w+'_cabinet' for w in ['oak','spruce','birch','jungle','acacia','dark_oak','mangrove','cherry','bamboo','crimson','warped']]
        for source,names in [('ocean',ocean),('farm',farm)]:
            for n in names:
                # Model naming changed between upstream releases; prefer the actual generated asset.
                if source=='farm' and n=='basket':n='basket'
                g,m=self.java_model(source,n)
                name=('decor_ocean_' if source=='ocean' else 'decor_galley_')+n.removesuffix('_inventory').removesuffix('_bottom')
                extra={}
                if any(s in n for s in ['glowing','lantern','crystal','vent']):extra['minecraft:light_emission']=10
                self.block(name,n.replace('_inventory','').replace('_bottom','').replace('_',' ').title(),g,m,
                           extra=extra,source='Ocean Overhaul' if source=='ocean' else "Farmer's Delight",
                           ingredient='minecraft:iron_ingot' if n in ['anchor','stove','cooking_pot','skillet'] else 'endless:driftwood_plank')

    def original_props(self):
        # Original cuboid builds using the licensed material palette.
        box=lambda x,y,z,w,h,d,mat='wood':(x,y,z,w,h,d,mat)
        props={
            'rope_coil':[box(-6,0,-5,12,2,2,'rope'),box(-6,0,3,12,2,2,'rope'),box(-6,0,-3,2,2,6,'rope'),box(4,0,-3,2,2,6,'rope'),box(-3,2,-3,6,2,1,'rope'),box(-3,2,2,6,2,1,'rope')],
            'open_crate':[box(-7,0,-7,14,2,14),box(-7,2,-7,2,11,14),box(5,2,-7,2,11,14),box(-5,2,-7,10,11,2),box(-5,2,5,10,11,2)],
            'sealed_crate':[box(-7,0,-7,14,14,14),box(-8,3,-8,16,2,16,'metal'),box(-8,10,-8,16,2,16,'metal')],
            'powder_keg':[box(-5,0,-5,10,14,10),box(-6,2,-6,12,2,12,'metal'),box(-6,10,-6,12,2,12,'metal'),box(-1,14,-1,2,2,2,'rope')],
            'cannonballs':[box(-6,0,-6,5,5,5,'metal'),box(1,0,-6,5,5,5,'metal'),box(-6,0,1,5,5,5,'metal'),box(1,0,1,5,5,5,'metal'),box(-2,5,-2,5,5,5,'metal')],
            'weapon_rack':[box(-7,0,4,2,16,2),box(5,0,4,2,16,2),box(-7,4,4,14,2,2),box(-7,12,4,14,2,2)]+[box(x,5,2,1,10,1,'metal') for x in [-4,0,4]],
            'hammock':[box(-8,6,-6,16,1,12,'cloth'),box(-8,7,-7,16,1,1,'rope'),box(-8,7,6,16,1,1,'rope'),box(-8,7,-6,1,8,12,'rope'),box(7,7,-6,1,8,12,'rope')],
            'boots':[box(-5,0,-4,4,3,7,'metal'),box(1,0,-4,4,3,7,'metal'),box(-5,3,0,4,5,3,'metal'),box(1,3,0,4,5,3,'metal')],
            'hanging_coat':[box(-4,3,5,8,11,2,'cloth'),box(-7,8,5,3,6,2,'cloth'),box(4,8,5,3,6,2,'cloth'),box(-1,14,5,2,2,2,'metal')],
            'mug':[box(-3,0,-3,6,1,6,'metal'),box(-3,1,-3,1,5,6,'metal'),box(2,1,-3,1,5,6,'metal'),box(-2,1,-3,4,5,1,'metal'),box(-2,1,2,4,5,1,'metal'),box(3,1,-1,2,1,2,'metal'),box(4,2,-1,1,3,2,'metal'),box(3,5,-1,2,1,2,'metal')],
            'inkwell':[box(-4,0,-3,6,4,6,'metal'),box(-2,4,-1,2,2,2,'metal'),box(3,0,0,1,11,1,'cloth')],
            'sextant':[box(-5,0,-4,10,1,8),box(-5,1,0,10,1,1,'metal'),box(-5,2,0,1,8,1,'metal'),box(-4,10,0,8,1,1,'metal'),box(3,2,0,1,8,1,'metal'),box(-1,1,0,1,9,1,'metal')],
            'compass_stand':[box(-4,0,-4,8,2,8),box(-1,2,-1,2,5,2),box(-5,7,-5,10,2,10,'metal'),box(-1,9,-4,2,1,8,'cloth')],
            'canvas_bundle':[box(-6,0,-5,12,6,10,'cloth'),box(-7,2,-6,14,2,12,'rope')],
            'coin_pile':[box(-5,0,-4,5,1,5,'gold'),box(0,0,1,6,1,5,'gold'),box(-1,1,-2,4,2,4,'gold'),box(3,0,-5,3,1,3,'gold')],
            'treasure_chest':[box(-7,0,-5,14,8,10),box(-7,8,-5,14,3,10,'gold'),box(-8,0,-6,2,11,12,'metal'),box(6,0,-6,2,11,12,'metal'),box(-1,5,-6,2,4,1,'gold')],
            'porthole':[box(-7,1,5,14,2,2,'metal'),box(-7,13,5,14,2,2,'metal'),box(-7,3,5,2,10,2,'metal'),box(5,3,5,2,10,2,'metal')],
            'pipe':[box(-2,0,-2,4,16,4,'metal'),box(-4,1,-4,8,2,8,'metal'),box(-4,13,-4,8,2,8,'metal')],
            'valve':[box(-2,0,3,4,16,4,'metal'),box(-6,4,0,12,2,2,'gold'),box(-6,10,0,12,2,2,'gold'),box(-6,6,0,2,4,2,'gold'),box(4,6,0,2,4,2,'gold')],
            'pressure_gauge':[box(-6,3,4,12,10,3,'metal'),box(-4,5,3,8,6,1,'cloth'),box(0,6,2,1,4,1,'metal')],
            'oxygen_cylinder':[box(-3,0,-3,6,13,6,'metal'),box(-2,13,-2,4,2,4,'gold'),box(-4,15,-1,8,1,2,'metal')],
            'equipment_rack':[box(-7,0,4,2,16,2,'metal'),box(5,0,4,2,16,2,'metal'),box(-7,14,4,14,2,2,'metal')]+[box(x,4,2,3,8,3,'metal') for x in [-5,1]],
            'control_console':[box(-7,0,-5,14,8,12,'metal'),box(-7,8,1,14,6,6),box(-5,10,0,4,3,1,'cloth'),box(1,10,0,4,3,1,'cloth'),box(-5,8,-4,2,1,2,'gold'),box(1,8,-4,2,1,2,'gold')],
            'broken_pottery':[box(-5,0,-5,10,2,10),box(-5,2,-5,2,5,10),box(3,2,0,2,3,5),box(-3,2,3,6,2,2)],
        }
        material_files={'wood':OCEAN/'textures/block/driftwood_plank.png','metal':OCEAN/'textures/block/anchor.png','cloth':OCEAN/'textures/block/tattered_sail.png','rope':OCEAN/'textures/block/rope.png','gold':OCEAN/'textures/block/pearl_block.png'}
        mats={key:{'texture':self.texture('original_'+key,p),'render_method':'opaque'} for key,p in material_files.items()}
        mats['*']=mats['wood']
        for name,parts in props.items():
            cubes=[]
            for x,y,z,w,h,d,mat in parts:
                cubes.append({'origin':[x,y,z],'size':[w,h,d],'uv':{face:{'uv':[0,0],'uv_size':[8,8],'material_instance':mat} for face in ['north','south','east','west','up','down']}})
            g=self.geometry('prop_'+name,[{'name':'root','pivot':[0,0,0],'cubes':cubes}])
            self.block('decor_'+name,name.replace('_',' ').title(),g,mats,collision=False,source='Endless Waters original',ingredient='minecraft:iron_ingot' if name in ['pipe','valve','porthole','pressure_gauge','oxygen_cylinder','equipment_rack','control_console'] else 'endless:driftwood_plank')

    def food_items(self):
        # Vanilla-accessible recipes keep ocean survival independent of new crops.
        foods={
            'kelp_roll':('ocean',4,['minecraft:dried_kelp','minecraft:cooked_salmon']),
            'salted_cod':('ocean',5,['minecraft:cooked_cod','minecraft:dried_kelp']),
            'seafood_stew':('ocean',8,['minecraft:bowl','minecraft:cooked_cod','minecraft:cooked_salmon','minecraft:dried_kelp']),
            'fish_stew':('farm',8,['minecraft:bowl','minecraft:cooked_cod','minecraft:carrot','minecraft:potato']),
            'baked_cod_stew':('farm',9,['minecraft:bowl','minecraft:cooked_cod','minecraft:baked_potato']),
            'grilled_salmon':('farm',7,['minecraft:cooked_salmon','minecraft:carrot']),
            'fruit_salad':('farm',5,['minecraft:bowl','minecraft:apple','minecraft:melon_slice']),
            'mixed_salad':('farm',5,['minecraft:bowl','minecraft:carrot','minecraft:beetroot']),
            'vegetable_soup':('farm',6,['minecraft:bowl','minecraft:carrot','minecraft:baked_potato']),
            'apple_cider':('farm',4,['minecraft:glass_bottle','minecraft:apple','minecraft:sugar']),
            'hot_cocoa':('farm',4,['minecraft:glass_bottle','minecraft:cocoa_beans','minecraft:sugar']),
            'melon_juice':('farm',3,['minecraft:glass_bottle','minecraft:melon_slice','minecraft:sugar']),
            'sweet_berry_cookie':('farm',3,['minecraft:cookie','minecraft:sweet_berries']),
            'honey_cookie':('farm',3,['minecraft:cookie','minecraft:honey_bottle']),
        }
        for name,(source,nutrition,ingredients) in foods.items():
            full='endless:food_'+name;assert full not in self.ids;self.ids.add(full)
            root=OCEAN if source=='ocean' else FARM;src=root/f'textures/item/{name}.png'
            if not src.exists():src=root/f'textures/item/food/{name}.png'
            assert src.exists(),src
            key='food_'+name;dst=self.rp/f'textures/items/decor/{name}.png';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
            self.items['texture_data'][key]={'textures':str(dst.relative_to(self.rp).with_suffix(''))}
            save(self.bp/f'items/decor/{name}.json',{'format_version':'1.26.30','minecraft:item':{
                'description':{'identifier':full,'menu_category':{'category':'items'}},'components':{
                    'minecraft:display_name':{'value':name.replace('_',' ').title()},'minecraft:icon':{'textures':{'default':key}},
                    'minecraft:max_stack_size':16,'minecraft:use_animation':'eat','minecraft:use_modifiers':{'use_duration':1.6,'movement_modifier':0.35},
                    'minecraft:food':{'nutrition':nutrition,'saturation_modifier':0.6,'can_always_eat':False}}}})
            save(self.bp/f'recipes/decor/food_{name}.json',{'format_version':'1.20.10','minecraft:recipe_shapeless':{
                'description':{'identifier':full},'tags':['crafting_table'],'ingredients':[{'item':i} for i in ingredients],
                'unlock':[{'item':ingredients[0]}],'result':{'item':full,'count':1}}})
            self.catalog.append({'id':full,'name':name.replace('_',' ').title(),'source':source,'behavior':'edible','ingredients':ingredients})

    def harpoon(self):
        name='harpoon';key='endless_harpoon'
        dst=self.rp/'textures/items/decor/harpoon.png';dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(OCEAN/'textures/item/harpoon.png',dst)
        self.items['texture_data'][key]={'textures':'textures/items/decor/harpoon'}
        save(self.bp/'items/decor/harpoon.json',{'format_version':'1.26.30','minecraft:item':{
            'description':{'identifier':'endless:harpoon','menu_category':{'category':'equipment'}},'components':{
                'minecraft:display_name':{'value':'Harpoon'},'minecraft:icon':{'textures':{'default':key}},
                'minecraft:max_stack_size':16,'minecraft:hand_equipped':True,'minecraft:damage':5,
                'minecraft:use_animation':'spear','minecraft:use_modifiers':{'use_duration':1,'movement_modifier':0.7},
                'minecraft:throwable':{'do_swing_animation':True,'max_launch_power':2.5,'launch_power_scale':1.5},
                'minecraft:projectile':{'projectile_entity':'endless:harpoon_projectile'},
                'minecraft:cooldown':{'category':'endless_harpoon','duration':0.7}}}})
        save(self.bp/'recipes/decor/harpoon.json',{'format_version':'1.20.10','minecraft:recipe_shaped':{
            'description':{'identifier':'endless:harpoon'},'tags':['crafting_table'],'pattern':['  I',' SI','S  '],
            'key':{'I':{'item':'minecraft:iron_ingot'},'S':{'item':'minecraft:stick'}},
            'unlock':[{'item':'minecraft:iron_ingot'}],'result':{'item':'endless:harpoon','count':1}}})
        save(self.bp/'entities/harpoon.json',{'format_version':'1.26.0','minecraft:entity':{
            'description':{'identifier':'endless:harpoon_projectile','is_spawnable':False,'is_summonable':True},
            'components':{'minecraft:type_family':{'family':['projectile']},'minecraft:collision_box':{'width':0.15,'height':0.15},
                          'minecraft:physics':{},'minecraft:projectile':{'power':2.5,'gravity':0.025,'liquid_inertia':0.98,
                          'on_hit':{'impact_damage':{'damage':7,'knockback':False,'destroy_on_hit':False},'stick_in_ground':{}},
                          'uncertainty_base':0,'uncertainty_multiplier':0}}}})
        g=self.geometry('harpoon_projectile',[{'name':'root','pivot':[0,0,0],'cubes':[
            {'origin':[-0.5,-0.5,-12],'size':[1,1,22],'uv':[0,0]},
            {'origin':[-2,-0.5,8],'size':[4,1,4],'uv':[0,0]}]}])
        save(self.rp/'entity/harpoon.entity.json',{'format_version':'1.10.0','minecraft:client_entity':{'description':{
            'identifier':'endless:harpoon_projectile','materials':{'default':'entity_alphatest'},
            'textures':{'default':'textures/items/decor/harpoon'},'geometry':{'default':g},
            'render_controllers':['controller.render.default']}}})
        self.catalog.append({'id':'endless:harpoon','name':'Harpoon','source':'Ocean Overhaul texture; rebuilt Bedrock behavior',
                             'behavior':'throwable, recoverable on impact; no automatic loyalty return'})

    def finish(self):
        # Namespace atlas keys too: resource-pack priority must not replace another pack's art.
        keys=set(self.atlas['texture_data']) | set(self.items['texture_data'])
        rename={k:'endless_'+k for k in keys if not k.startswith('endless_')}
        for atlas in [self.atlas,self.items]:
            atlas['texture_data']={rename.get(k,k):v for k,v in atlas['texture_data'].items()}
        def remap(value):
            if isinstance(value,dict):return {k:remap(v) for k,v in value.items()}
            if isinstance(value,list):return [remap(v) for v in value]
            return rename.get(value,value) if isinstance(value,str) else value
        for folder in ['blocks','items']:
            for path in (self.bp/folder/'decor').glob('*.json'):save(path,remap(read(path)))
        save(self.rp/'textures/terrain_texture.json',self.atlas);save(self.rp/'textures/item_texture.json',self.items);save(self.rp/'blocks.json',self.sounds)
        with (self.rp/'texts/en_US.lang').open('a') as f:f.write('\n'.join(self.lang)+'\n')
        save(ROOT/'experiments/decor/catalog.json',{'entries':self.catalog,'count':len(self.catalog)})
        for dest in [self.bp,self.rp]:
            for name in ['furnideco','farmers_delight']:
                shutil.copy2(ROOT/'third_party'/name/'LICENSE',dest/f'{name.upper()}_LICENSE.txt')
            (dest/'DECOR_ATTRIBUTION.txt').write_text('FurniDeco by Arexon (Apache-2.0); Farmer\'s Delight by vectorwing (MIT); Ocean Overhaul by tinyclaw / VoX (MIT).\nModels/textures adapted for Endless Waters. Definitions, interactions and recipes rebuilt; source functionality is not reproduced in full.\n')
        for script in ['decor.js','decor_logic.js','harpoon.js']:
            shutil.copy2(ROOT/'scripts'/script,self.bp/'scripts'/script)


def build(bp,rp):
    d=Decor(bp,rp);d.furniture();d.java_blocks();d.original_props();d.food_items();d.harpoon();d.finish()
