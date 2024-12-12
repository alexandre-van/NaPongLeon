import { create_interface, remove_interface} from './init.js'
import { update_status, playerStatus } from './status.js'
import { launch_game, close_game } from './launch_game.js'
import { updateTree } from './object/tree.js';

let in_game = false;
let lastplayerStatus = null;

export async function updateTournament(data, nickname, game_private_id) {
	update_status(data.teams, nickname);
	updateTree(data.tree, nickname);
	if (playerStatus != "Join game..."
		&& playerStatus != "In game..."
		&& playerStatus != "Players are loading...") {
		if (in_game) {
			close_game();
			await create_interface(data, nickname);
			in_game = false;
		}
	}
	else if (playerStatus == "Join game..." && playerStatus != lastplayerStatus) {
		in_game = true
		console.log(playerStatus)
		launch_game(data.teams, nickname, game_private_id);
		await remove_interface()
	}
	lastplayerStatus = playerStatus;
}

export async function stopTournament(socket) {
	console.log("Tournament removed.");
	socket.close();
	if (in_game)
		close_game();
	else
		await remove_interface();
	const iframe = document.querySelector('#gameInTournamentFrame');
	if (iframe) {
		iframe.remove();
	}
	window.parent.postMessage('tournament_end', '*');
}