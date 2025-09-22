import { createRenderer, disposeRenderer, render } from './renderer.js';
import { createScene, cleanupScene } from './scene.js';
import { setOrbitControls, disposeOrbitControls } from './controls.js'
import { generateTree } from './object/tree.js';
import { createPlateau } from './object/plateau.js'
import { update_status } from './status.js'
import { animate, stopAnimation } from './animate.js';
import { setupLights, removeLights} from './object/light.js'
import { setupEventListeners, removeEventListeners} from './object/mouse.js'
import './object/mouse.js'

export async function init(data, ws, nickname){
	await create_interface(data, nickname, data.game_mode.team_size);
	console.log("ready");
	ws.send(JSON.stringify({type: 'ready'}));
}

export async function create_interface(data, nickname, team_size=null) {
	createScene();
	createRenderer();
	setupLights();
	setOrbitControls();
	animate();
	setupEventListeners();
	update_status(data.teams, nickname);
	generateTree(data.tree, nickname, team_size);
	await createPlateau(data.tree, team_size);
	render();
}

export async function remove_interface() {
	removeEventListeners();
	removeLights();
	stopAnimation();
	disposeOrbitControls();
	disposeRenderer();
	cleanupScene();
}