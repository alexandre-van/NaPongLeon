import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.136.0/build/three.module.js';
import { OrbitControls } from 'https://threejsfundamentals.org/threejs/resources/threejs/r122/examples/jsm/controls/OrbitControls.js';
import { camera, renderer } from './renderer.js';

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.25;
controls.enableZoom = true;
controls.mouseButtons = {
    LEFT: THREE.MOUSE.ROTATE,
    MIDDLE: THREE.MOUSE.DOLLY,
    RIGHT: THREE.MOUSE.PAN
};

function updateControls() {
    controls.update();
}

export { controls, updateControls };