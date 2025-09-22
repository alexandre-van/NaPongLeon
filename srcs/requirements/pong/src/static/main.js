import { init } from './srcs/init.js';
import { startGame, updateGame, stopAnimation } from './srcs/animate.js';
import { updateScore } from './srcs/object/score.js';
import { printWinner } from './srcs/object/win.js';
import {scene, cleanup} from './srcs/scene.js';
import './srcs/object/camera.js';

const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
const host = window.location.hostname;
const port = window.location.port;
const gameId = new URLSearchParams(window.location.search).get('gameId');
const specialId = new URLSearchParams(window.location.search).get('specialId');
const url = `${wsProtocol}//${host}${port ? `:${port}` : ''}/ws/pong/${gameId}${specialId ? `/${specialId}` : ''}/`;
const socket = new WebSocket(url);

socket.onopen = function() {
	console.log("WebSocket connection established.");
	const cookies = document.cookie;

	socket.send(JSON.stringify({
		type: 'auth',
		cookies: cookies
	}));
};

let playerLscore = 0;
let playerRscore = 0;

socket.onmessage = function(event) {
	const data = JSON.parse(event.data);
	switch (data.type) {
		case "waiting_room":
			console.log("Waiting for an opponent to join...");
			break;
		case "export_data":
			console.log("Game created! \nGame ID :", gameId);
			//console.log("DATA : ", data)
			init(data.data, socket);
			break;
		case "game_start":
			console.log("Game started!");
			startGame();
			break;
		case "gu":
			updateGame(data);
			break;
		case "scored":
			console.log("Scored :", data);
			if (data.team === "left") {
				playerLscore++;
			} else {
				playerRscore++;
			}
			updateScore(playerLscore, playerRscore);
			break;
		case "game_end":
			printWinner(data.team);
			console.log("Game ended. Reason:", data.reason);
			if (socket.readyState === WebSocket.OPEN)
				socket.close();
			break;
	}
};

socket.onclose = function(event) {
	console.log("WebSocket connection closed.", event);
}; 

socket.onerror = function(error) {
	console.error("WebSocket error:", error);
	stopGame();
};

function stopGame() {
    if (socket.readyState === WebSocket.OPEN)
        socket.close();
    stopAnimation();
    cleanup();
}


function sendMove(input) {
	if (socket.readyState === WebSocket.OPEN)
		socket.send(JSON.stringify({
			type: 'move',
			input: input
		}));
}

window.addEventListener('message', (event) => {
    if (event.data === 'stop_game') {
        stopGame();
    }
});


export { sendMove };