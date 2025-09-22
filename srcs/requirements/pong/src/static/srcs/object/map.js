import { loadModelGLT } from '../load.js';
import { scene } from '../scene.js';

async function createMap() {
	try {
		const model = (await loadModelGLT('map.glb')).scene;
		model.position.set(350, 1100, -60);
        model.scale.set(20, 20, 20);
		scene.add(model);
	} catch (error) {
        console.error("Error: ", error);
    }
}

export { createMap };