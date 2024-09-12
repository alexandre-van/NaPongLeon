import * as THREE from '../../js/three.module.js';
import { loadModelGLT, loadTexture } from '../load.js';
import scene from '../scene.js';

async function createTable() {
	try {
		const model = await loadModelGLT('table.glb');
		const texture = await loadTexture ('wood.jpg')
		model.position.set(0, 0, -27.5);
		model.traverse(function (child) {
			if (child.isMesh) {
				child.material.map = texture;
				child.material.needsUpdate = true;
			}
		});
		scene.add(model);
	} catch (error) {
        console.error("Error: ", error);
    }
}

export { createTable };