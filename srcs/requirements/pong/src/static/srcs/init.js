import { init_keyboard } from './keyboard.js';
import { ball_init } from './object/ball.js';
import { padels_init } from './object/pad.js';
import { createBorders, createDashedLine } from './object/border.js';
import { createPlateau } from './object/plateau.js';
import { createSunlight, createPlateauLight } from './object/lights.js';
import { createTable } from './object/table.js';
import { createMap } from './object/map.js';
import { createMap2 } from './object/map2.js';
import { createCoins } from './object/coin.js';
import { createStatue } from './object/statue.js';
import { renderer, camera, scene } from './renderer.js';
import { createScore } from './object/score.js';
import { createName } from './object/name.js';

async function init_map1()
{
	await createMap();
	await createTable();
	await createCoins();
	await createStatue();
}

async function init_map2()
{
	await createMap2();
}

async function map_choice(map) {
	switch(map) {
		case "mountain":
			await init_map1();
			break;
		case "island":
			await init_map2();
			break;
	}
}

async function init(data, ws){
	init_keyboard(data.key, data.input);
	ball_init(data.ball);
	createBorders(data.arena);
	createDashedLine(data.arena);
	createSunlight();
	createPlateauLight();
	createScore();
	createName(data.teams);
	await padels_init(data.padel, data.game_mode);
	await createPlateau(data.arena);
	await map_choice(data.map);
	renderer.render(scene, camera);
	if (ws.readyState === WebSocket.OPEN)
		ws.send(JSON.stringify({type: 'ready'}));
}

export { init }