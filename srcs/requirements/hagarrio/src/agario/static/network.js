import { updatePlayers, removePlayer, getMyPlayerId } from './player.js';
import { updateFood } from './food.js';
import { startGameLoop } from './main.js';
import { updateGameInfo, showGameEndScreen } from './utils.js';
import { updatePowerUps, displayPowerUpCollected, createNewPowerUp, usePowerUp } from './powers.js';
import { updateHotbar } from './hotbar.js';

let socket;

document.addEventListener('keydown', (event) => {
	const keyToSlot = {
		'1': 0,
		'2': 1,
		'3': 2
	};

	if (keyToSlot.hasOwnProperty(event.key)) {
		const slotIndex = keyToSlot[event.key];
		usePowerUp(socket, slotIndex);
	}
});

export function initNetwork() {
	console.log('Initializing network connection...');
	connectWebSocket();
}

function connectWebSocket() {
	const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
	const host = window.location.hostname;
	const port = window.location.port;
	const wsUrl = `${wsProtocol}//${host}:${port}/ws/hagarrio/`;
	console.log('Attempting WebSocket connection to:', wsUrl);
	
	try {
		socket = new WebSocket(wsUrl);
		console.log('WebSocket instance created');

		socket.onopen = function() {
			console.log('WebSocket connection established successfully');
		};

		socket.onerror = function(error) {
			console.error('WebSocket error:', error);
			console.log('WebSocket readyState:', socket.readyState);
		};

		socket.onclose = function(event) {
			console.log('WebSocket connection closed:', event.code, event.reason);
		};

		socket.onmessage = function(e) {
			const data = JSON.parse(e.data);
			switch (data.type) {
				case 'waiting_room':
					console.log('Waiting room:', data);
					document.getElementById('waitingRoom').style.display = 'block';
					document.getElementById('gameContainer').style.display = 'none';
					updateGameInfo(data);
					document.getElementById('gameInfoContainer').style.display = 'block';
					break;
				case 'update_waiting_room':
					console.log('Update waiting room:', data);
					updateGameInfo(data);
					updatePlayers(data.players, data.yourPlayerId);
					break;
				case 'game_started':
					console.log('Game started:', data);
					updateGameInfo(data);
					document.getElementById('waitingRoom').style.display = 'none';
					document.getElementById('gameInfoContainer').style.display = 'none';
					document.getElementById('gameContainer').style.display = 'block';
					startGameLoop(data);
					break;
				case 'game_joined':
					console.log('Joined existing game:', data);
					document.getElementById('waitingRoom').style.display = 'none';
					document.getElementById('gameInfoContainer').style.display = 'none';
					document.getElementById('gameContainer').style.display = 'block';
					startGameLoop(data);
					break;
				case 'food_update':
					// console.log('FOOD_UPDATE:', data);
					updateFood(data.food);
					updatePlayers(data.players, data.yourPlayerId);
					break;
				case 'players_update':
					// console.log('PLAYERS_UPDATE:', data);
					updatePlayers(data.players, data.yourPlayerId);
					break;
				case 'player_disconnected':
					removePlayer(data.playerId);
					console.log('Game stopped');
					updateGameInfo(data);
					break;
				case 'power_up_spawned':
					console.log('Power-up spawned:', data);
					createNewPowerUp(data.power_up);
					updatePowerUps(data.power_ups);
					break;
				case 'power_up_collected':
					console.log('Power-up collected:', data);
					updatePowerUps(data.power_ups);
					if (data.yourPlayerId === getMyPlayerId()) {
						updateHotbar(data.players[data.yourPlayerId].inventory);
						displayPowerUpCollected(data.power_up, true);
					}
					break;
				case 'power_up_used':
					console.log('Power-up used:', data);
					if (data.yourPlayerId === getMyPlayerId()) {
						updateHotbar(data.players[data.yourPlayerId].inventory, data.slot_index);
					}
					break;
				case 'player_eat_other_player':
					console.log('Player ate other player:', data);
					updatePlayers(data.players, data.yourPlayerId);
					removePlayer(data.player_eaten);
					break;
				case 'game_over':
					console.log('Game ending:', data);
					showGameEndScreen(data);
					updateGameInfo(data);
					break;
				case 'error':
					console.log('Error:', data.message);
					break;
				default:
					console.log('Unknown message type:', data.type);
			}
		};

	} catch (error) {
		console.error('Error creating WebSocket:', error);
	}
}

export function sendPlayerMove(playerId, key, isKeyDown) {
	if (!socket || socket.readyState !== WebSocket.OPEN) {
		console.warn('Socket not ready, attempting to reconnect...');
		return;
	}
	try {
		socket.send(JSON.stringify({
			type: 'input',
			playerId: playerId,
			key: key,
			isKeyDown: isKeyDown
		}));
	} catch (error) {
		console.error('Error sending player move:', error);
	}
}


export async function startMatchmaking() {
	if (!socket || socket.readyState !== WebSocket.OPEN) {
		console.error('Socket not ready');
		return false;
	}
	try {
		const response = await fetch(`${location.origin}/api/game_manager/matchmaking/game_mode=HAGARRIO`);
		if (!response.ok) {
			console.error('Network response was not ok');
			return false;
		}
		const data = await response.json();
		const gameId = data.data.game_id;
		if (!gameId) {
			return false;
		}
		socket.send(JSON.stringify({
			type: 'start_game',
			game_id: gameId
		}));
		return true;
	} catch (error) {
		console.error('An error occurred:', error);
		return false;
	}
}

export async function stopMatchmaking() {
	if (!socket || socket.readyState !== WebSocket.OPEN) {
		console.error('Socket not ready');
		return false; // Retourne false si le socket n'est pas prêt
	}
	try {
		const response = await fetch(`${location.origin}/api/game_manager/matchmaking/game_mode=`);
		if (!response.ok) {
			return false; // Retourne false si la réponse réseau est invalide
		}
		return true; // Retourne true si tout s'est bien passé
	} catch (error) {
		console.error('An error occurred:', error);
		return false; // Retourne false en cas d'erreur
	}
}

export function joinGame(gameId) {
	if (!socket || socket.readyState !== WebSocket.OPEN) {
		console.error('Socket not ready');
		return;
	}
	
	socket.send(JSON.stringify({
		type: 'join_game',
		gameId: gameId
	}));
}

