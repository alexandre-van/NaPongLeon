import * as THREE from '../js/three.module.js';
import scene from './scene.js';

function createSunlight() {
    // Ajouter une lumière ambiante pour un éclairage de base
    const ambientLight = new THREE.AmbientLight(0x404040); // Lumière ambiante douce
    scene.add(ambientLight);

    // Ajouter une lumière directionnelle pour simuler la lumière du soleil
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1); // Lumière directionnelle blanche
    directionalLight.position.set(100, 100, 100); // Positionner la lumière au-dessus de la scène
    directionalLight.castShadow = true; // Activer les ombres pour la lumière directionnelle

    // Configurer les ombres
    directionalLight.shadow.mapSize.width = 2048; // Résolution de la carte des ombres
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5; // Propriétés de la caméra d'ombre
    directionalLight.shadow.camera.far = 500;
    directionalLight.shadow.camera.left = -100; // Limites de la caméra d'ombre
    directionalLight.shadow.camera.right = 100;
    directionalLight.shadow.camera.top = 100;
    directionalLight.shadow.camera.bottom = -100;

    scene.add(directionalLight);

   // // Optionnel : Ajouter un helper pour visualiser la direction de la lumière
    //const lightHelper = new THREE.DirectionalLightHelper(directionalLight, 5);
    //scene.add(lightHelper);

    // Optionnel : Ajouter un helper pour visualiser les ombres
   // const shadowHelper = new THREE.CameraHelper(directionalLight.shadow.camera);
    //scene.add(shadowHelper);
}

export { createSunlight };
