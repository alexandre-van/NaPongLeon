import { findCellByCellId } from './object/tree.js';

function launch_game(teams, nickname, game_private_id){
	let current_team = null
	let branch = null
	teams.forEach(team => {
		team.players.forEach(player => {
			if (player.nickname === nickname) {
				current_team = team;
			}
		});
	});
	if (current_team && current_team.current_cell_id)
		branch = findCellByCellId(current_team.current_cell_id)

	if (branch && branch.match && branch.match.game) {
		console.log(branch)
		const gameId = branch.match.game.id
		const gameServiceName = branch.match.game.service_name
		// Construire l'URL du jeu avec le gameId
		const protocol = location.protocol;
		const host = window.location.hostname;
		const port = window.location.port;
		const gameUrl = `${location.origin}/api/${gameServiceName}/?gameId=${gameId}&specialId=${game_private_id}`;
		console.log(gameUrl);
		// Créer une iframe pour afficher le jeu
		const iframe = document.createElement('iframe');
		iframe.src = gameUrl;
		iframe.style.position = "fixed"; // Fixe pour qu'il reste à la même position
		iframe.style.top = "0";                 // Aligner en haut de la page
		iframe.style.left = "0";                // Aligner à gauche de la page
		iframe.style.width = "100vw";           // Largeur : 100% de la fenêtre
		iframe.style.height = "100vh"; // Hauteur : 100% de la fenêtre moins la hauteur de la barre
		iframe.style.border = "none";           // Supprimer les bordures
		iframe.style.zIndex = "9999";           // Mettre l'iframe au premier plan
		iframe.sandbox = "allow-scripts allow-same-origin"; // Sécuriser l'iframe
		// Supprimer l'ancienne iframe s'il en existe une
		const existingIframe = document.querySelector('#gameInTournamentFrame');
		if (existingIframe) {
			existingIframe.remove();
		}
		iframe.id = "gameInTournamentFrame";
		document.body.appendChild(iframe);
	}
}

function close_game(){
	const iframe = document.querySelector('#gameInTournamentFrame');
	if (iframe) {
		iframe.remove();
	}
}

export { launch_game, close_game }