import { init } from './srcs/init.js';
import { updateTournament, stopTournament } from './srcs/tournament.js'

const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
const host = window.location.hostname;
const port = window.location.port;
const tournamentId = new URLSearchParams(window.location.search).get('gameId');
const socket = new WebSocket(`${wsProtocol}//${host}:${port}/ws/tournament/${tournamentId}/`);
let nickname = ''
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
			console.log("Game created! \Tournament ID :", tournamentId);
			console.log("export_data : ", data);
			console.log("nickname : ", data.nickname);
			nickname = data.username;
			if (data.nickname)
				nickname = data.nickname;
			init(data.data, socket, nickname);
			break;
		case "tournament_update":
			console.log("Tournament update");
			console.log("tu : ", data);
			updateTournament(data, nickname, data.game_private_id);
			break;
		case "tournament_start":
			console.log("Tournament started!");
			break;
		case "tournament_end":
			console.log("Tournament ended.", data.reason);
			updateTournament(data, nickname, data.game_private_id);
			//stopTournament();
			break;
		default:
			console.log("Unknown message type:", data.type);
	}
};

socket.onclose = function(event) {
	console.log("WebSocket connection closed.", event);
	stopTournament();
}; 

socket.onerror = function(error) {
	console.error("WebSocket error:", error);
	stopTournament();
};