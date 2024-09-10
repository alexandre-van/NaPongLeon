import * as THREE from '../js/three.module.js';
import scene from './scene.js';

// Fonction pour créer le plateau
function createPlateau(data) {
	const plateauGeometry = new THREE.BoxGeometry(data.size.x, data.size.y, 0.1);
	const plateauMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
	const plateau = new THREE.Mesh(plateauGeometry, plateauMaterial);
	plateau.position.set(0, 0, -0.1);
	plateau.castShadow = false;
	scene.add(plateau);
}

export { createPlateau };
