import { renderer, camera, scene } from './renderer.js';
import { generateTree } from './object/tree.js';
import { createPlateau } from './object/plateau.js'

async function init(data, ws){
	generateTree(data.tree);
	await createPlateau(data.tree);
	renderer.render(scene, camera);
	console.log("ready");
	ws.send(JSON.stringify({type: 'ready'}));
}

export { init }