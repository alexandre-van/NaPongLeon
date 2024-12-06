import { renderer, camera, scene } from './renderer.js';
import { generateTree } from './object/tree.js';
import { createPlateau } from './object/plateau.js'
import { update_status } from './object/status.js'

async function init(data, ws, nickname){
	const team_size = data.game_mode.team_size
	update_status(data.teams, nickname);
	generateTree(data.tree, nickname,team_size);
	await createPlateau(data.tree, team_size);
	renderer.render(scene, camera);
	console.log("ready");
	ws.send(JSON.stringify({type: 'ready'}));
}

export { init }