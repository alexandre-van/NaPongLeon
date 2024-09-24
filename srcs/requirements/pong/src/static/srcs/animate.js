import { updateBallPosition } from './object/ball.js'
import { updatePadsPosition } from './object/pad.js'
import { renderer, camera, scene } from './renderer.js';
import { updateControls } from './controls.js';


function startGame() {
	animate();
}

function animate() {
	requestAnimationFrame(animate);
	//updateControls();
	renderer.render(scene, camera);
}

function updateGame(state) {
	updateBallPosition(state.bp);
	updatePadsPosition(state.pp);
}

export { startGame, updateGame };