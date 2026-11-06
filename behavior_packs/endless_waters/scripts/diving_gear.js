// Bedrock adaptation of Ocean Overhaul's independent diving-kit bonuses (MIT).
// Small player-only poll: no terrain edits, entity scans or world-generation work.
import {system, world, EquipmentSlot} from '@minecraft/server';
import './starter_boat.js';
import './decor.js';

const BASE = 'endless:flippers_base';
const BOOST = 'endless:flippers_boost';
const near = (a,b) => Math.abs(a-b)<0.000001;

function refresh(player, effect, duration, threshold) {
    const active=player.getEffect(effect);
    // Preserve stronger or longer potion/beacon effects. Let equipment bonuses
    // expire normally after removal instead of stripping unrelated effects.
    if (!active || (active.amplifier===0 && active.duration<threshold)) {
        player.addEffect(effect,duration,{amplifier:0,showParticles:false});
    }
}

export function updateDivingGear(player) {
    const equipment=player.getComponent('minecraft:equippable');
    if (!equipment) return;
    const head=equipment.getEquipment(EquipmentSlot.Head)?.typeId;
    const chest=equipment.getEquipment(EquipmentSlot.Chest)?.typeId;
    const feet=equipment.getEquipment(EquipmentSlot.Feet)?.typeId;
    if (head==='endless:deep_sea_helmet') {
        const headBlock=player.dimension.getBlock(player.getHeadLocation());
        const submerged=headBlock && ['minecraft:water','minecraft:flowing_water',
            'minecraft:kelp','minecraft:seagrass','minecraft:bubble_column'].includes(headBlock.typeId);
        if (submerged) refresh(player,'night_vision',300,230);
    }
    if (chest==='endless:oxygen_tank') refresh(player,'water_breathing',100,40);

    const previous=player.getDynamicProperty(BASE);
    if (feet!=='endless:flippers' && typeof previous!=='number') return;
    const movement=player.getComponent('minecraft:underwater_movement');
    if (!movement) return;
    const boost=player.getDynamicProperty(BOOST);
    if (feet==='endless:flippers') {
        // Persist the original value so removing gear after a reload restores it.
        // An externally changed value becomes the new baseline, not a value we
        // overwrite with a stale default. Never multiply our own boost again.
        if (typeof boost!=='number' || !near(movement.currentValue,boost)) {
            const base=movement.currentValue;
            const target=base*1.5;
            movement.setCurrentValue(target);
            player.setDynamicProperty(BASE,base);
            player.setDynamicProperty(BOOST,movement.currentValue);
        }
    } else if (typeof previous==='number') {
        if (typeof boost==='number' && near(movement.currentValue,boost)) {
            movement.setCurrentValue(previous);
        }
        player.setDynamicProperty(BASE,undefined);
        player.setDynamicProperty(BOOST,undefined);
    }
}

const reportedErrors = new Set();
world.afterEvents.playerLeave.subscribe(event=>reportedErrors.delete(event.playerId));
system.runInterval(()=>{
    for (const player of world.getAllPlayers()) {
        if (!player?.isValid) continue;
        try {
            updateDivingGear(player);
            reportedErrors.delete(player.id);
        } catch (error) {
            // A disconnect or unloaded block for one player must not interrupt
            // gear updates for the other players. Report once until recovery.
            if (player.isValid && !reportedErrors.has(player.id)) {
                console.warn('Endless Waters gear update: '+error);
                reportedErrors.add(player.id);
            }
        }
    }
},10);
