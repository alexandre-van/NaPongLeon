import { init } from './srcs/init.js';
import { startGame, updateGame, stopAnimation } from './srcs/animate.js';
import {scene, cleanup} from './srcs/scene.js';
import './srcs/object/camera.js';

const host = window.location.hostname;
const port = window.location.port;
const gameId = new URLSearchParams(window.location.search).get('gameId');
const socket = new WebSocket(`ws://${host}:${port}/ws/pong/${gameId}/`);
//const socket = new WebSocket(`ws://${host}:${port}/ws/pong/_/_/`);

socket.onopen = function() {
	console.log("WebSocket connection established.");
	const cookies = document.cookie;

	socket.send(JSON.stringify({
		type: 'auth',
		cookies: cookies
	}));
};

socket.onmessage = function(event) {
	const data = JSON.parse(event.data);
	switch (data.type) {
		case "waiting_room":
			console.log("Waiting for an opponent to join...");
			break;
		case "export_data":
			console.log("Game created! \nGame ID :", gameId);
			init(data.data, socket);
			break;
		case "game_start":
			console.log("Game started!");
			startGame();
			break;
		case "gu":
			console.log("Game state updated:", data);
			updateGame(data);
			break;
		case "scored":
			console.log(data.msg);
			break;
		case "game_end":
			//socket.close();
			console.log("Game ended. Reason:", data.reason);
			stopGame()
			break;
		default:
			console.log("Unknown message type:", data.type);
	}
};

socket.onclose = function(event) {
	console.log("WebSocket connection closed.", event);
	stopGame()
}; 

socket.onerror = function(error) {
	console.error("WebSocket error:", error);
	stopGame()
};

function stopGame() {
	console.log("Jeu terminé.");
	socket.close();
	stopAnimation();
	cleanup();
	
	window.parent.postMessage('game_end', '*');
}



function sendMove(input) {
	socket.send(JSON.stringify({
		type: 'move',
		input: input
	}));
}

export { sendMove };