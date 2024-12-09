/**
 * Apply a set of styles to an element.
 * @param {HTMLElement} element - The element to style.
 * @param {Object} styles - A dictionary of styles.
 */
function applyStyles(element, styles) {
    Object.assign(element.style, styles);
}

/**
 * Create a paragraph with specific text and optional styles.
 * @param {string} text - The paragraph content.
 * @param {Object} [styles={}] - Optional styles to apply.
 * @returns {HTMLParagraphElement} The created paragraph.
 */
function createParagraph(text, styles = {}) {
    const paragraph = document.createElement('p');
    paragraph.textContent = text;
    applyStyles(paragraph, styles);
    return paragraph;
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
                <p style="margin: 3px 0; font-style: italic;">(Future value)</p>
                <p style="font-weight: bold; margin: 3px 0;">${score[team1.name] || '0'}</p>
            </div>
            <div style="border-left: 2px solid #5D4037; height: 50px; margin: 0 12px;"></div>
            <div style="text-align: center; margin-left: 12px;">
                <p style="font-weight: bold; margin: 3px 0;">${team2.name}</p>
                <p style="margin: 3px 0; font-style: italic;">(Future value)</p>
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
function showParchment(branch) {
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
 * Show the parchment for a specific team.
 * @param {Object} team - The team data.
 */
function showTeamParchment(team) {
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

export {showParchment, showTeamParchment} ;
