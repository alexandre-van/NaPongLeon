import { init_keyboard } from './keyboard.js';
import { ball_init } from './object/ball.js';
import { padels_init } from './object/pad.js';
import { createBorders, createDashedLine } from './object/border.js';
import { createPlateau } from './object/plateau.js';
import { createSunlight } from './object/lights.js';
import { createTable } from './object/table.js';
import { createMap } from './object/map.js';
import { createCoins } from './object/coin.js';

function init(data){
    init_keyboard(data.key, data.input);
    ball_init(data.ball);
    padels_init(data.padel);
    createBorders(data.arena);
    createDashedLine(data.arena);
    createPlateau(data.arena);
    createTable();
    createCoins();
    createMap();
    createSunlight();
}

export { init }