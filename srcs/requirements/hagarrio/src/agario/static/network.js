import { updatePlayers, removePlayer, getMyPlayerId } from './player.js';
import { updateFood } from './food.js';
import { startGameLoop, stopGameLoop } from './main.js';
import { updateGameInfo, showGameEndScreen } from './utils.js';
import { updatePowerUps, displayPowerUpCollected, createNewPowerUp, usePowerUp } from './powers.js';
import { updateHotbar } from './hotbar.js';

let socket;
let gameManagerSocket;

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
			//console.log('WebSocket readyState:', socket.readyState);
		};

		socket.onclose = function(event) {
			console.log('WebSocket connection closed:', event.code, event.reason);
		};

		socket.onmessage = function(e) {
			const data = JSON.parse(e.data);
			switch (data.type) {
				case 'waiting_room':
					//console.log('Waiting room:', data);
					updateGameInfo(data);
					document.getElementById('waitingRoom').style.display = 'block';
					document.getElementById('gameContainer').style.display = 'none';
					document.getElementById('gameInfoContainer').style.display = 'block';
					break;
				case 'update_waiting_room':
					// console.log('Update waiting room:', data);
					updateGameInfo(data);
					//updatePlayers(data.players, data.yourPlayerId);
					break;
				case 'game_started':
					// console.log('Game started:', data);
					updateGameInfo(data);
					document.getElementById('waitingRoom').style.display = 'none';
					document.getElementById('gameInfoContainer').style.display = 'none';
					document.getElementById('gameContainer').style.display = 'block';
					startGameLoop(data);
					break;
				case 'game_joined':
					// console.log('Joined existing game:', data);
					updateGameInfo(data);
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
				case 'power_up_spawned':
					// console.log('Power-up spawned:', data);
					createNewPowerUp(data.power_up);
					updatePowerUps(data.power_ups);
					break;
				case 'power_up_collected':
					updatePowerUps(data.power_ups);	
					if (data.player_id === getMyPlayerId()) {
						displayPowerUpCollected(data.power_up, true);
						updateHotbar(data.players[data.player_id].inventory);
					}
					break;
				case 'power_up_used':
					// console.log('Power up used:', data);
					if (data.player_id === getMyPlayerId()) {
						displayPowerUpCollected(data.power_up, false);
						updateHotbar(data.players[data.player_id].inventory);
					}
					break;
				case 'player_disconnected':
					// console.log('Player disconnected:', data);
					if (data.playerId) {
						// console.log('Removing player:', data.playerId);
						removePlayer(data.playerId);
					}
					if (data.games) {
						//console.log('Updating game info:', data);
						updateGameInfo(data);
					}
					break;
				case 'error':
					// console.log('Error:', data.message);
					break;
				case 'game_over':
					console.log('Game over:', data.loser.name);
					stopGameLoop();
					showGameEndScreen({
						winner: false,
						message: data.message_loser || `Score final : ${data.loser_score || 0}`,
						killer: data.winner?.name
					});
					break;
				case 'victory':
					console.log('Victory:', data.winner.name);
					stopGameLoop();
					showGameEndScreen({
						winner: true,
						message: data.message_winner || `Score final : ${data.winner_score || 0}`,
						victim: data.loser?.name
					});
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

// Fonction pour créer la connexion WebSocket
function connectGameManagerSocket() {
    return new Promise((resolve, reject) => {
        const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        const port = window.location.port;
        const wsUrl = `${wsProtocol}//${host}${port ? `:${port}` : ''}/ws/matchmaking/`;
        console.log('Attempting Game Manager WebSocket connection to:', wsUrl);
        
        try {
            gameManagerSocket = new WebSocket(wsUrl);
            //console.log('Game Manager WebSocket instance created');

            gameManagerSocket.onopen = function() {
                console.log('Game Manager WebSocket connection established successfully');
                resolve(gameManagerSocket);  // La connexion est prête, on résout la promesse
            };

            gameManagerSocket.onerror = function(error) {
                console.error('Game Manager WebSocket error:', error);
                reject(error);  // Si erreur, on rejette la promesse
            };

            gameManagerSocket.onclose = function(event) {
                console.log('Game Manager WebSocket connection closed:', event.code, event.reason);
            };

            gameManagerSocket.onmessage = handleMatchmakingMessages;

        } catch (error) {
            console.error('Error creating Game Manager WebSocket:', error);
            reject(error);  // Si erreur dans la création du WebSocket, on rejette la promesse
        }
    });
}

// Fonction pour gérer les messages du matchmaking
function handleMatchmakingMessages(e) {
    const data = JSON.parse(e.data);
    switch (data.status) {
        case 'queued':
            console.log('Matchmaking started:', data);
            break;
        case 'matchmaking_cancelled':
            console.log('Matchmaking cancelled:', data);
            break;
        case 'game_found':
            console.log('Game found:', data);
            joinGame(data.game_id);
            break;
        default:
            console.log('Unknown matchmaking message type:', data.status);
    }
}

// Fonction pour rejoindre le matchmaking
export async function startMatchmaking() {
    try {
        if (!gameManagerSocket || gameManagerSocket.readyState !== WebSocket.OPEN) {
            // Si la connexion WebSocket n'est pas encore ouverte, on attend
            await connectGameManagerSocket();
        }

        // Une fois la connexion établie, on envoie la requête
        gameManagerSocket.send(JSON.stringify({
            action: 'join_matchmaking',
            game_mode: 'HAGARRIO'
        }));

        return true;
    } catch (error) {
        console.error('Error starting matchmaking:', error);
        return false;
    }
}

// Fonction pour arrêter le matchmaking
export async function stopMatchmaking() {
    if (!gameManagerSocket || gameManagerSocket.readyState !== WebSocket.OPEN) {
        console.error('Game Manager WebSocket not ready');
        return false;
    }
    try {
        // On ferme la connexion WebSocket sans envoyer de message pour annuler le matchmaking
        gameManagerSocket.close();
        return true;
    } catch (error) {
        console.error('Error while closing WebSocket connection:', error);
        return false;
    }
}

export function joinGame(gameId) {
	if (!socket || socket.readyState !== WebSocket.OPEN) {
		console.error('Socket not ready');
		return;
	}
	
	socket.send(JSON.stringify({
		type: 'start_game',
		game_id: gameId
	}));
}
