import * as THREE from '../../js/three.module.js';
import scene from '../scene.js';

function createPlateau(data) {
    const textureLoader = new THREE.TextureLoader();
    textureLoader.load('/api/pong/static/texture/plain.jpg', function (texture) {
        const plateauGeometry = new THREE.BoxGeometry(data.size.x, data.size.y, 0.1);
        const plateauMaterial = new THREE.MeshStandardMaterial({
            map: texture
        });
        const plateau = new THREE.Mesh(plateauGeometry, plateauMaterial);
        plateau.position.set(0, 0, -0.1);
        plateau.castShadow = false;
        scene.add(plateau);
    });
}

export { createPlateau };
