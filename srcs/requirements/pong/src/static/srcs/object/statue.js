import * as THREE from '../../.js/three.module.js';
import { loadModelSTL } from '../load.js'
import { scene } from '../scene.js';

async function createStatue() {
	try {
		const geometry = await loadModelSTL('statue.stl');
		const material = new THREE.MeshStandardMaterial({ color: 0x318CE7 });
		const model = new THREE.Mesh(geometry, material);
		let size = 248
		model.position.set(-700, 700, size / 2 -80);
		scene.add(model);
	} catch (error) {
		console.error("Error: ", error);
	}
}

export { createStatue };
