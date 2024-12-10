import * as THREE from '../js/three.module.js';
import { renderer, camera, scene } from './renderer.js';
import { controls } from './controls.js'
import { updateTree } from './object/tree.js';
import { update_status, playerStatus } from './status.js'
import { launch_game, close_game } from './launch_game.js'

let animationId;

function startTournament() {
	animate();
}

function animate() {
	animationId = requestAnimationFrame(animate);
	renderer.render(scene, camera);
}

let lastplayerStatus = null;

async function updateTournament(data, nickname, game_private_id) {
	update_status(data.teams, nickname);
	if (playerStatus != "Join game..."
		&& playerStatus != "In game..."
		&& playerStatus != "Players are loading...") {
		close_game()
		updateTree(data.tree, nickname);
		renderer.render(scene, camera);
	}
	else if (playerStatus == "Join game..." && playerStatus != lastplayerStatus) {
		updateTree(data.tree, nickname);
		launch_game(data.teams, nickname, game_private_id)
	}
	lastplayerStatus = playerStatus
}

function stopAnimation() {
	cancelAnimationFrame(animationId);
}

export { startTournament, updateTournament, stopAnimation };