import * as THREE from '../../js/three.module.js';
import { GLTFLoader } from '../../js/GLTFLoader.js';
import scene from '../scene.js';

function createCoins() {
	const loader = new GLTFLoader();
	loader.load('static/models/coin.glb', function (gltf) {
		const model = gltf.scene;
		model.position.set(20, -35, 1);
        model.scale.set(2, 2, 2);
		const textureLoader = new THREE.TextureLoader();
		textureLoader.load('static/texture/coin/PIECE_PIECE_BaseColor.png', function (texture) {
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

export { createCoins };