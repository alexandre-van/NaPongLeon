import * as THREE from '../../.js/three.module.js';
import { loadModelGLT } from '../load.js';
import { scene } from '../scene.js';

let map2_mixer;

async function createMap2() {
	try {
		const gltf = await loadModelGLT('map2.glb');  // Charger le GLTF, pas juste le modèle
		const model = gltf.scene;  // Obtenir le modèle à partir de gltf.scene
		model.position.set(-3, -3, -3.5);
		model.scale.set(40, 40, 40);
		model.rotation.set(THREE.MathUtils.degToRad(90), 0, 0);
		scene.add(model);

		// Créer l'AnimationMixer si des animations sont présentes
		if (gltf.animations && gltf.animations.length > 0) {
			map2_mixer = new THREE.AnimationMixer(model);  // Utiliser le modèle, pas le GLTF
			const action = map2_mixer.clipAction(gltf.animations[0]);  // Utiliser les animations de gltf
			action.play();
		}
	} catch (error) {
		console.error("Error: ", error);
	}
}

function updateMap2Mixer(delta) {
	if (map2_mixer) {
		map2_mixer.update(delta);  // Mettre à jour le mixer avec le delta
	}
}

export { createMap2, updateMap2Mixer };
