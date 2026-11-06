// Runs only on the isolated local BDS world; never packaged with the download.
import {world, system, BlockPermutation, SignSide, ItemStack} from '@minecraft/server';
import {SHIPS, BUILD_ID, DECOR, ITEMS} from './data.js';
import {interactDecor} from './decor_logic.js';

const pause = ticks => new Promise(resolve => system.runTimeout(resolve, ticks));
const check = (condition, message) => {if (!condition) throw Error(message);};
const position = (origin, p) => ({x:origin[0]+p[0], y:origin[1]+p[1], z:origin[2]+p[2]});
let dimension;

function fill(a,b,name) {
    dimension.runCommand(`fill ${a.join(' ')} ${b.join(' ')} ${name}`);
}
function sign(p,text) {
    const block = dimension.getBlock(p);
    block.setPermutation(BlockPermutation.resolve('minecraft:standing_sign',{ground_sign_direction:8}));
    const component = block.getComponent('minecraft:sign');
    check(component, 'Sign component missing');
    component.setText(text, SignSide.Front);
    component.setText(text, SignSide.Back);
    component.setWaxed(true);
}
async function loadAreas() {
    for(const [variant,data] of Object.entries(SHIPS)) {
        const x=data.origin[0];
        await world.tickingAreaManager.createTickingArea('dreadwake:'+variant, {
            dimension, from:{x:x-8,y:0,z:-16}, to:{x:x+55,y:0,z:127},
        });
    }
    await world.tickingAreaManager.createTickingArea('dreadwake:plaza', {
        dimension, from:{x:-16,y:0,z:-32}, to:{x:255,y:0,z:-1},
    });
    await pause(10);
}
async function dock(data,variant) {
    const x=data.origin[0];
    // An eight-block-deep display tank on the normal flat grass surface.
    for(let z=-2;z<120;z+=16) {
        fill([x-3,-60,z],[x+51,-53,Math.min(z+15,119)],'stone_bricks');
        fill([x-1,-60,z+Math.max(0,-z)],[x+49,-53,Math.min(z+15,117)],'water');
        await pause(1);
    }
    // Upper rim and continuous public boardwalk.
    fill([x-3,-52,-2],[x+51,-52,-1],'spruce_planks');
    fill([x-3,-52,118],[x+51,-52,119],'spruce_planks');
    fill([x-3,-52,0],[x-2,-52,117],'spruce_planks');
    fill([x+50,-52,0],[x+51,-52,117],'spruce_planks');
    for(let z=8;z<=112;z+=16)for(const xx of [x-3,x+51]) {
        dimension.getBlock({x:xx,y:-51,z}).setType('minecraft:oak_fence');
        dimension.getBlock({x:xx,y:-50,z}).setType('minecraft:lantern');
    }
    for(let part=0;part<2;part++) {
        world.structureManager.place(`dreadwake:${variant}_${part}`,dimension,
            {x,y:-60,z:58*part},{includeEntities:false});
    }
    // Both halves must seal the hull before the next fluid simulation tick.
    await pause(20);
    sign({x:x+24,y:-51,z:-3},`DREADWAKE\n${variant.toUpperCase()}\n${data.crew.length} pillagers\nFly aboard`);
    // A short side boarding ramp connects the tank rim to the existing ladder.
    fill([x+41,-52,56],[x+50,-52,58],'spruce_planks');
}
function spawnCrew(data,variant) {
    data.crew.forEach((p,index)=>{
        const location=position(data.origin,p);
        location.x+=.5;location.z+=.5;
        const mob=dimension.spawnEntity('minecraft:pillager',location);
        mob.addTag('dreadwake_'+variant);
        mob.addTag('dreadwake_'+variant+'_'+index);
        mob.nameTag=index===0?'Captain of the Dreadwake':`Dreadwake ${variant} crew ${index}`;
        if(index===0)mob.triggerEvent('minecraft:spawn_as_illager_captain');
        dimension.runCommand(`replaceitem entity @e[type=pillager,tag=dreadwake_${variant}_${index},c=1] slot.weapon.mainhand 0 crossbow`);
    });
}
async function inspect(phase) {
    const variants={};
    for(const [variant,data] of Object.entries(SHIPS)) {
        const mismatch=[];
        let checked=0,interiorAir=0,emptyBarrels=0;
        for(const [x,y,z,id] of data.blocks) {
            const expected=data.palette[id];
            // Explicit interior air must stay clear, including the old bed/loot locations.
            if(expected.name==='air') {
                if((y>=5 && y<=13) || (y>=15 && y<=20 && z>=86 && z<=103 && x>=14 && x<=34)) {
                    check(dimension.getBlock(position(data.origin,[x,y,z])).typeId==='minecraft:air',
                          'Interior obstructed '+variant+' '+[x,y,z]);
                    interiorAir++;
                }
                continue;
            }
            const actual=dimension.getBlock(position(data.origin,[x,y,z]));
            const canonical=BlockPermutation.resolve(expected.name.includes(':')?expected.name:'minecraft:'+expected.name,expected.states);
            if(actual.typeId!==canonical.type.id) {
                if(mismatch.length<30)mismatch.push({p:[x,y,z],expected:expected.name,actual:actual.typeId,
                    below:dimension.getBlock(position(data.origin,[x,y-1,z])).permutation.getAllStates()});
            }
            if(expected.name==='barrel') {
                const container=actual.getComponent('minecraft:inventory')?.container;
                check(container && container.emptySlotsCount===container.size,'Deck barrel contains loot '+variant);
                emptyBarrels++;
            }
            checked++;
            if(checked%700===0)await pause(1);
        }
        check(!mismatch.length,'Block mismatches '+variant+' '+JSON.stringify(mismatch));
        let dry=0;
        for(const [x,y,z,id] of data.blocks) {
            if(y<8 && data.palette[id].name==='air') {
                check(!['minecraft:water','minecraft:flowing_water'].includes(dimension.getBlock(position(data.origin,[x,y,z])).typeId),
                      'Flooded hold '+variant+' '+[x,y,z]);
                dry++;
            }
        }
        const crew=dimension.getEntities({tags:['dreadwake_'+variant],type:'minecraft:pillager'});
        check(crew.length===data.crew.length,'Crew count '+variant+': '+crew.length);
        for(const mob of crew) {
            check(mob.getComponent('minecraft:health').currentValue>0,'Crew dead');
            check(mob.location.y>=-56,'Crew fell below the lowest deck '+mob.nameTag);
        }
        for(let i=0;i<crew.length;i++)check(dimension.runCommand(`testfor @e[type=pillager,tag=dreadwake_${variant}_${i},hasitem={item=crossbow,location=slot.weapon.mainhand}]`).successCount>0,'Crew unarmed '+variant+' '+i);
        variants[variant]={checkedBlocks:checked,dryHoldCells:dry,clearInteriorCells:interiorAir,
                           emptyDeckBarrels:emptyBarrels,lootChests:data.loot.length,pillagers:crew.length};
        console.warn('DREADWAKE_VARIANT '+JSON.stringify({phase,variant,...variants[variant]}));
    }
    check(dimension.getBlock({x:260,y:-61,z:0})?.typeId==='minecraft:grass_block' ||
          dimension.getBlock({x:55,y:-61,z:0})?.typeId==='minecraft:grass_block','World not flat grass');
    console.warn('DREADWAKE_REPORT '+JSON.stringify({buildId:BUILD_ID,phase,passed:true,variants}));
}

async function testDecorAndLoot() {
    const p={x:0,y:40,z:0},block=dimension.getBlock(p);
    let permutations=0,interactions=0;
    for(const entry of DECOR) {
        block.setPermutation(BlockPermutation.resolve(entry.id));
        check(block.typeId===entry.id,'Unregistered decoration '+entry.id);
        for(const [state,values] of Object.entries(entry.states))for(const value of values) {
            block.setPermutation(BlockPermutation.resolve(entry.id,{[state]:value}));
            check(block.permutation.getState(state)===value,'Invalid decor state '+entry.id+' '+state);
            permutations++;
        }
        if(entry.interaction) {
            block.setPermutation(BlockPermutation.resolve(entry.id));
            const before=JSON.stringify(block.permutation.getAllStates());
            interactDecor(block,{isSneaking:false},entry.interaction);
            check(before!==JSON.stringify(block.permutation.getAllStates()),'Interaction did nothing '+entry.id);
            interactions++;
        }
        await pause(1);
    }
    for(const id of ITEMS)check(new ItemStack(id).typeId===id,'Item unavailable '+id);
    // Roll the native tables on disposable chests; leave actual ship loot unopened.
    const signatures=[];
    for(let i=0;i<12;i++) {
        block.setType('minecraft:air');
        world.structureManager.place('dreadwake:loot_probe',dimension,p,{includeEntities:false});
        await pause(1);
        dimension.runCommand('loot replace block 0 40 0 slot.container 0 loot \"ships/new_vault\"');
        const container=block.getComponent('minecraft:inventory')?.container;
        check(container,'Probe chest lacks inventory');
        const contents=[];
        for(let slot=0;slot<container.size;slot++) {
            const stack=container.getItem(slot);if(stack)contents.push([stack.typeId,stack.amount]);
        }
        signatures.push(JSON.stringify(contents));
    }
    block.setType('minecraft:air');
    check(new Set(signatures).size>=2,'Native chest loot did not vary: '+JSON.stringify(signatures));
    // Exercise the real projectile and impact recovery, with no players connected.
    fill([0,40,6],[2,43,6],'stone');
    const harpoon=dimension.spawnEntity('endless:harpoon_projectile',{x:0.5,y:42,z:0.5});
    harpoon.getComponent('minecraft:projectile').shoot({x:0,y:0,z:1.2});
    await pause(30);
    const recovered=dimension.getEntities({type:'minecraft:item'}).filter(e=>e.getComponent('minecraft:item').itemStack.typeId==='endless:harpoon');
    check(!harpoon.isValid && recovered.length===1,'Harpoon impact/recovery failed '+JSON.stringify({valid:harpoon.isValid,location:harpoon.isValid?harpoon.location:null,recovered:recovered.map(e=>e.location)}));
    for(const entity of recovered)entity.remove();
    fill([0,40,6],[2,43,6],'air');
    console.warn('DREADWAKE_DECOR_REPORT '+JSON.stringify({passed:true,blocks:DECOR.length,items:ITEMS.length,permutations,interactions,uniqueLootRolls:new Set(signatures).size,harpoonRecovery:true}));
}

world.afterEvents.worldLoad.subscribe(()=>system.run(async()=>{
    try {
        dimension=world.getDimension('overworld');
        // Fail early if any generated palette uses an unsupported Bedrock state.
        const checked=new Set();
        for(const data of Object.values(SHIPS))for(const block of data.palette) {
            const key=JSON.stringify(block);
            if(checked.has(key))continue;
            checked.add(key);
            try{BlockPermutation.resolve(block.name.includes(':')?block.name:'minecraft:'+block.name,block.states);}
            catch(e){throw Error('Invalid palette '+key+' '+e);}
        }
        await loadAreas();
        if(world.getDynamicProperty('dreadwake:built')) {
            check(world.getDynamicProperty('dreadwake:built')===BUILD_ID,
                  'Different layout already built here; prepare a fresh world folder');
            await pause(80);
            await inspect('reload');
            console.warn('DREADWAKE_RELOAD_READY');
            return;
        }
        for(const variant of Object.keys(SHIPS))for(const mob of dimension.getEntities({tags:['dreadwake_'+variant]}))mob.remove();
        dimension.runCommand('gamerule doMobSpawning false');
        dimension.runCommand('gamerule doDaylightCycle false');
        dimension.runCommand('gamerule doWeatherCycle false');
        dimension.runCommand('gamerule mobGriefing false');
        dimension.runCommand('gamerule doFireTick false');
        dimension.runCommand('time set noon');
        dimension.runCommand('weather clear');
        fill([-8,-52,-14],[248,-52,-3],'spruce_planks');
        for(const [variant,data] of Object.entries(SHIPS)) {
            await dock(data,variant);
            spawnCrew(data,variant);
            console.warn('DREADWAKE_PLACED '+variant);
        }
        sign({x:118,y:-51,z:-12},'DREADWAKE SHIPYARD\nFURNISHED EDITION\nExplore every deck\nLoot varies per chest');
        sign({x:122,y:-51,z:-12},'NEW | TATTERED | EMPTY\n12 crew | 8 crew | 0\nSurvival = hostile crew\nKeep Normal difficulty');
        world.setDefaultSpawnLocation({x:120,y:-51,z:-10});
        await pause(120);
        await testDecorAndLoot();
        await inspect('built');
        world.setDynamicProperty('dreadwake:built',BUILD_ID);
        // Remove detached decoration drops only in this isolated construction world.
        for(const item of dimension.getEntities({type:'minecraft:item'}))item.remove();
        console.warn('DREADWAKE_READY');
    }catch(e){console.error('DREADWAKE_FAIL '+e+' '+e.stack);}
}));
