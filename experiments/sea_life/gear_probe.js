// Isolated GameTest diagnostic; not part of the distributed pack.
// Copy scripts/diving_gear.js beside this file unchanged. GameTest's simulated
// players are only exposed in script contexts importing the GameTest module.
import './diving_gear.js';
import {spawnSimulatedPlayer} from '@minecraft/server-gametest';
import {system,world,GameMode,ItemStack,EquipmentSlot,Direction} from '@minecraft/server';
const pause=t=>new Promise(r=>system.runTimeout(r,t));
const check=(v,m)=>{if(!v)throw new Error(m);};
const log=r=>console.warn('GEAR_TEST '+JSON.stringify(r));
world.afterEvents.worldLoad.subscribe(()=>system.run(async()=>{try{
 const d=world.getDimension('overworld');
 await world.tickingAreaManager.createTickingArea('endless:gear_test',{dimension:d,from:{x:-2032,y:0,z:1168},to:{x:-1937,y:0,z:1231}});
 const p=spawnSimulatedPlayer({dimension:d,x:-2000,y:52,z:1200},'GearTest',GameMode.Survival);
 p.addEffect('resistance',24000,{amplifier:4,showParticles:false});
 const eq=p.getComponent('minecraft:equippable');
 const movement=p.getComponent('minecraft:underwater_movement');
 const base=movement.currentValue;
 log({phase:'baseline',underwaterMovement:base});
 eq.setEquipment(EquipmentSlot.Head,new ItemStack('endless:deep_sea_helmet'));
 eq.setEquipment(EquipmentSlot.Chest,new ItemStack('endless:oxygen_tank'));
 eq.setEquipment(EquipmentSlot.Feet,new ItemStack('endless:flippers'));
 await pause(25);
 check(p.getEffect('night_vision'),'Helmet effect missing');
 check(p.getEffect('water_breathing'),'Oxygen tank effect missing');
 check(Math.abs(movement.currentValue-base*1.5)<.000001,'Flippers did not boost movement');
 await pause(100);
 check(Math.abs(movement.currentValue-base*1.5)<.000001,'Flippers stacked their multiplier');
 log({phase:'equipped',nightVision:true,waterBreathing:true,underwaterMovement:movement.currentValue,nonStacking:true});
 // Stronger/longer effects from other sources must not be shortened.
 p.addEffect('night_vision',1200,{amplifier:1,showParticles:false});
 await pause(20);
 check(p.getEffect('night_vision').amplifier===1 && p.getEffect('night_vision').duration>1100,'Gear overwrote a stronger effect');
 eq.setEquipment(EquipmentSlot.Head,undefined);eq.setEquipment(EquipmentSlot.Chest,undefined);eq.setEquipment(EquipmentSlot.Feet,undefined);
 await pause(120);
 check(Math.abs(movement.currentValue-base)<.000001,'Movement did not restore on removal');
 check(!p.getEffect('water_breathing'),'Tank effect did not expire');
 check(p.getEffect('night_vision')?.amplifier===1,'Removing gear stripped unrelated effect');
 log({phase:'removed',movementRestored:true,waterBreathingExpired:true,externalEffectPreserved:true});
 p.removeEffect('night_vision');
 // A helmet worn on land must not continually grant night vision.
 p.setGameMode(GameMode.Creative);p.teleport({x:-2000,y:80,z:1200});
 eq.setEquipment(EquipmentSlot.Head,new ItemStack('endless:deep_sea_helmet'));
 await pause(20);check(!p.getEffect('night_vision'),'Helmet applies underwater vision on dry land');
 eq.setEquipment(EquipmentSlot.Head,undefined);
 const blockResults=[];
 for(const [i,name] of ['driftwood_plank','sea_glass','polished_prismarine_bricks','pearl_lantern'].entries()){
  const below={x:-2000+i*3,y:52,z:1210};const above={...below,y:53};
  d.getBlock(below).setType('minecraft:stone');d.getBlock(above).setType('minecraft:air');
  p.teleport({x:below.x-1,y:54,z:1210});
  p.setItem(new ItemStack('endless:'+name),0,true);
  await pause(10); // Respect the simulated player's held-item use cooldown.
  check(p.useItemInSlotOnBlock(0,below,Direction.Up),'Could not place '+name);
  await pause(2);check(d.getBlock(above).typeId==='endless:'+name,'Wrong placed block '+name);
  d.runCommand(`setblock ${above.x} ${above.y} ${above.z} air destroy`);
  await pause(2);
  const drops=d.getEntities({type:'minecraft:item',location:above,maxDistance:2}).map(e=>e.getComponent('minecraft:item').itemStack.typeId);
  check(drops.includes('endless:'+name),'Missing block drop '+name);
  blockResults.push(name);
 }
 log({phase:'building_blocks',placementAndDrops:blockResults});
 // Spawn eggs and name-tag interaction use the real held-item path.
 for(const [i,name] of ['jellyfish','seahorse'].entries()){
  const below={x:-2000+i*3,y:52,z:1195};d.getBlock(below).setType('minecraft:stone');
  p.teleport({x:below.x-1,y:54,z:below.z});
  p.setItem(new ItemStack('endless:'+name+'_spawn_egg'),0,true);
  await pause(10);
  check(p.useItemInSlotOnBlock(0,below,Direction.Up),'Spawn egg failed '+name);
  await pause(2);
  const e=d.getEntities({type:'endless:'+name,location:{...below,y:53},maxDistance:2})[0];check(e,'Egg spawned nothing');
  const tag=new ItemStack('minecraft:name_tag');tag.nameTag='Kept_'+name;p.setItem(tag,0,true);
  check(p.interactWithEntity(e),'Name tag interaction failed');await pause(2);check(e.nameTag===tag.nameTag,'Name not applied');
 }
 log({phase:'creature_items',spawnEggs:2,nameTags:2});
 p.disconnect();console.warn('GEAR_TEST_DONE');
}catch(e){console.error('GEAR_TEST_FAIL '+e+' '+e.stack);}}));
