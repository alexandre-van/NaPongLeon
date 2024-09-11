import * as THREE from '../../js/three.module.js';
import { GLTFLoader } from '../../js/GLTFLoader.js';
import scene from '../scene.js';

function createMap() {
	const loader = new GLTFLoader();
	loader.load('/api/pong/static/models/map.glb', function (gltf) {
		const model = gltf.scene;
		model.position.set(350, 1100, -60);
        model.scale.set(20, 20, 20);
		scene.add(model);
	});
}

export { createMap };