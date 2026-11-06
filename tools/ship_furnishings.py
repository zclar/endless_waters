"""Dense room-specific furnishings for the Dreadwake, with safe circulation."""

def furnish(s):
    from pirate_ship import b, AIR, HULL, slab, stair
    s.loot=[]
    def prop(name,x,y,z,d='north',style=0,color=0):
        states={'minecraft:cardinal_direction':d}
        if style:states['endless:style']=style
        if color:states['endless:color']=color
        p=(x,y,z)
        if s.blocks.get(p,AIR)==AIR:
            s.put(x,y,z,b('endless:decor_'+name,**states));return True
        return False
    def furniture(name,x,y,z,**kw):return prop('rustic_'+name,x,y,z,**kw)
    def chest(x,y,z,role='cargo'):
        if s.blocks.get((x,y,z),AIR)!=AIR:return
        s.put(x,y,z,b('chest',facing_direction=2))
        s.loot.append({'position':[x,y,z],'role':role,'table':f'loot_tables/ships/{s.variant}_{role}.json'})
    def table(x,y,z,length=3):
        for zz in range(z,z+length):
            furniture('spruce_table',x,y,zz)
            furniture('spruce_chair',x-2,y,zz,d='east')
            furniture('spruce_chair',x+2,y,zz,d='west')
            furniture('bottle' if zz%2 else 'book',x,y+1,zz,style=1 if zz%2 else 0)
    # Bulkheads divide the lower hold into cabins, stores and secure treasure.
    for z in [32,57,78,94]:
        for x in range(18,31):
            if 23<=x<=25:continue
            for y in range(5,8):
                if s.blocks.get((x,y,z),AIR)==AIR:s.put(x,y,z,HULL)
    # Forepeak bosun store: rolled canvas, stacked ropes and spare equipment.
    for x,z in [(21,23),(26,24),(20,27),(28,28)]:
        prop('canvas_bundle',x,5,z);prop('rope_coil',x,6,z)
    for x,z in [(20,30),(28,30)]:chest(x,5,z,'supplies')
    # Six crew bays with real beds, personal lockers, books, boots and hammocks.
    for side in [-1,1]:
        x=24+side*6
        for z in [35,42,49]:
            for dz,head in [(0,False),(1,True)]:
                s.put(x,5,z+dz,b('bed',direction=0,head_piece_bit=head,occupied_bit=False))
            furniture('spruce_cabinet',x+side,5,z+3,d='east' if side<0 else 'west')
            prop('boots',x-side,5,z+1);prop('hanging_coat',x+side,6,z+2)
            furniture('book',x+side,6,z+3,style=1)
            prop('hammock',x,7,z+1)
            chest(x-side,5,z+3,'crew')
    # Cargo stacks with mixed shapes; keep the center aisle and stairs open.
    for x,z in [(18,62),(29,63),(17,69),(30,70),(18,74),(29,75),(18,81),(29,82)]:
        prop('sealed_crate',x,5,z);prop('canvas_bundle',x,6,z)
        prop('open_crate',x+1,5,z+1);prop('rope_coil',x+1,6,z+1)
        chest(x,5,z+2,'cargo')
        prop('galley_rice_bag',x-1,5,z)
    # Brig, small desk, supplies and salvager's cache below the aft stairs.
    for x in range(18,23):
        if s.blocks.get((x,5,85),AIR)==AIR:
            for y in [5,6,7]:s.put(x,y,85,b('iron_bars'))
    furniture('spruce_stool',20,5,88);prop('mug',20,6,88)
    prop('canvas_bundle',19,5,90);chest(29,5,92,'salvage')
    # Vault: reinforced forward wall, iron door and an accessible floor lever.
    for x in range(19,30):
        for y in [5,6,7]:
            s.put(x,y,94,b('polished_blackstone_bricks'))
    for y,upper in [(5,False),(6,True)]:
        s.put(24,y,94,b('iron_door',direction=1,upper_block_bit=upper,door_hinge_bit=False,open_bit=False))
    s.put(24,5,93,b('lever',lever_direction='up_north_south',open_bit=False))
    s.put(24,5,95,b('lever',lever_direction='up_north_south',open_bit=False))
    for x,z in [(20,97),(28,97),(22,100),(26,100)]:
        chest(x,5,z,'vault');prop('coin_pile',x,6,z)
    for x,z in [(20,99),(28,99)]:prop('treasure_chest',x,5,z);prop('coin_pile',x,6,z)
    # Galley: full work counters, stoves, pots, pantry, tableware and food stores.
    for x in range(20,29):
        prop('galley_spruce_cabinet',x,10,25)
        prop('galley_cooking_pot' if x%3==0 else 'galley_cutting_board' if x%3==1 else 'galley_skillet',x,11,25)
    for x in [20,28]:prop('galley_stove',x,10,23)
    table(20,10,29,3);table(28,10,29,3)
    for x,z in [(18,33),(30,33)]:
        chest(x,10,z,'pantry');prop('galley_wooden_basket',x,11,z)
        prop('galley_carrot_crate',x,10,z+2);prop('galley_potato_crate',x,11,z+2)
    # Gun deck: ammunition, gunner's tools, racks, mess and infirmary stations.
    for z in [37,45,53,69,77]:
        for x in [16,32]:
            prop('cannonballs',x,10,z);prop('powder_keg',x,10,z+2)
            prop('rope_coil',x,11,z+2)
    for x,z in [(19,41),(29,49),(19,73)]:chest(x,10,z,'armory')
    for x,z in [(18,83),(30,83),(18,95),(30,95)]:prop('weapon_rack',x,10,z)
    table(19,10,87,3);table(29,10,87,3)
    for x in [19,29]:
        furniture('spruce_cabinet',x,10,99);furniture('bottle',x,11,99,style=2)
        chest(x+1,10,97,'supplies');prop('equipment_rack',x,10,101)
    # Captain's suite: entrance, library, writing room, map table and private berth.
    for z in [87,89,93,95,99,101]:
        furniture('dark_oak_cabinet',15,15,z,d='east')
        furniture('book',15,16,z,style=2)
    for z in [87,90,94,98,101]:
        furniture('curtain',34,17,z,d='west',color=14)
    for z in [94,95,96]:
        for x in [21,22,23,24,25,26,27]:furniture('dark_oak_table',x,15,z)
    for x,z,name in [(22,94,'rustic_scroll'),(24,94,'sextant'),(26,94,'compass_stand'),(21,96,'inkwell'),(27,96,'rustic_book'),(25,95,'rustic_bottle')]:prop(name,x,16,z)
    furniture('dark_oak_chair',24,15,98,d='north')
    furniture('dark_oak_chair',20,15,95,d='east')
    furniture('dark_oak_chair',28,15,95,d='west')
    for x,z in [(31,98),(31,100)]:
        s.put(x,15,z,b('bed',direction=0,head_piece_bit=False,occupied_bit=False))
        s.put(x,15,z+1,b('bed',direction=0,head_piece_bit=True,occupied_bit=False))
    for x in [29,33]:
        s.box(x,15,97,x,18,102,b('dark_oak_fence'))
    s.box(29,19,97,33,19,102,slab('dark_oak'))
    furniture('dark_oak_coffee_table',30,15,89);furniture('bottle',30,16,89,style=2)
    furniture('dark_oak_sofa',31,15,87,color=14)
    furniture('grandfather_clock',17,15,87)
    chest(17,15,101,'captain');chest(32,15,93,'navigation')
    prop('coin_pile',18,15,100);prop('boots',30,15,96)
    for x,z in [(19,91),(29,91)]:
        furniture('chandelier',x,19,z)
        p=(x,19,z)
        if s.blocks.get(p,AIR).name=='endless:decor_rustic_chandelier':s.put(*p,b('endless:decor_rustic_chandelier',**{'minecraft:cardinal_direction':'north','endless:lit':True}))
    # Busy working main deck: gear, repair materials, navigational fittings.
    for x,z in [(14,44),(34,47),(15,72),(33,76),(18,79),(30,40)]:
        prop('rope_coil',x,15,z);prop('open_crate',x,15,z+2)
        prop('canvas_bundle',x,16,z+2)
    prop('ocean_ships_wheel',24,22,92);prop('compass_stand',26,22,94)
    prop('ocean_anchor',18,19,22);prop('ocean_anchor',30,19,22)
    s.zones={'crew_quarters_and_bosun_store':[5,8],'cargo_brig_and_vault':[5,8],
             'galley_gun_deck_armory_and_infirmary':[10,13],'captains_suite_library_and_chart_room':[15,20],'quarterdeck':[22,25]}
    # Weathering affects props without compromising stairs or the sealed hull.
    if s.variant!='new':
        import random
        rng=random.Random(730 if s.variant=='tattered' else 731)
        for p,block in list(s.blocks.items()):
            if not block.name.startswith('endless:decor_'):continue
            if rng.random() < (.05 if s.variant=='tattered' else .30):
                s.put(*p,AIR)
            elif s.variant=='abandoned' and 'endless:lit' in dict(block.states):
                states=dict(block.states);states['endless:lit']=False;s.put(*p,b(block.name,**states))
        if s.variant=='abandoned':
            for y in [5,6]:s.put(24,y,94,AIR)
            for x,z in [(20,97),(28,99),(18,63),(29,82)]:prop('broken_pottery',x,5,z+1)
    # Contents remain lazy native loot tables, never fixed inventories.
    s.loot=[l for l in s.loot if s.blocks.get(tuple(l['position']),AIR).name=='chest']
