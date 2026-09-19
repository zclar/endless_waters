import { world } from '@minecraft/server';
import { initialize } from './runtime.js';

world.afterEvents.worldLoad.subscribe(initialize);
