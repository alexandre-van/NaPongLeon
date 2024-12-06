function showParchment(branch) {
    const parchmentDiv = document.getElementById('parchment');
    parchmentDiv.style.display = 'block';

    const team1 = branch.match ? branch.match.team1 : null;
    const team2 = branch.match ? branch.match.team2 : null;
    const bench = branch.bench ? branch.bench : null;

    let context = '';
    switch (branch.level) {
        case 0: context = 'Winner'; break;
        case 1: context = 'Final'; break;
        case 2: context = 'Semi-Final'; break;
        case 3: context = 'Quarter-Final'; break;
        default: break;
    }

    const branchInfoDiv = document.getElementById('branchInfo');
    branchInfoDiv.style.fontFamily = `'Dancing Script', cursive`;
    branchInfoDiv.style.lineHeight = '1.15'; // Légère augmentation de l'interligne
    branchInfoDiv.style.fontSize = '15px'; // Légère augmentation de la taille du texte

    if (!branch.match && !bench) {
        branchInfoDiv.innerHTML = `
            <h2 style="margin: 0; text-align: center; font-size: 23px;">Cell ${branch.id}</h2> <!-- Légère augmentation de la taille du titre -->
            <p style="text-align: center; font-size: 17px; margin: 6px 0;">Level: ${branch.level} (${context})</p> <!-- Légère augmentation de la taille du texte -->
            <p style="text-align: center; font-size: 17px; margin: 12px 0;">This cell is empty.</p> <!-- Légère augmentation de la taille du texte -->
        `;
    } else if (bench && !branch.match) {
        branchInfoDiv.innerHTML = `
            <h2 style="margin: 0; text-align: center; font-size: 23px;">Cell ${branch.id}</h2>
            <p style="text-align: center; font-size: 17px; margin: 6px 0;">Level: ${branch.level} (${context})</p>
            <h3 style="text-align: center; margin-top: 17px; font-size: 19px;">Bench</h3> <!-- Légère augmentation de la taille du titre -->
            <div style="text-align: center; font-size: 15px; margin-top: 6px;">
                <p style="font-weight: bold; margin: 3px 0;">Team: ${bench.name}</p>
            </div>
        `;
    } else {
        branchInfoDiv.innerHTML = `
            <h2 style="margin: 0; text-align: center; font-size: 23px;">Cell ${branch.id}</h2>
            <p style="text-align: center; font-size: 17px; margin: 6px 0;">Level: ${branch.level} (${context})</p>
            <h3 style="text-align: center; margin-top: 17px; font-size: 19px;">Match</h3>
            <p style="text-align: center; font-size: 17px; font-weight: bold;">
                ${team1.name} <span style="font-size: 15px; font-weight: normal;">vs</span> ${team2.name}
            </p>
            <p style="text-align: center; margin: 6px 0; font-size: 15px;">
                <strong>State:</strong> ${branch.match.status}
            </p>
            <h3 style="text-align: center; margin-top: 17px; font-size: 19px;">Score</h3>
            <div style="display: flex; justify-content: center; align-items: center; font-size: 15px; margin: 12px 0;">
                <div style="text-align: center; margin-right: 12px;">
                    <p style="font-weight: bold; margin: 3px 0;">${team1.name}</p>
                    <p style="margin: 3px 0; font-style: italic;">(Future value)</p>
                    <p style="font-weight: bold; margin: 3px 0;">${branch.match.score[team1.name] || '0'}</p>
                </div>
                <div style="border-left: 2px solid #5D4037; height: 50px; margin: 0 12px;"></div>
                <div style="text-align: center; margin-left: 12px;">
                    <p style="font-weight: bold; margin: 3px 0;">${team2.name}</p>
                    <p style="margin: 3px 0; font-style: italic;">(Future value)</p>
                    <p style="font-weight: bold; margin: 3px 0;">${branch.match.score[team2.name] || '0'}</p>
                </div>
            </div>
            <h3 style="text-align: center; margin-top: 17px; font-size: 19px;">Winner</h3>
            <p style="text-align: center; font-size: 15px;">
                ${branch.match.winner || 'Not yet defined'}
            </p>
        `;
    }
}

// Close button functionality
document.getElementById('closeParchment').addEventListener('click', () => {
    const teamParchment = document.getElementById('parchment');
    teamParchment.style.display = 'none';
});

export default showParchment;
