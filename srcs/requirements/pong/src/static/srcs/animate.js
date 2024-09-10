import { updateControls } from './controls.js';
import { updateBallPosition } from './ball.js'
import { updatePadsPosition } from './pad.js'
import { renderer, camera, scene } from './renderer.js';


function startGame() {
    requestAnimationFrame(animate);
}

function animate() {
    requestAnimationFrame(animate);
    updateControls();
    renderer.render(scene, camera);
}

function updateGame(state) {
    updateBallPosition(state.bp);
    updatePadsPosition(state.pp);
}

export { startGame, updateGame };