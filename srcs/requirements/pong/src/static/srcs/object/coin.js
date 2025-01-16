import * as THREE from '../../.js/three.module.js';
import { loadModelSTL, loadTexture } from '../load.js';
import { scene } from '../scene.js';

async function createCoins() {
	try {
		const geometry = await loadModelSTL('coin.stl');
		const material = new THREE.MeshStandardMaterial({ color: 0xffffff });
		const texture = await loadTexture('coin.jpg');
        material.map = texture;
        material.needsUpdate = true;
		const model = new THREE.Mesh(geometry, material);
        model.position.set(20, -35, 0);
        model.scale.set(1.5, 1.5, 1.5);
		scene.add(model);
	} catch (error) {
		console.error("Error: ", error);
	}
}

export { createCoins };