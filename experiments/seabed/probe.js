import {system,world} from '@minecraft/server';
const pause=t=>new Promise(r=>system.runTimeout(r,t));
const liquid=new Set(['minecraft:water','minecraft:flowing_water','minecraft:kelp','minecraft:seagrass','minecraft:bubble_column']);
const sites=[['forest',0,0],['high_forest',4096,4096],['frozen_ocean',992,1056],['frozen_peaks',928,864],['warm_ocean',-2016,1184]];
world.afterEvents.worldLoad.subscribe(()=>system.run(async()=>{try{
const d=world.getDimension('overworld');
for(const [name,x,z] of sites){
 const start=Date.now(),key='endless:compare_'+name;
 await world.tickingAreaManager.createTickingArea(key,{dimension:d,from:{x,y:0,z},to:{x:x+15,y:0,z:z+15}});
 const generationMs=Date.now()-start;await pause(40);
 const r={name,x,z,generationMs,columns:256,surfaceFailures:0,aboveWater:0,ice:0,underwaterGrass:0,underwaterLogs:0,caveAir:0,caveWater:0,caveLava:0,caveHash:2166136261,ores:0,plants:{},biomes:{},floors:[],tops:[],materials:{}};
 let work=0;
 await new Promise(resolve=>system.runJob((function*(){
 for(let dx=0;dx<16;dx++)for(let dz=0;dz<16;dz++){
  let floor=null,top=null;
  const a={x:x+dx,y:62,z:z+dz};const biome=d.getBiome(a).id;r.biomes[biome]=(r.biomes[biome]??0)+1;
  if(!liquid.has(d.getBlock(a)?.typeId))r.surfaceFailures++;
  for(let y=319;y>=-64;y--){
   a.y=y;const id=d.getBlock(a)?.typeId;
   if(!id)throw new Error('Unloaded sample');
   if(id==='minecraft:ice'||id==='minecraft:packed_ice'||id==='minecraft:blue_ice'||id==='minecraft:frosted_ice')r.ice++;
   if(y>62 && id!=='minecraft:air')r.aboveWater++;
   if(y<63 && id==='minecraft:grass_block')r.underwaterGrass++;
   if(y<63 && id.endsWith('_log'))r.underwaterLogs++;
   if(y<63 && /coral|kelp|seagrass|sea_pickle/.test(id))r.plants[id]=(r.plants[id]??0)+1;
   if(y<0){
    const c=id==='minecraft:air'?1:id.includes('water')?2:id.includes('lava')?3:0;
    if(c===1)r.caveAir++;if(c===2)r.caveWater++;if(c===3)r.caveLava++;
    r.caveHash=Math.imul(r.caveHash^c,16777619)>>>0;
    if(id.includes('ore'))r.ores++;
   }
   const solid=id!=='minecraft:air'&&!liquid.has(id)&&!(/coral|sea_pickle|grass|flower|leaves|snow_layer/.test(id));
   if(solid&&top===null)top=y;
   if(y<=62&&solid&&floor===null){floor=y;r.materials[id]=(r.materials[id]??0)+1;}
   if(++work%4096===0)yield;
  }
  r.floors.push(floor);r.tops.push(top);
 }
 resolve();})()));
 console.warn('OCEAN_COMPARE '+JSON.stringify(r));
 world.tickingAreaManager.removeTickingArea(key);
}
console.warn('OCEAN_COMPARE_DONE');
}catch(e){console.error('OCEAN_COMPARE_FAIL '+e);}}));
