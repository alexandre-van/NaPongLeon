let current_parchment_type = null
let current_parchment_data = null

/**
 * Apply a set of styles to an element.
 * @param {HTMLElement} element - The element to style.
 * @param {Object} styles - A dictionary of styles.
 */
function applyStyles(element, styles) {
	Object.assign(element.style, styles);
}

/**
 * Generate the branch information based on its data.
 * @param {Object} branch - The branch data.
 * @returns {string} The HTML string for the branch information.
 */
function generateBranchContent(branch) {
	const { id, level, match, bench } = branch;
	const context = ['(Winner)', '(Final)', '(Semi-Final)', '(Quarter-Final)'][level] || '';
	const baseHTML = `
		<h2 style="margin: 0; text-align: center; font-size: 23px;">Cell ${id}</h2>
		<p style="text-align: center; font-size: 17px; margin: 6px 0;">Level: ${level} ${context}</p>
	`;

	if (!match && !bench) {
		return baseHTML + `
			<p style="text-align: center; font-size: 17px; margin: 12px 0;">This cell is empty.</p>
		`;
	}

	if (bench && !match) {
		return baseHTML + `
			<h3 style="text-align: center; margin-top: 17px; font-size: 19px;">Bench</h3>
			<div style="text-align: center; font-size: 15px; margin-top: 6px;">
				<p style="font-weight: bold; margin: 3px 0;">Team: ${bench.name}</p>
			</div>
		`;
	}

	const { team1, team2, status, score, winner } = match;
	return baseHTML + `
		<h3 style="text-align: center; margin-top: 17px; font-size: 19px;">Match</h3>
		<p style="text-align: center; font-size: 17px; font-weight: bold;">
			${team1.name} <span style="font-size: 15px; font-weight: normal;">vs</span> ${team2.name}
		</p>
		<p style="text-align: center; margin: 6px 0; font-size: 15px;">
			<strong>Status:</strong> ${status}
		</p>
		<h3 style="text-align: center; margin-top: 17px; font-size: 19px;">Score</h3>
		<div style="display: flex; justify-content: center; align-items: center; font-size: 15px; margin: 12px 0;">
			<div style="text-align: center; margin-right: 12px;">
				<p style="font-weight: bold; margin: 3px 0;">${team1.name}</p>
				<p style="margin: 3px 0; font-style: italic;">(${match.team_in_game[team1.name]})</p>
				<p style="font-weight: bold; margin: 3px 0;">${score[team1.name] || '0'}</p>
			</div>
			<div style="border-left: 2px solid #5D4037; height: 50px; margin: 0 12px;"></div>
			<div style="text-align: center; margin-left: 12px;">
				<p style="font-weight: bold; margin: 3px 0;">${team2.name}</p>
				<p style="margin: 3px 0; font-style: italic;">(${match.team_in_game[team2.name]})</p>
				<p style="font-weight: bold; margin: 3px 0;">${score[team2.name] || '0'}</p>
			</div>
		</div>
		<h3 style="text-align: center; margin-top: 17px; font-size: 19px;">Winner</h3>
		<p style="text-align: center; font-size: 15px;">
			${winner || 'Not yet defined'}
		</p>
	`;
}

/**
 * Show the parchment for a specific branch.
 * @param {Object} branch - The branch data.
 */
export function showParchment(branch) {
	current_parchment_type = 'branch';
	current_parchment_data = branch;
	const parchmentDiv = document.getElementById('parchment');
	parchmentDiv.style.display = 'block';

	const branchInfoDiv = document.getElementById('branchInfo');
	applyStyles(branchInfoDiv, {
		fontFamily: `'Dancing Script', cursive`,
		lineHeight: '1.15',
		fontSize: '15px',
	});

	branchInfoDiv.innerHTML = generateBranchContent(branch);
}

/**
 * Generate the detailed content for a team.
 * @param {Object} team - The team data.
 * @returns {string} The HTML string for the team details.
 */
/**
 * Generate the content for a team, formatted strictly as per the style.
 * @param {Object} team - The team data.
 * @param {Array} matchHistory - An array of match history objects.
 * @returns {string} The HTML string for the team details.
 */
function generateTeamContent(team) {
	const { name, status, players, level, current_cell_id } = team;

	// Map level to its corresponding context
	const levelContext = ['(Winner)', '(Final)', '(Semi-Final)', '(Quarter-Final)'][level] || '';

	// Players section
	const playerList = players
		.map(player => `
			<p style="font-weight: bold; font-size: 18px; margin: 6px 0;">${player.nickname}</p>
			<p style="font-style: italic; font-size: 16px; margin: 3px 0;">Status: ${player.status || 'Unknown'}</p>
		`)
		.join('<br>');

	// Match history section
	//const matchHistoryList = matchHistory
	//    .map(match => `
	//        <p style="font-weight: bold; font-size: 17px; margin: 6px 0;">
	//            ${match.team1} vs ${match.team2}
	//        </p>
	//    `)
	//    .join('<br>');

	return `
		<p style="font-weight: bold; font-size: 23px; margin: 6px 0;">${name}</p>
		<p style="font-size: 17px; margin: 6px 0;">Level: ${level || 'N/A'} ${levelContext}</p>
		<p style="font-style: italic; font-size: 16px; margin: 6px 0;">Status: ${status || 'Unknown'}</p>
		<p style="font-weight: bold; margin: 12px 0; margin-top: 17px; font-size: 19px; ">Players</p>
		${playerList || '<p>No players in this team.</p>'}
		<br>
	`;
}

/**
 * Update the parchment display with new data without regenerating the full HTML.
 * @param {HTMLElement} element - The element containing the parchment content.
 * @param {Object} data - The updated data for the parchment.
 * @param {Function} generateContent - A function to generate the updated HTML content for specific data.
 */
function updateParchment(element, data, generateContent) {
	// Create a temporary container to generate the new content
	const tempContainer = document.createElement('div');
	tempContainer.innerHTML = generateContent(data);

	// Compare and update each field individually
	Array.from(tempContainer.children).forEach((newChild, index) => {
		const currentChild = element.children[index];

		if (!currentChild || newChild.outerHTML !== currentChild.outerHTML) {
			// Replace or update the field only if it's different
			if (currentChild) {
				element.replaceChild(newChild, currentChild);
			} else {
				element.appendChild(newChild);
			}
		}
	});
}

/**
 * Update branch parchment with new data.
 * @param {Object} branch - The updated branch data.
 */
export function updateBranchParchment(branch) {
	if (current_parchment_type == 'branch' && current_parchment_data.id == branch.id) {
		const branchInfoDiv = document.getElementById('branchInfo');
		updateParchment(branchInfoDiv, branch, generateBranchContent);
	}
}

/**
 * Update team parchment with new data.
 * @param {Object} team - The updated team data.
 */
export function updateTeamParchment(team) {
	if (current_parchment_type == 'team' && current_parchment_data.name == team.name) {
		const branchInfoDiv = document.getElementById('branchInfo');
		updateParchment(branchInfoDiv, team, generateTeamContent);
	}
}



/**
 * Show the parchment for a specific team.
 * @param {Object} team - The team data.
 */
export function showTeamParchment(team) {
	current_parchment_type = 'team';
	current_parchment_data = team;
	const parchmentDiv = document.getElementById('parchment');
	parchmentDiv.style.display = 'block';

	const branchInfoDiv = document.getElementById('branchInfo');
	applyStyles(branchInfoDiv, {
		fontFamily: `'Dancing Script', cursive`,
		lineHeight: '1.15',
		fontSize: '15px',
	});

	branchInfoDiv.innerHTML = generateTeamContent(team);
}

// Close button functionality for both parchments
document.getElementById('closeParchment').addEventListener('click', () => {
	const parchmentDiv = document.getElementById('parchment');
	parchmentDiv.style.display = 'none';
});
