import * as THREE from '../js/three.module.js';
import camera from './object/camera.js';
import { get_scene, scene } from './scene.js';

let renderer = null;

export function get_renderer() {
	return renderer;
}

export function render() {
	let scene = get_scene()
	if (renderer && scene && camera)
		renderer.render(get_scene(), camera);
}

export function createRenderer() {
	if (renderer) {
		console.warn("Renderer déjà créé. Retourne l'instance existante.");
		return renderer;
	}

	renderer = new THREE.WebGLRenderer();
	renderer.setSize(window.innerWidth, window.innerHeight);
	renderer.shadowMap.enabled = true;
	renderer.shadowMap.type = THREE.PCFSoftShadowMap;

	document.body.appendChild(renderer.domElement);
	window.addEventListener('resize', onWindowResize);
	return renderer;
}

export function disposeRenderer() {
	if (!renderer) {
		console.warn("Aucun renderer à libérer.");
		return;
	}

	if (renderer.domElement && renderer.domElement.parentNode) {
		renderer.domElement.parentNode.removeChild(renderer.domElement);
	}

	window.removeEventListener('resize', onWindowResize);

	renderer.dispose();
	renderer = null;

	console.log("Renderer libéré.");
}

function onWindowResize() {
	if (!renderer) return;

	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize(window.innerWidth, window.innerHeight);
}

export {camera}