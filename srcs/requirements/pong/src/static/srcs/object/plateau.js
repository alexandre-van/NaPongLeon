import * as THREE from '../../.js/three.module.js';
import { loadTexture } from '../load.js';
import { scene } from '../scene.js';

async function createPlateau(data) {
    try {
        const texture = await loadTexture('plain.jpg');
        const plateauGeometry = new THREE.BoxGeometry(data.size.x, data.size.y, 0.1);
        const plateauMaterial = new THREE.MeshStandardMaterial({ map: texture });
        const plateau = new THREE.Mesh(plateauGeometry, plateauMaterial);
        plateau.position.set(0, 0, -0.1);
        plateau.castShadow = false;
        scene.add(plateau);

    } catch (error) {
        console.error('Error:', error);
    }
}

export { createPlateau };
