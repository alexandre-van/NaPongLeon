import * as THREE from '../../js/three.module.js';
import { GLTFLoader } from '../../js/GLTFLoader.js';
import scene from '../scene.js';

function createTable() {
	const loader = new GLTFLoader();
	loader.load('static/models/table.glb', function (gltf) {
		const model = gltf.scene;
		model.position.set(0, 0, -27.5);
		const textureLoader = new THREE.TextureLoader();
		textureLoader.load('static/texture/wood.jpg', function (texture) {
			model.traverse(function (child) {
				if (child.isMesh) {
					child.material.map = texture;
					child.material.needsUpdate = true;
				}
			});
		});
		scene.add(model);
	});
}

export { createTable };