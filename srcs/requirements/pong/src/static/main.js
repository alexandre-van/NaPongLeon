import scene from './srcs/scene.js';
import camera from './srcs/camera.js';
import plateau from './srcs/plateau.js';
import { borderTop, borderBottom, borderLeft, borderRight } from './srcs/border.js';
import { ball } from './srcs/ball.js';
import { pad1, pad2 } from './srcs/pad.js';
import { startGame, updateGame } from './srcs/animate.js';
import './srcs/lights.js';
import './srcs/keyboard.js';
import './srcs/collisions.js';

let game_id = null;

const socket = new WebSocket("ws://localhost:8080/ws/pong/");

socket.onopen = function(event) {
	console.log("WebSocket connection established.");
};

socket.onmessage = function(event) {
	console.log('Message received:', event.data);
	const data = JSON.parse(event.data);
	switch (data.type) {
		case "waiting_room":
			console.log("Waiting for an opponent to join...");
			break;
		case "game_start":
			const game_id = data.game_id;
			console.log("Game started! \nGame ID :", game_id);
            startGame(game_id);
			break;
		case "game_update":
			console.log("Game state updated:", data.state);
            updateGame(data);
			break;
		case "game_end":
			console.log("Game ended. Reason:", data.reason);
			socket.close();
			break;
		default:
			console.log("Unknown message type:", data.type);
	}
};

socket.onclose = function(event) {
	console.log("WebSocket connection closed.", event);
};

socket.onerror = function(error) {
	console.error("WebSocket error:", error);
};

function sendMove(position) {
    socket.send(JSON.stringify({
        type: 'move',
        position: position
    }));
}

export { sendMove };