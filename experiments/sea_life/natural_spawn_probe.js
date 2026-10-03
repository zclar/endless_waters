import * as GameTest from '@minecraft/server-gametest';
import {system,world,GameMode} from '@minecraft/server';
world.afterEvents.worldLoad.subscribe(()=>system.run(async()=>{try {
 console.warn('NATURAL_API '+Object.keys(GameTest).join(','));
 const d=world.getDimension('overworld');
 await world.tickingAreaManager.createTickingArea('endless:natural',{dimension:d,from:{x:-2048,y:0,z:1152},to:{x:-1953,y:0,z:1247}});
 const p=GameTest.spawnSimulatedPlayer({dimension:d,x:-2000,y:63,z:1200},'OceanTest',GameMode.Creative);
 console.warn('NATURAL_PLAYER_READY '+p.name);
 p.addEffect('water_breathing',24000,{showParticles:false});
 p.addEffect('resistance',24000,{amplifier:4,showParticles:false});
 let elapsed=0;
 const handle=system.runInterval(()=>{
  elapsed+=10;
  const counts={};
  for(const e of d.getEntities({location:{x:-2000,y:50,z:1200},maxDistance:80})){counts[e.typeId]=(counts[e.typeId]??0)+1;}
  console.warn('NATURAL_COUNTS '+JSON.stringify({seconds:elapsed,counts}));
  if(elapsed>=120){system.clearRun(handle);p.disconnect();console.warn('NATURAL_DONE');}
 },200);
}catch(e){console.error('NATURAL_FAIL '+e+' '+e.stack);}}));
