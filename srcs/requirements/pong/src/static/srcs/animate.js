import * as THREE from '../.js/three.module.js';
import { updateBallPosition } from './object/ball.js'
import { updatePadsPosition } from './object/pad.js'
import { renderer, camera, scene } from './renderer.js';
import { updateMap2Mixer } from './object/map2.js'
import { controls } from './controls.js'

let animationId;
const clock = new THREE.Clock();

function startGame() {
	animate();
}

function animate() {
	animationId = requestAnimationFrame(animate);
	const delta = clock.getDelta();
	updateMap2Mixer(delta);
	renderer.render(scene, camera);
}

function updateGame(state) {
	updateBallPosition(state.bp);
	updatePadsPosition(state.pp);
}

function stopAnimation() {
	cancelAnimationFrame(animationId);
}

export { startGame, updateGame, stopAnimation };