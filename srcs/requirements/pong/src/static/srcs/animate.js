import { controls, updateControls } from './controls.js';
import { updateBallPosition } from './ball.js'
import { updatePadsPosition } from './pad.js'
import { checkCollisions } from './collisions.js';
import { renderer, camera, scene } from './renderer.js';


function startGame(gameId) {
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