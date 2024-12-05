function showParchment(branch) {
    // Récupérer l'élément du parchemin et le rendre visible
    const parchmentDiv = document.getElementById('parchment');
    parchmentDiv.style.display = 'block';

    // Récupérer les informations des équipes et du banc
    const team1 = branch.match ? branch.match.team1 : null;
    const team2 = branch.match ? branch.match.team2 : null;
    const bench = branch.bench ? branch.bench : null; // Supposons que "bench" contient un objet "team"
	let context = '';
	switch (branch.level) {
        case 0:
            context = 'Winner';
            break;
        case 1:
            context = 'Final';
            break;
        case 2:
            context = 'Semi-Final';
            break;
		case 3:
			context = "Quarter-Final";
        default:
            break;
    }

    // Construire le contenu du parchemin avec les informations détaillées
    const branchInfoDiv = document.getElementById('branchInfo');
    branchInfoDiv.style.fontFamily = `'Dancing Script', cursive`; // Police style script
    branchInfoDiv.style.lineHeight = '1.2'; // Réduction de l'espacement entre les lignes

    // Vérifier les cas possibles
    if (!branch.match && !bench) {
        // Cas 1 : Cellule vide
        branchInfoDiv.innerHTML = `
            <h2 style="margin: 0; text-align: center; font-size: 28px;">Cell ${branch.id}</h2>
            <p style="text-align: center; font-size: 18px; margin-top: 10px;">Level: ${branch.level} (${context})</p>
            <p style="text-align: center; font-size: 20px; margin-top: 20px;">This cell is empty.</p>
        `;
    } else if (bench && !branch.match) {
        // Cas 2 : Une équipe est sur le banc
        branchInfoDiv.innerHTML = `
            <h2 style="margin: 0; text-align: center; font-size: 28px;">Cell ${branch.id}</h2>
			<p style="text-align: center; font-size: 18px; margin-top: 10px;">Level: ${branch.level} (${context})</p>
            <h3 style="text-align: center; margin-top: 20px; font-size: 24px;">Bench</h3>
            <div style="text-align: center; font-size: 20px; margin-top: 10px;">
                <p style="font-weight: bold; margin: 0;">Team: ${bench.name}</p>
            </div>
        `;
    } else {
        // Cas 3 : Match en cours
        branchInfoDiv.innerHTML = `
            <h2 style="margin: 0; text-align: center; font-size: 28px;">Cell ${branch.id}</h2>
			<p style="text-align: center; font-size: 18px; margin-top: 10px;">Level: ${branch.level} (${context})</p>
            <h3 style="text-align: center; margin-top: 20px; font-size: 24px;">Match</h3>
            <p style="text-align: center; font-size: 22px; font-weight: bold;">
                ${team1.name} <span style="font-size: 24px; font-weight: normal;">vs</span> ${team2.name}
            </p>
        
            <p style="text-align: center; margin: 10px 0; font-size: 18px;">
                <strong>State:</strong> ${branch.match.status}
            </p>
        
            <h3 style="text-align: center; margin-top: 25px; font-size: 22px;">Score</h3>
            <div style="display: flex; justify-content: center; align-items: center; font-size: 20px; margin: 15px 0;">
                <!-- Score Team 1 -->
                <div style="text-align: center; margin-right: 20px;">
                    <p style="font-weight: bold; margin: 0;">${team1.name}</p>
                    <p style="margin: 5px 0; font-style: italic;">(Future value)</p>
                    <p style="font-weight: bold; margin: 0;">${branch.match.score[team1.name] || '0'}</p>
                </div>
                <!-- Separating Line -->
                <div style="border-left: 2px solid #5D4037; height: 60px; margin: 0 20px;"></div>
                <!-- Score Team 2 -->
                <div style="text-align: center; margin-left: 20px;">
                    <p style="font-weight: bold; margin: 0;">${team2.name}</p>
                    <p style="margin: 5px 0; font-style: italic;">(Future value)</p>
                    <p style="font-weight: bold; margin: 0;">${branch.match.score[team2.name] || '0'}</p>
                </div>
            </div>
        
            <h3 style="text-align: center; margin-top: 25px; font-size: 22px;">Winner</h3>
            <p style="text-align: center; font-size: 18px;">
                ${branch.match.winner || 'Not yet defined'}
            </p>
        `;
    }
}

export default showParchment;
