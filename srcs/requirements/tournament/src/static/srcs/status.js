import { findCellByCellId } from './object/tree.js';
import { showParchment, showTeamParchment } from './object/parchment.js';

let teams = [];
let playerStatus = 'Unknown';

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
	});

	const statusButton = document.getElementById('statusButton');
	if (statusButton) {
		statusButton.textContent = playerStatus;
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
		showTeamParchment(team)
	}
}
/**
 * Generate the list of teams dynamically.
 */
function generateTeamList() {
	const teamList = document.getElementById('teamList');
	teamList.innerHTML = ''; // Clear the current list

	teams.forEach(team => {
		const li = document.createElement('li');
		applyStyles(li, {
			display: 'flex',
			flexDirection: 'column',
			justifyContent: 'center',
			alignItems: 'center',
			fontFamily: 'Dancing Script, cursive',
			fontSize: '18px',
			textAlign: 'center',
		});

		// Team Name and Status
		const teamName = document.createElement('div');
		teamName.textContent = team.name;

		const statusSpan = document.createElement('div');
		statusSpan.textContent = `Status: ${team.status || 'Unknown'}`;

		// Check if the team is "defeated"
		if (team.status === 'Defeated') {
			applyStyles(teamName, {
				fontSize: '20px',
				fontWeight: 'bold',
				color: 'red',
				textDecoration: 'line-through', // Barré
			});
			applyStyles(statusSpan, {
				color: 'red', // Status en rouge
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

		// Button Container
		const buttonContainer = document.createElement('div');
		applyStyles(buttonContainer, {
			display: 'inline-flex',
			alignItems: 'center',
			justifyContent: 'center',
			gap: '10px',
		});

		// Button for inspecting the team
		const inspectButton = createButton('Inspect', () => {
			inspect(team);
		});

		// Button for switching to the current cell
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

		teamList.appendChild(li);
	});
}


// Event listener for the team list button
document.getElementById('teamListButton').addEventListener('click', () => {
	const teamParchment = document.getElementById('teamParchment');
	teamParchment.style.display = teamParchment.style.display === 'none' ? 'block' : 'none';
	generateTeamList();
});

// Event listener for the close button
document.getElementById('closeTeamParchment').addEventListener('click', () => {
	const teamParchment = document.getElementById('teamParchment');
	teamParchment.style.display = 'none';
});

export { update_status, playerStatus };
