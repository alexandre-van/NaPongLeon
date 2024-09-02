import { controls, updateControls } from './controls.js';
import { updateBallPosition } from './ball.js'
import { updatePadsPosition } from './pad.js'
import { checkCollisions } from './collisions.js';
import { renderer, camera, scene } from './renderer.js';

function animate() {
    requestAnimationFrame(animate);
    updateControls();
    updatePadsPosition();
    updateBallPosition();
    renderer.render(scene, camera);
}

export default animate;