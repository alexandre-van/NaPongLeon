import { controls, updateControls } from './controls.js';
import { updateBallPosition } from './ball.js'
import { updatePadsPosition } from './pad.js'
import { checkCollisions } from './collisions.js';
import { renderer, camera, scene } from './renderer.js';


function startGame(gameId) {
    // On commence la boucle de rendu
    requestAnimationFrame(update);
    // On peut ajouter ici d'autres initialisations si nécessaire
}

function update() {
    requestAnimationFrame(update);
    updateControls();
    renderer.render(scene, camera);
}

function updateGame(state) {
    updateBallPosition(state.ball);
    updatePadsPosition(state.players_position_y);
}

export { startGame, updateGame };