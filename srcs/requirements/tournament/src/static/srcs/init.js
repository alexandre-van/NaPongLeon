import { renderer, camera, scene } from './renderer.js';
import generateTree from './object/tree.js';

async function init(data, ws){
	generateTree(data.tree);
	renderer.render(scene, camera);
	console.log("ready");
	ws.send(JSON.stringify({type: 'ready'}));
}

export { init }