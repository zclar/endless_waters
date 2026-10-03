// Standalone diagnostic pack only. Never included in the addon.
import {system, world} from '@minecraft/server';
const pause = ticks => new Promise(resolve => system.runTimeout(resolve, ticks));
const check = (value, message) => { if (!value) throw new Error(message); };
const variant = entity => entity.getComponent('minecraft:variant').value;
const health = entity => entity.getComponent('minecraft:health').currentValue;
const report = data => console.warn('SEA_LIFE_TEST ' + JSON.stringify(data));
world.afterEvents.worldLoad.subscribe(() => system.run(async () => {
 try {
  const d = world.getDimension('overworld');
  await world.tickingAreaManager.createTickingArea('endless:sealife_test', {
   dimension:d, from:{x:-2032,y:0,z:1168}, to:{x:-1969,y:0,z:1231}
  });
  await pause(40);
  if (world.getDynamicProperty('endless:sea_life_reload')) {
   // Swimmers can leave the original sample before shutdown. Load its neighbors
   // before interpreting an unloaded entity as a failed save.
   await world.tickingAreaManager.createTickingArea('endless:sealife_reload', {
    dimension:d, from:{x:-2064,y:0,z:1136}, to:{x:-1937,y:0,z:1263}
   });
   await pause(40);
   const expected=JSON.parse(world.getDynamicProperty('endless:sea_life_expected'));
   const pets=d.getEntities({tags:['endless:probe_pet']});
   check(pets.length===expected.length, `Reload lost pets: ${pets.length}/${expected.length}`);
   for(const row of expected) {
    const e=pets.find(e=>e.nameTag===row.name);
    check(e && variant(e)===row.variant, 'Reload changed color: '+row.name);
   }
   report({phase:'reload',pets:pets.length,colorsPreserved:true});
   console.warn('SEA_LIFE_TEST_DONE');return;
  }
  const pets=[],speciesResults=[];
  for(const species of ['jellyfish','seahorse']) {
   const spawned=[];
   for(let i=0;i<20;i++) {
    const location={x:-2015+(i%5)*4,y:54+(i%2),z:1185+Math.floor(i/5)*4};
    check(d.getBlock(location).typeId==='minecraft:water','Test spawn point is not water');
    const e=d.spawnEntity('endless:'+species,location);
    e.nameTag='EWTEST_'+species+'_'+i;
    e.addTag('endless:probe_pet');
    spawned.push(e);
   }
   await pause(2);
   const randomColors=spawned.map(variant);
   check(randomColors.every(v=>v>=0&&v<5),'Invalid random color');
   check(new Set(randomColors).size>=2,'Spawn initialization did not randomize');
   for(let i=0;i<spawned.length;i++) {
    const e=spawned[i];
    e.triggerEvent('endless:keep');
    e.triggerEvent('endless:color_'+(i%5));
   }
   await pause(2);
   for(let i=0;i<spawned.length;i++) {
    const e=spawned[i];
    check(variant(e)===i%5,'Color event failed');
    // Persistence/despawn are not exposed as Script API component wrappers;
    // verify retention through the subsequent real server restart instead.
    pets.push({e,start:e.location,health:health(e)});
   }
   speciesResults.push({species,spawned:spawned.length,randomColors:[...new Set(randomColors)].sort()});
  }
  await pause(240);
  let moved=0;
  for(const p of pets) {
   check(p.e.isValid,'Creature vanished underwater');
   check(health(p.e)===p.health,'Creature lost health underwater');
   check(p.e.location.y<63,'Creature swam out of the ocean');
   if(Math.hypot(p.e.location.x-p.start.x,p.e.location.y-p.start.y,p.e.location.z-p.start.z)>.1)moved++;
  }
  check(moved>=pets.length*.75,'Too many creatures are stuck');
  report({phase:'swimming',species:speciesResults,pets:pets.length,moved,underwaterSurvival:true});
  // Deliberate dry platform, confined to this temporary diagnostic world.
  d.runCommand('fill -2004 90 1205 -2000 90 1209 glass');
  const dry=['jellyfish','seahorse'].map((species,i)=>{
   const e=d.spawnEntity('endless:'+species,{x:-2003+i*2,y:91,z:1207});
   e.triggerEvent('endless:keep');return e;
  });
  await pause(440);
  check(dry.every(e=>!e.isValid),'Aquatic creatures survive indefinitely out of water');
  report({phase:'dry_land',suffocationPassed:true});
  // Use the engine's real death/loot path; accept either outcome of random drops.
  const lootSpot={x:-1980,y:55,z:1200};
  for(let i=0;i<32;i++) {
   const e=d.spawnEntity('endless:jellyfish',lootSpot);e.kill();
  }
  await pause(5);
  const drops=d.getEntities({type:'minecraft:item',location:lootSpot,maxDistance:8});
  const loot=drops.map(e=>e.getComponent('minecraft:item').itemStack.typeId);
  check(loot.length>0 && loot.every(id=>id==='minecraft:slime_ball'),'Unexpected or missing jellyfish loot');
  report({phase:'loot',drops:loot.length,onlySlimeBalls:true});
  world.setDynamicProperty('endless:sea_life_expected',JSON.stringify(pets.map(p=>({name:p.e.nameTag,variant:variant(p.e)}))));
  world.setDynamicProperty('endless:sea_life_reload',true);
  console.warn('SEA_LIFE_READY_RELOAD');
 } catch(e) { console.error('SEA_LIFE_TEST_FAIL '+e+' '+e.stack); }
}));
