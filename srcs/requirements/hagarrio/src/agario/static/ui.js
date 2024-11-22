import { getPlayers } from './player.js';
import { getFood } from './food.js';
import { getMyPlayerId } from './player.js';
import { mapHeight, mapWidth } from './main.js';

const minimapCanvas = document.getElementById('minimap');
const minimapCtx = minimapCanvas.getContext('2d');
const minimapSize = 175;
minimapCanvas.width = minimapSize;
minimapCanvas.height = minimapSize;

export function updateUI() {
    updateScoreboard();
    updateMinimap();
    updateSpeedometer();
}

export function updateScoreboard() {
    const scoreboard = document.getElementById('scoreboard');
    const players = getPlayers();
    const sortedPlayers = Object.values(players).sort((a, b) => b.score - a.score);
    let scoreboardHTML = '<h3>Scoreboard</h3>';
    scoreboardHTML += '<table><tr><th>Name</th><th>Score</th></tr>';
    sortedPlayers.forEach(player => {
        const displayName = player.name.length > 10 ? player.name.substring(0, 10) + '...' : player.name;
        scoreboardHTML += `<tr><td> ${displayName} </td><td> ${player.score} </td></tr>`;
    });
    scoreboardHTML += '</table>';
    scoreboard.innerHTML = scoreboardHTML;
}

export function updateMinimap() {
    const players = getPlayers();
    const food = getFood();
    // console.log('in updateMinimap, mapheight', mapHeight, 'mapWidth', mapWidth);

    minimapCtx.clearRect(0, 0, minimapSize, minimapSize);

    // Dessiner le fond
    minimapCtx.fillStyle = 'rgba(0, 0, 0, 1)';
    minimapCtx.fillRect(0, 0, minimapSize, minimapSize);
    
    // Dessiner les axes
    minimapCtx.strokeStyle = 'rgba(255, 255, 255, 0.60)';
    minimapCtx.beginPath();
    minimapCtx.moveTo(0, minimapSize / 2);
    minimapCtx.lineTo(minimapSize, minimapSize / 2);
    minimapCtx.moveTo(minimapSize / 2, 0);
    minimapCtx.lineTo(minimapSize / 2, minimapSize);
    minimapCtx.stroke();
    
    // Dessiner uniquement le joueur actuel
    const myPlayerId = getMyPlayerId();
    if (myPlayerId && players[myPlayerId]) {
        const player = players[myPlayerId];
        const x = (player.x / mapWidth) * minimapSize;
        const y = ((mapHeight - player.y) / mapHeight) * minimapSize;//Inverser l'axe Y
        minimapCtx.fillStyle = 'red';
        minimapCtx.beginPath();
        minimapCtx.arc(x, y, 3, 0, 2 * Math.PI);
        minimapCtx.fill();
    }

    // Dessiner la nourriture
    if (Array.isArray(food) && food.length > 0) {
        food.forEach(f => {
            const x = (f.x / mapWidth) * minimapSize;
            const y = ((mapHeight - f.y) / mapHeight) * minimapSize;//Inverser l'axe Y
            if (f.type === 'epic') {
                minimapCtx.fillStyle = f.color;
                minimapCtx.beginPath();
                minimapCtx.arc(x, y, 1.5, 0, 2 * Math.PI);
                minimapCtx.fill();
            } else {
                minimapCtx.fillStyle = f.type === 'rare' ? f.color : 'green';
                minimapCtx.beginPath();
                minimapCtx.arc(x, y, 1, 0, 2 * Math.PI);
                minimapCtx.fill();
            }
        });
    }
}

function updateSpeedometer() {
    const speedometer = document.getElementById('speedometer');
    const myPlayerId = getMyPlayerId();
    const players = getPlayers();
    
    if (myPlayerId && players[myPlayerId]) {
        const speed = players[myPlayerId].current_speed || 0;
        speedometer.textContent = `Speed: ${speed}`;
    }
}
