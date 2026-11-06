// Modern Bedrock interactions for adapted decorative furniture.
// Event driven: no terrain or entity scans, and no background furniture ticks.
import {system} from '@minecraft/server';

import {interactDecor} from './decor_logic.js';
import './harpoon.js';

system.beforeEvents.startup.subscribe(event=>{
    event.blockComponentRegistry.registerCustomComponent('endless:decor_interact',{
        onPlayerInteract(event,config) {
            if (!event.player) return;
            interactDecor(event.block,event.player,config.params);
        },
    });
});
