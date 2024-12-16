import { findCellByCellId } from './object/tree.js';
import { showParchment, showTeamParchment, updateTeamParchment } from './object/parchment.js';

let teams = [];
let playerStatus = 'Unknown';
let current_team_inspect = null;
let teamListIsOpen = false;

/**
 * Apply a set of styles to an element.
 * @param {HTMLElement} element - The element to style.
 * @param {Object} styles - A dictionary of styles.
 */
function applyStyles(element, styles) {
	Object.assign(element.style, styles);
}

/**
 * Create a button with specific properties.
 * @param {string} text - The button's text.
 * @param {Function} onClick - The click event handler.
 * @returns {HTMLButtonElement} The created button.
 */
function createButton(text, onClick) {
	const button = document.createElement('button');
	button.textContent = text;
	applyStyles(button, {
		fontFamily: `'Dancing Script', cursive`,
		fontSize: '16px',
		cursor: 'pointer',
	});
	button.addEventListener('click', onClick);
	return button;
}

/**
 * Update the player's status in the UI.
 * @param {Array} teamsUpdate - The updated list of teams.
 * @param {string} nickname - The player's nickname.
 */
function update_status(teamsUpdate, nickname) {
	teams = teamsUpdate;

	teams.forEach(team => {
		team.players.forEach(player => {
			if (player.nickname === nickname) {
				console.log(player.status);
				playerStatus = player.status;
			}
		});
		if (team.name == current_team_inspect)
			updateTeamParchment(team);
	});
	const statusButton = document.getElementById('statusButton');
	if (statusButton) {
		statusButton.textContent = playerStatus;
	}
	if (teamListIsOpen) {
		generateTeamList()
	}
}

function current_cell(team) {
	const cell = findCellByCellId(team.current_cell_id);
	if (cell) {
		alert(`Navigating to cell ID: ${cell.id}\nLevel: ${cell.level}`);
		showParchment(cell)
	} else {
		alert(`Cell with ID ${team.current_cell_id} not found.`);
	}
}

function inspect(team) {
	if (team) {
		alert(`Inspecting team: ${team.name}\nStatus: ${team.status}`);
		current_team_inspect = team.name;
		showTeamParchment(team)
	}
}

/**
 * Génère ou met à jour dynamiquement la liste des équipes.
 */
function generateTeamList() {
    const teamList = document.getElementById('teamList');

    // Sauvegarder la position de défilement actuelle
    const scrollTop = teamList.scrollTop;

    // Crée un dictionnaire des éléments actuels pour un accès rapide
    const existingItems = {};
    Array.from(teamList.children).forEach(li => {
        const teamNameDiv = li.querySelector('div:first-child');
        if (teamNameDiv) {
            existingItems[teamNameDiv.textContent] = li;
        }
    });

    // Mise à jour ou ajout des équipes
    teams.forEach(team => {
        let li = existingItems[team.name];
        if (!li) {
            // Créer un nouvel élément s'il n'existe pas encore
            li = document.createElement('li');
            applyStyles(li, {
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                fontFamily: 'Dancing Script, cursive',
                fontSize: '18px',
                textAlign: 'center',
            });

            // Ajouter au DOM
            teamList.appendChild(li);
        } else {
            // Effacer l'élément pour une mise à jour propre
            li.innerHTML = '';
        }

        // Nom de l'équipe et statut
        const teamName = document.createElement('div');
        teamName.textContent = team.name;

        const statusSpan = document.createElement('div');
        const newStatusText = `Status: ${team.status || 'Unknown'}`;
        if (statusSpan.textContent !== newStatusText) {
            statusSpan.textContent = newStatusText;
        }

        // Vérification si l'équipe est "défaite"
        if (team.status === 'Defeated') {
            applyStyles(teamName, {
                fontSize: '20px',
                fontWeight: 'bold',
                color: 'red',
                textDecoration: 'line-through', // Barré
            });
            applyStyles(statusSpan, {
                color: 'red', // Statut en rouge
            });
        } else {
            applyStyles(teamName, {
                fontSize: '20px',
                fontWeight: 'bold',
            });
            applyStyles(statusSpan, {
                fontSize: '16px',
                fontStyle: 'italic',
            });
        }

        li.appendChild(teamName);
        li.appendChild(document.createElement('br'));
        li.appendChild(statusSpan);
        li.appendChild(document.createElement('br'));

        // Conteneur des boutons
        const buttonContainer = document.createElement('div');
        applyStyles(buttonContainer, {
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
        });

        // Bouton pour inspecter l'équipe
        const inspectButton = createButton('Inspect', () => {
            inspect(team);
        });

        // Bouton pour passer à la cellule actuelle
        const currentCellButton = createButton('Current Cell', () => {
            current_cell(team);
        });

        const separator = document.createElement('span');
        separator.textContent = '|';
        applyStyles(separator, { color: '#000' });

        buttonContainer.appendChild(inspectButton);
        buttonContainer.appendChild(separator);
        buttonContainer.appendChild(currentCellButton);

        li.appendChild(buttonContainer);
        li.appendChild(document.createElement('br'));
    });

    // Supprimer les éléments qui ne sont plus dans la liste des équipes
    Array.from(teamList.children).forEach(li => {
        const teamNameDiv = li.querySelector('div:first-child');
        if (teamNameDiv && !teams.some(team => team.name === teamNameDiv.textContent)) {
            li.remove();
        }
    });

    // Restaurer la position de défilement
    teamList.scrollTop = scrollTop;
}



// Event listener for the team list button
document.getElementById('teamListButton').addEventListener('click', () => {
	teamListIsOpen = true
	const teamParchment = document.getElementById('teamParchment');
	teamParchment.style.display = teamParchment.style.display === 'none' ? 'block' : 'none';
	generateTeamList();
});

// Event listener for the close button
document.getElementById('closeTeamParchment').addEventListener('click', () => {
	teamListIsOpen = false
	const teamParchment = document.getElementById('teamParchment');
	teamParchment.style.display = 'none';
});

export { update_status, playerStatus };
