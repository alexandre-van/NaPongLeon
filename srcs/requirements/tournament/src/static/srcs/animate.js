import * as THREE from '../js/three.module.js';
import { renderer, camera, scene } from './renderer.js';
import { controls } from './controls.js'

let animationId;

function startTournament() {
	animate();
}

function animate() {
	animationId = requestAnimationFrame(animate);
	renderer.render(scene, camera);
}

function updateTournament(state) {
}

function stopAnimation() {
	cancelAnimationFrame(animationId);
}

export { startTournament, updateTournament, stopAnimation };