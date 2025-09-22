import { findCellByCellId } from './object/tree.js';
import { get_data_saved, get_nickname_saved } from './tournament.js'
import { create_interface } from './init.js'

let spectate = false;

function launch_game(teams, nickname, game_private_id){
	const parchmentDiv = document.getElementById('parchment');
	const teamParchment = document.getElementById('teamParchment');
    parchmentDiv.style.display = 'none';
	teamParchment.style.display = 'none';
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
		const gameUrl = `${location.origin}/api/${gameServiceName}/?gameId=${gameId}&specialId=${game_private_id}`;
		console.log(gameUrl);
		// Créer une iframe pour afficher le jeu
		const iframe = document.createElement('iframe');
		iframe.src = gameUrl;
		iframe.style.position = "fixed"; // Fixe pour qu'il reste à la même position
		iframe.style.top = "0";                 // Aligner en haut de la page
		iframe.style.left = "0";                // Aligner à gauche de la page
		iframe.style.width = "100%";           // Largeur : 100% de la fenêtre
		iframe.style.height = "100%"; // Hauteur : 100% de la fenêtre moins la hauteur de la barre
		iframe.style.border = "none";           // Supprimer les bordures
		iframe.style.zIndex = "9999";           // Mettre l'iframe au premier plan
		iframe.sandbox = "allow-scripts allow-same-origin"; // Sécuriser l'iframe
		iframe.scrolling = "no";
		// Supprimer l'ancienne iframe s'il en existe une
		const existingIframe = document.querySelector('#gameInTournamentFrame');
		if (existingIframe) {
			existingIframe.remove();
		}
		iframe.id = "gameInTournamentFrame";
		document.body.appendChild(iframe);
	}
}

function spectate_game(game) {
    const { id, service_name, spectator_id } = game;

    // Construire l'URL pour spectater le jeu
    const gameUrl = `${location.origin}/api/${service_name}/?gameId=${id}&specialId=${spectator_id}`;
	spectate = true;
    console.log(gameUrl);

    // Créer une iframe pour afficher le jeu
    const iframe = document.createElement('iframe');
    iframe.src = gameUrl;
    iframe.style.position = "fixed"; // Fixe pour qu'il reste à la même position
    iframe.style.top = "0";          // Aligner en haut de la page
    iframe.style.left = "0";         // Aligner à gauche de la page
    iframe.style.width = "100%";    // Largeur : 100% de la fenêtre
    iframe.style.height = "100%";   // Hauteur : 100% de la fenêtre
    iframe.style.border = "none";    // Supprimer les bordures
    iframe.style.zIndex = "9999";    // Mettre l'iframe au premier plan
	iframe.scrolling = "no";
    iframe.sandbox = "allow-scripts allow-same-origin"; // Sécuriser l'iframe

    // Supprimer l'ancienne iframe s'il en existe une
    const existingIframe = document.querySelector('#gameInTournamentFrame');
    if (existingIframe) {
        existingIframe.remove();
    }

    iframe.id = "gameInTournamentFrame";
    document.body.appendChild(iframe);

    // Ajouter le bouton pour arrêter de spectate
    create_stop_button();
}

function close_game(){
	const iframe = document.querySelector('#gameInTournamentFrame');
	if (iframe) {
		iframe.remove();
	}
}

function create_stop_button() {
    // Vérifier s'il existe déjà un bouton et le supprimer
    const existingButton = document.querySelector('#stopSpectateButton');
    if (existingButton) {
        existingButton.remove();
    }

    // Créer le bouton
    const button = document.createElement('button');
    button.id = 'stopSpectateButton';
    button.textContent = 'Stop Spectating';
    button.style.position = 'fixed';
    button.style.bottom = '20px';
    button.style.left = '3	0px';

    // Styles similaires à #menu button
    button.style.backgroundColor = '#941a1d';
    button.style.color = 'black';
    button.style.border = 'none';
    button.style.borderRadius = '5px';
    button.style.fontFamily = "'Dancing Script', cursive";
    button.style.cursor = 'pointer';
    button.style.margin = '0 5px';
    button.style.padding = '6px 14px';
    button.style.fontSize = '20px';
    button.style.transition = 'transform 0.2s ease, background-color 0.2s ease';
    button.style.zIndex = '10000';

    // Ajouter des effets au survol
    button.addEventListener('mouseover', () => {
        button.style.transform = 'scale(1.1)';
        button.style.backgroundColor = '#a52325'; // Une teinte plus claire au survol
    });

    button.addEventListener('mouseout', () => {
        button.style.transform = 'scale(1)';
        button.style.backgroundColor = '#941a1d'; // Retour à la couleur initiale
    });

    // Ajouter un événement de clic pour fermer l'iframe
    button.addEventListener('click', () => {
        close_spectate();
    });

    document.body.appendChild(button);
}


async function close_spectate() {
    // Supprimer l'iframe
	spectate = false;
    const iframe = document.querySelector('#gameInTournamentFrame');
    if (iframe) {
        iframe.remove();
    }

    // Supprimer le bouton
    const button = document.querySelector('#stopSpectateButton');
    if (button) {
        button.remove();
    }
	let data = get_data_saved()
	if (data)
		await create_interface(data, get_nickname_saved());
}

function get_spectate() {
	return spectate;
}

export { launch_game, close_game, spectate_game, close_spectate, get_spectate}