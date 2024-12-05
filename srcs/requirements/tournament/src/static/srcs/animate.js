import * as THREE from '../js/three.module.js';
import { renderer, camera, scene } from './renderer.js';
import { controls } from './controls.js'
import { updateTree } from './object/tree.js';

let animationId;

function startTournament() {
	animate();
}

function animate() {
	animationId = requestAnimationFrame(animate);
	renderer.render(scene, camera);
}

async function updateTournament(tree, nickname) {
	updateTree(tree, nickname);
	renderer.render(scene, camera);
}

function stopAnimation() {
	cancelAnimationFrame(animationId);
}

export { startTournament, updateTournament, stopAnimation };