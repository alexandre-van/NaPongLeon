import { OrbitControls } from '../js/OrbitControls.js';
import { camera, get_renderer } from './renderer.js';

let controls = null;

export function getOrbitControls() {
    return controls;
}

export function setOrbitControls(customCamera = camera, canvas = get_renderer().domElement) {
    if (controls) {
        return controls;
    }

    controls = new OrbitControls(customCamera, canvas);

    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    //controls.screenSpacePanning = false;
    controls.minDistance = 1;
    controls.maxDistance = 100;

    return controls;
}

export function disposeOrbitControls() {
    if (!controls) {
        return;
    }

    controls.dispose();
    controls = null;
}

