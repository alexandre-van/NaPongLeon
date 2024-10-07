import * as THREE from '../js/three.module.js';
import { updateBallPosition } from './object/ball.js'
import { updatePadsPosition } from './object/pad.js'
import { renderer, camera, scene } from './renderer.js';
import { updateControls } from './controls.js';
import { updateMap2Mixer } from './object/map2.js'

const clock = new THREE.Clock();

function startGame() {
	animate();
}

function animate() {
	requestAnimationFrame(animate);
	//updateControls();
	const delta = clock.getDelta();
	updateMap2Mixer(delta);
	renderer.render(scene, camera);
}

function updateGame(state) {
	updateBallPosition(state.bp);
	updatePadsPosition(state.pp);
}

export { startGame, updateGame };