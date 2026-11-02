// Runs only on the isolated local BDS world; never packaged with the download.
import {world, system, BlockPermutation, ItemStack, SignSide} from '@minecraft/server';
import {SHIPS} from './data.js';

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
function furnish(data,variant) {
    for(const target of data.loot) {
        const p=position(data.origin,target.position),block=dimension.getBlock(p);
        const container=block.getComponent('minecraft:inventory')?.container;
        check(container,'Missing loot container '+variant+' '+JSON.stringify(target));
        for(let i=0;i<container.size;i++)container.setItem(i,undefined);
        target.items.forEach((item,i)=>container.setItem(i*2,new ItemStack('minecraft:'+item.name,item.amount)));
    }
    // Functional beds supplement the decorative stacked crew bunks.
    // Vanilla bed blocks default to red; both halves are set explicitly.
    for(const [x,y,z] of [[22,5,31],[26,5,31]]) {
        for(const [dz,head] of [[0,false],[1,true]]) {
            dimension.getBlock(position(data.origin,[x,y,z+dz])).setPermutation(
                BlockPermutation.resolve('minecraft:bed',{direction:0,head_piece_bit:head,occupied_bit:false}));
        }
    }
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
        let checked=0;
        for(const [x,y,z,id] of data.blocks) {
            const expected=data.palette[id];
            // Air is checked separately for flooding; these are all real ship blocks.
            if(expected.name==='air')continue;
            const actual=dimension.getBlock(position(data.origin,[x,y,z]));
            const canonical=BlockPermutation.resolve('minecraft:'+expected.name,expected.states);
            if(actual.typeId!==canonical.type.id) {
                if(mismatch.length<30)mismatch.push({p:[x,y,z],expected:expected.name,actual:actual.typeId,
                    below:dimension.getBlock(position(data.origin,[x,y-1,z])).permutation.getAllStates()});
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
        let filled=0,stacks=0;
        for(const target of data.loot) {
            const container=dimension.getBlock(position(data.origin,target.position)).getComponent('minecraft:inventory')?.container;
            check(container,'Container missing after load');
            for(let i=0;i<target.items.length;i++) {
                const item=container.getItem(i*2),want=target.items[i];
                check(item?.typeId==='minecraft:'+want.name && item.amount===want.amount,'Loot mismatch '+variant+' '+target.role);
                stacks++;
            }
            filled++;
        }
        const crew=dimension.getEntities({tags:['dreadwake_'+variant],type:'minecraft:pillager'});
        check(crew.length===data.crew.length,'Crew count '+variant+': '+crew.length);
        for(const mob of crew) {
            check(mob.getComponent('minecraft:health').currentValue>0,'Crew dead');
            check(mob.location.y>=-56,'Crew fell below the lowest deck '+mob.nameTag);
        }
        for(let i=0;i<crew.length;i++)check(dimension.runCommand(`testfor @e[type=pillager,tag=dreadwake_${variant}_${i},hasitem={item=crossbow,location=slot.weapon.mainhand}]`).successCount>0,'Crew unarmed '+variant+' '+i);
        variants[variant]={checkedBlocks:checked,dryHoldCells:dry,filledContainers:filled,lootStacks:stacks,pillagers:crew.length};
        console.warn('DREADWAKE_VARIANT '+JSON.stringify({phase,variant,...variants[variant]}));
    }
    check(dimension.getBlock({x:260,y:-61,z:0})?.typeId==='minecraft:grass_block' ||
          dimension.getBlock({x:55,y:-61,z:0})?.typeId==='minecraft:grass_block','World not flat grass');
    console.warn('DREADWAKE_REPORT '+JSON.stringify({phase,passed:true,variants}));
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
            try{BlockPermutation.resolve('minecraft:'+block.name,block.states);}
            catch(e){throw Error('Invalid palette '+key+' '+e);}
        }
        await loadAreas();
        if(world.getDynamicProperty('dreadwake:built')) {
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
            furnish(data,variant);
            console.warn('DREADWAKE_PLACED '+variant);
        }
        sign({x:118,y:-51,z:-12},'DREADWAKE SHIPYARD\nCreative review world\nFly into each ship\nLoot is in containers');
        sign({x:122,y:-51,z:-12},'NEW | TATTERED | EMPTY\n12 crew | 8 crew | 0\nSurvival = hostile crew\nKeep Normal difficulty');
        world.setDefaultSpawnLocation({x:120,y:-51,z:-10});
        await pause(120);
        await inspect('built');
        world.setDynamicProperty('dreadwake:built',true);
        // Remove detached decoration drops only in this isolated construction world.
        for(const item of dimension.getEntities({type:'minecraft:item'}))item.remove();
        console.warn('DREADWAKE_READY');
    }catch(e){console.error('DREADWAKE_FAIL '+e+' '+e.stack);}
}));
