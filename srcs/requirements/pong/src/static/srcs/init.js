import { init_keyboard } from './keyboard.js';
import { ball_init } from './object/ball.js';
import { padels_init } from './object/pad.js';
import { createBorders, createDashedLine } from './object/border.js';
import { createPlateau } from './object/plateau.js';
import { createSunlight, createPlateauLight } from './object/lights.js';
import { createTable } from './object/table.js';
import { createMap } from './object/map.js';
import { createCoins } from './object/coin.js';
import { createStatue } from './object/statue.js';

async function init(data, ws){
	init_keyboard(data.key, data.input);
	ball_init(data.ball);
	createBorders(data.arena);
	createDashedLine(data.arena);
	createSunlight();
	createPlateauLight();
	
	await padels_init(data.padel);
	await createPlateau(data.arena);
	await createMap();
	await createTable();
	await createCoins();
	await createStatue();
	ws.send(JSON.stringify({type: 'ready'}));
}

export { init }