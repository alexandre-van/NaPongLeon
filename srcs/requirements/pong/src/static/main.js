import { init } from './srcs/init.js';
import { startGame, updateGame } from './srcs/animate.js';
import './srcs/scene.js';
import './srcs/object/camera.js';

let game_id = null;
const host = window.location.hostname;
const port = window.location.port;
const gameId = window.gameInfo.gameId;

const socket = new WebSocket(`ws://${host}:${port}/ws/pong/${gameId}/`);

socket.onopen = function() {
	console.log("WebSocket connection established.");
};

socket.onmessage = function(event) {
	const data = JSON.parse(event.data);
	switch (data.type) {
		case "waiting_room":
			console.log("Waiting for an opponent to join...");
			break;
		case "export_data":
			game_id = data.game_id
			console.log("Game created! \nGame ID :", game_id);
			init(data.data, socket);
			break;
		case "game_start":
			console.log("Game started!");
			startGame();
			break;
		case "gu":
			//console.log("Game state updated:", data);
			updateGame(data);
			break;
		case "scored":
			console.log(data.msg);
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

function sendMove(input) {
	socket.send(JSON.stringify({
		type: 'move',
		input: input
	}));
}

export { sendMove };