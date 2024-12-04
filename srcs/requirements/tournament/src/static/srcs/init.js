import { renderer, camera, scene } from './renderer.js';
import { generateTree } from './object/tree.js';
import { createPlateau } from './object/plateau.js'

async function init(data, ws){
	const team_size = data.game_mode.team_size
	generateTree(data.tree, team_size);
	await createPlateau(data.tree, team_size);
	renderer.render(scene, camera);
	console.log("ready");
	ws.send(JSON.stringify({type: 'ready'}));
}

export { init }