// Give each player one vanilla boat and a brief breathing window when the
// addon first sees them. The marker persists across sessions and respawns.
import {ItemStack, world} from '@minecraft/server';

const GIVEN = 'endless:starter_boat_given';
const BREATHING_TICKS = 30 * 20;

export function giveStarterBoat(player) {
    if (player.getDynamicProperty(GIVEN)) return false;
    const inventory = player.getComponent('minecraft:inventory')?.container;
    if (!inventory) return false;

    const leftover = inventory.addItem(new ItemStack('minecraft:oak_boat', 1));
    if (leftover) player.dimension.spawnItem(leftover, player.location);
    player.setDynamicProperty(GIVEN, true);

    const breathing = player.getEffect('water_breathing');
    if (!breathing || (breathing.amplifier === 0 && breathing.duration < BREATHING_TICKS)) {
        player.addEffect('water_breathing', BREATHING_TICKS, {
            amplifier: 0, showParticles: false,
        });
    }
    return true;
}

world.afterEvents.playerSpawn.subscribe(event => {
    if (event.initialSpawn && event.player?.isValid) giveStarterBoat(event.player);
});
