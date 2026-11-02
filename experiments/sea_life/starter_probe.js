// Server-only GameTest diagnostic. Copy the release's starter_boat.js beside it.
import {spawnSimulatedPlayer} from '@minecraft/server-gametest';
import {system, world, GameMode} from '@minecraft/server';
import {giveStarterBoat} from './starter_boat.js';

const pause = ticks => new Promise(resolve => system.runTimeout(resolve, ticks));
const check = (ok, why) => { if (!ok) throw new Error(why); };
const countBoats = player => {
    const inventory = player.getComponent('minecraft:inventory').container;
    let count = 0;
    for (let i = 0; i < inventory.size; i++) {
        const item = inventory.getItem(i);
        if (item?.typeId === 'minecraft:oak_boat') count += item.amount;
    }
    return count;
};

world.afterEvents.worldLoad.subscribe(() => system.run(async () => {
    try {
        const dimension = world.getDimension('overworld');
        await world.tickingAreaManager.createTickingArea('endless:starter_test', {
            dimension, from: {x:-2032,y:0,z:1168}, to: {x:-1937,y:0,z:1231},
        });
        const players = ['StarterA','StarterB'].map((name, i) =>
            spawnSimulatedPlayer({dimension,x:-2000+i*3,y:80,z:1200}, name, GameMode.Survival));
        await pause(10);
        for (const player of players) {
            // Simulated-player spawn events may not be forwarded from the
            // GameTest module. Exercise the exact production handler either way.
            if (!player.getDynamicProperty('endless:starter_boat_given')) {
                check(giveStarterBoat(player), 'Initial grant failed for '+player.name);
            }
            check(countBoats(player) === 1, 'Expected one boat for '+player.name);
            const effect = player.getEffect('water_breathing');
            check(effect && effect.duration <= 600 && effect.duration >= 580,
                'Expected 30-second breathing grace for '+player.name);
            check(!giveStarterBoat(player), 'Second grant was allowed for '+player.name);
            check(countBoats(player) === 1, 'Duplicate boat for '+player.name);
            console.warn('STARTER_TEST '+JSON.stringify({player:player.name, boats:1,
                breathingTicks:effect.duration, duplicatePrevented:true}));
        }
        for (const player of players) player.disconnect();
        console.warn('STARTER_TEST_DONE');
    } catch (e) {
        console.error('STARTER_TEST_FAIL '+e+' '+e.stack);
    }
}));
