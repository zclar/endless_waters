// Node tests with a small Script API stub, not a network/client simulation.
// Run: node --experimental-vm-modules experiments/sea_life/lifecycle_test.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const events = {};
let players = [], poll;
const warnings = [];
const context = vm.createContext({console:{warn:m=>warnings.push(m)},Set});
const api = new vm.SyntheticModule(['world','system','EquipmentSlot','ItemStack'], function(){
    this.setExport('world', {
        afterEvents:Object.fromEntries(['playerSpawn','playerLeave'].map(name=>[name,{
            subscribe:fn=>events[name]=fn,
        }])), getAllPlayers:()=>players,
    });
    this.setExport('system',{runInterval:fn=>poll=fn});
    this.setExport('EquipmentSlot',{Head:'head',Chest:'chest',Feet:'feet'});
    this.setExport('ItemStack',class {constructor(typeId,amount){Object.assign(this,{typeId,amount});}});
},{context});
const modules = new Map();
async function load(url){
    if(modules.has(url)) return modules.get(url);
    const module = new vm.SourceTextModule(fs.readFileSync(url,'utf8'),{context,identifier:url.href});
    modules.set(url,module);
    await module.link((name,parent)=>name==='@minecraft/server'?api:load(new URL(name,parent.identifier)));
    return module;
}
const gear=await load(new URL('../../scripts/diving_gear.js',import.meta.url));
await gear.evaluate();
function player(id,{full=false,props=new Map()}={}){
    const items=[],drops=[],effects=new Map();
    const p={id,isValid:true,props,items,drops,effects,equipment:{},
        location:{x:0,y:62,z:0},
        dimension:{spawnItem:item=>drops.push(item),getBlock:()=>{throw Error('Unexpected block read');}},
        getHeadLocation:()=>p.location,
        getDynamicProperty:key=>props.get(key),
        setDynamicProperty:(key,value)=>value===undefined?props.delete(key):props.set(key,value),
        getEffect:name=>effects.get(name),
        addEffect:(name,duration,options)=>effects.set(name,{duration,...options}),
        getComponent:name=>name==='minecraft:inventory'?{container:{addItem:item=>{
            if(full)return item;items.push(item);
        }}}:name==='minecraft:equippable'?{getEquipment:slot=>p.equipment[slot]}:undefined,
    };
    return p;
}
const a=player('a'),b=player('b');
for(const p of [a,b]){
    events.playerSpawn({initialSpawn:true,player:p});
    assert.equal(p.items[0].typeId,'minecraft:oak_boat');
    assert.equal(p.items.length,1);
    assert.equal(p.effects.get('water_breathing').duration,600);
    p.effects.clear();
    events.playerSpawn({initialSpawn:false,player:p});
    events.playerSpawn({initialSpawn:true,player:p});
    assert.equal(p.items.length,1);
    assert.equal(p.effects.size,0,'Reconnect must not refresh grace');
}
const reloaded=player('a',{props:new Map(a.props)});
events.playerSpawn({initialSpawn:true,player:reloaded});
assert.equal(reloaded.items.length,0,'Saved marker must prevent repeat grants');
const full=player('full',{full:true});
events.playerSpawn({initialSpawn:true,player:full});
assert.equal(full.drops.length,1);
assert.equal(full.items.length,0);
const potion=player('potion');
potion.effects.set('water_breathing',{duration:1200,amplifier:1});
events.playerSpawn({initialSpawn:true,player:potion});
assert.equal(potion.effects.get('water_breathing').duration,1200);
events.playerSpawn({initialSpawn:true,player:undefined});
// Bare players must not request blocks that can be unavailable while joining.
players=[a,b];poll();assert.equal(warnings.length,0);
// A bad/unloaded player must not prevent the next player's tank bonus.
a.equipment.head={typeId:'endless:deep_sea_helmet'};
b.equipment.chest={typeId:'endless:oxygen_tank'};
poll();assert.equal(b.effects.get('water_breathing').duration,100);
poll();assert.equal(warnings.length,1,'Repeated failures should not spam logs');
a.equipment={};poll();a.equipment.head={typeId:'endless:deep_sea_helmet'};
poll();assert.equal(warnings.length,2,'Failure after recovery should be reported');
console.log('PASS: two players, 600-tick grace, respawn/rejoin/reload, full inventory, potion preservation and isolated gear errors.');
