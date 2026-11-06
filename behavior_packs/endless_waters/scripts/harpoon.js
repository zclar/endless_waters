// Recover thrown harpoons exactly once. No inventory scans or player timers.
import {world, system, ItemStack, GameMode} from '@minecraft/server';
const ID='endless:harpoon_projectile';
function recover(projectile) {
    if (!projectile?.isValid || projectile.typeId!==ID || projectile.getDynamicProperty('endless:recovered')) return;
    projectile.setDynamicProperty('endless:recovered',true);
    const owner=projectile.getComponent('minecraft:projectile')?.owner;
    if (!owner?.isValid || owner.typeId!=='minecraft:player' || owner.getGameMode()!==GameMode.Creative) {
        projectile.dimension.spawnItem(new ItemStack('endless:harpoon',1),projectile.location);
    }
    projectile.remove();
}
world.afterEvents.projectileHitBlock.subscribe(event=>recover(event.projectile));
world.afterEvents.projectileHitEntity.subscribe(event=>recover(event.projectile));
world.afterEvents.entitySpawn.subscribe(event=>{
    if(event.entity.typeId===ID)system.runTimeout(()=>recover(event.entity),1200);
});
