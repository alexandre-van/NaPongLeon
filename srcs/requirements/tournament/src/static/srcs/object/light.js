import * as THREE from '../../js/three.module.js';
import { get_scene } from '../scene.js';

let pointLight = null;
let ambientLight = null;

export function setupLights() {
    const scene = get_scene();

    pointLight = new THREE.PointLight(0xffffff, 1, 100);
    pointLight.position.set(10, 10, 10);
    scene.add(pointLight);

    ambientLight = new THREE.AmbientLight(0x404040); // Lumière douce
    scene.add(ambientLight);
}

export function removeLights() {
    const scene = get_scene();

    if (pointLight) {
        scene.remove(pointLight);
        pointLight.dispose();
        pointLight = null;
    }

    if (ambientLight) {
        scene.remove(ambientLight);
        ambientLight.dispose();
        ambientLight = null;
    }
}

