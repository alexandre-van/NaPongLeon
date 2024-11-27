
const host = window.location.hostname;
const port = window.location.port;
const tournamentId = new URLSearchParams(window.location.search).get('gameId');
const socket = new WebSocket(`ws://${host}:${port}/ws/tournament/${gameId}/`);
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
			ws.send(JSON.stringify({type: 'ready'}));
			break;
		case "tournament_start":
			console.log("Tournament started!");
			break;
		case "tournament_end":
			//socket.close();
			console.log("Tournament ended. Reason:", data.reason);
			stopTournament()
			break;
		default:
			console.log("Unknown message type:", data.type);
	}
};

socket.onclose = function(event) {
	console.log("WebSocket connection closed.", event);
	stopTournament()
}; 

socket.onerror = function(error) {
	console.error("WebSocket error:", error);
	stopTournament()
};

function stopTournament() {
	console.log("Tournament removed.");
	socket.close();
	
	window.parent.postMessage('tournament_end', '*');
}