import { OrbitControls } from '../.js/OrbitControls.js';
import { camera, renderer } from './renderer.js';

const controls = new OrbitControls(camera, renderer.domElement);
/*controls.enableDamping = true;
controls.dampingFactor = 0.25;
controls.enableZoom = true;
controls.mouseButtons = {
    LEFT: THREE.MOUSE.ROTATE,
    MIDDLE: THREE.MOUSE.DOLLY,
    RIGHT: THREE.MOUSE.PAN
};*/

function updateControls() {
    //controls.update();
}

export { controls, updateControls };