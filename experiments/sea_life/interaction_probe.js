// Uses the same isolated GameTest-enabled world/manifest as natural_spawn_probe.js.
import {spawnSimulatedPlayer} from '@minecraft/server-gametest';
import {system,world,GameMode,ItemStack,Direction} from '@minecraft/server';
const pause=t=>new Promise(r=>system.runTimeout(r,t));
const check=(v,m)=>{if(!v)throw new Error(m);};
world.afterEvents.worldLoad.subscribe(()=>system.run(async()=>{try{
 const d=world.getDimension('overworld');
 await world.tickingAreaManager.createTickingArea('endless:interaction',{dimension:d,from:{x:-2032,y:0,z:1168},to:{x:-1969,y:0,z:1231}});
 const p=spawnSimulatedPlayer({dimension:d,x:-2000,y:54,z:1200},'InteractionTest',GameMode.Creative);
 p.addEffect('water_breathing',24000,{showParticles:false});
 const pets=[];
 for(const [i,species] of ['jellyfish','seahorse'].entries()){
  const block={x:-1998+i*3,y:52,z:1200};d.getBlock(block).setType('minecraft:stone');
  const egg=new ItemStack('endless:'+species+'_spawn_egg');
  p.teleport({x:block.x-1,y:54,z:block.z});
  p.setItem(egg,0,true);
  check(p.useItemInSlotOnBlock(0,block,Direction.Up),'Spawn egg use failed');
  await pause(2);
  const e=d.getEntities({type:'endless:'+species,location:{...block,y:53},maxDistance:2})[0];
  check(e,'Spawn egg did not create creature');
  const tag=new ItemStack('minecraft:name_tag');tag.nameTag='Test_'+species;
  p.setItem(tag,0,true);
  check(p.interactWithEntity(e),'Name tag interaction failed');
  await pause(2);check(e.nameTag===tag.nameTag,'Name tag did not apply');
  pets.push(e);
 }
 // Keep the aquarium chunks loaded while the player moves beyond the wild
 // despawn distance; named creatures must remain alive.
 p.teleport({x:-1840,y:70,z:1200});
 await pause(240);
 check(pets.every(e=>e.isValid),'Named creature despawned');
 console.warn('INTERACTION_TEST '+JSON.stringify({spawnEggs:2,nameTags:2,namedPetsRetained:2}));
 p.disconnect();console.warn('INTERACTION_DONE');
}catch(e){console.error('INTERACTION_FAIL '+e+' '+e.stack);}}));
