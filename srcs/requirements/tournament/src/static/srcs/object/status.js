let teams = [];

function update_status(teams_update, nickname) {
    teams = teams_update;
    let playerStatus = "Unknown";

    teams.forEach(team => {
        team.players.forEach(player => {
            if (player.nickname === nickname) {
                playerStatus = player.status;
            }
        });
    });

    const statusButton = document.getElementById('statusButton');
    if (statusButton) {
        statusButton.textContent = playerStatus;
    }
}

document.getElementById('teamListButton').addEventListener('click', () => {
    const teamParchment = document.getElementById('teamParchment');
    // Toggle visibility of the team parchment
    teamParchment.style.display = 
        teamParchment.style.display === 'none' ? 'block' : 'none';

    const teamList = document.getElementById('teamList');
    teamList.innerHTML = ''; // Clear the current list

    // Dynamically generate the teams list
    teams.forEach(team => {
        const li = document.createElement('li');
        li.style.display = 'flex';
        li.style.flexDirection = 'column';
        li.style.justifyContent = 'center';
        li.style.alignItems = 'center';
        li.style.fontFamily = 'Dancing Script, cursive';
        li.style.fontSize = '18px';
        li.style.textAlign = 'center'; // Center text horizontally

        // Add team name (larger font)
        const teamName = document.createElement('div');
        teamName.textContent = team.name;
        teamName.style.fontSize = '20px';
        teamName.style.fontWeight = 'bold';
        li.appendChild(teamName);

        // Add line break
        li.appendChild(document.createElement('br'));

        // Add team status (smaller font)
        const statusSpan = document.createElement('div');
        statusSpan.textContent = `Status: ${team.status || 'Unknown'}`;
        statusSpan.style.fontSize = '16px';
        statusSpan.style.fontStyle = 'italic';
        li.appendChild(statusSpan);

        // Add line break
        li.appendChild(document.createElement('br'));

        // Add buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.style.display = 'inline-flex';
        buttonContainer.style.alignItems = 'center';
        buttonContainer.style.justifyContent = 'center';
        buttonContainer.style.gap = '10px';

        const inspectButton = document.createElement('button');
		inspectButton.style.fontFamily = `'Dancing Script', cursive`;
        inspectButton.textContent = 'Inspect';
        inspectButton.style.fontSize = '16px';
        inspectButton.style.cursor = 'pointer';
        inspectButton.addEventListener('click', () => {
            alert(`Inspecting ${team.name}`);
            // Add your inspect action here
        });

        const separator = document.createElement('span');
        separator.textContent = '|';
        separator.style.color = '#000';

        const currentCellButton = document.createElement('button');
        currentCellButton.textContent = 'Current Cell';
		currentCellButton.style.fontFamily = `'Dancing Script', cursive`;
        currentCellButton.style.fontSize = '16px';
        currentCellButton.style.cursor = 'pointer';
        currentCellButton.addEventListener('click', () => {
            alert(`Switching to ${team.name}`);
            // Add your current cell action here
        });

        buttonContainer.appendChild(inspectButton);
        buttonContainer.appendChild(separator);
        buttonContainer.appendChild(currentCellButton);

        li.appendChild(buttonContainer);

        // Add final line break
        li.appendChild(document.createElement('br'));

        teamList.appendChild(li);
    });
});

// Close button functionality
document.getElementById('closeTeamParchment').addEventListener('click', () => {
    const teamParchment = document.getElementById('teamParchment');
    teamParchment.style.display = 'none';
});

export { update_status };
