import { getPlayers } from './player.js';
import { getFood } from './food.js';
import { getMyPlayerId } from './player.js';
import { mapHeight, mapWidth } from './main.js';
import { getPowerUps } from './powers.js';

const minimapCanvas = document.getElementById('minimap');
const minimapCtx = minimapCanvas.getContext('2d');
const minimapSize = 175;
minimapCanvas.width = minimapSize;
minimapCanvas.height = minimapSize;

export function initUI() {
    updateScoreboard();
    initMinimap();
    updateSpeedometer();
}

export function updateUI() {
    updateScoreboard();
    updateMinimap();
    updateSpeedometer();
}

export function updateScoreboard() {
    const scoreboard = document.getElementById('scoreboard');
    const players = getPlayers();
    const myPlayerId = getMyPlayerId();
    const sortedPlayers = Object.values(players).sort((a, b) => b.score - a.score);
    
    let scoreboardHTML = '<h3>Scoreboard</h3>';
    scoreboardHTML += '<table><tr><th>Name</th><th>Score</th></tr>';
    
    sortedPlayers.forEach(player => {
        const displayName = player.name.length > 10 ? player.name.substring(0, 10) + '...' : player.name;
        const isCurrentPlayer = player.id === myPlayerId;
        const rowStyle = isCurrentPlayer ? 'style="color: #00BFFF;"' : 'style="color: white;"';
        
        scoreboardHTML += `<tr ${rowStyle}><td>${displayName}</td><td>${player.score}</td></tr>`;
    });
    
    scoreboardHTML += '</table>';
    scoreboard.innerHTML = scoreboardHTML;
}

export function initMinimap() {
    const players = getPlayers();
    const food = getFood();
    // console.log('in updateMinimap, mapheight', mapHeight, 'mapWidth', mapWidth);

    minimapCtx.clearRect(0, 0, minimapSize, minimapSize);

    // Dessiner le fond
    minimapCtx.fillStyle = 'rgba(0, 0, 0, 1)';
    minimapCtx.fillRect(0, 0, minimapSize, minimapSize);
    
    // Dessiner les axes
    minimapCtx.strokeStyle = 'rgba(255, 255, 255, 0.65)';
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
        const y = ((mapHeight - player.y) / mapHeight) * minimapSize;
        
        // Ajuster le calcul pour une meilleure proportion par rapport à la taille réelle
        const minimapScaleFactor = minimapSize / mapWidth; // Facteur d'échelle entre la minimap et la carte
        const minimapRadius = Math.max(2, Math.sqrt(player.size) * minimapScaleFactor);
        
        // Ajouter un effet de halo pour mieux voir l'avatar
        minimapCtx.fillStyle = 'rgba(255, 0, 0, 0.3)';
        minimapCtx.beginPath();
        minimapCtx.arc(x, y, minimapRadius + 1, 0, 2 * Math.PI);
        minimapCtx.fill();
        
        // Dessiner l'avatar
        minimapCtx.fillStyle = 'red';
        minimapCtx.beginPath();
        minimapCtx.arc(x, y, minimapRadius, 0, 2 * Math.PI);
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
            minimapCtx.arc(x, y, 2, 0, 2 * Math.PI);
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

export function updateMinimap() {
    const players = getPlayers();
    const food = getFood();
    const powerUps = getPowerUps();
    
    minimapCtx.clearRect(0, 0, minimapSize, minimapSize);

    // Dessiner la nourriture d'abord
    if (Array.isArray(food) && food.length > 0) {
        food.forEach(f => {
            const x = (f.x / mapWidth) * minimapSize;
            const y = ((mapHeight - f.y) / mapHeight) * minimapSize;//Inverser l'axe Y
            if (f.type === 'epic') {
                minimapCtx.fillStyle = f.color;
                minimapCtx.beginPath();
                minimapCtx.arc(x, y, 2, 0, 2 * Math.PI);
                minimapCtx.fill();
            } else {
                minimapCtx.fillStyle = f.type === 'rare' ? f.color : 'green';
                minimapCtx.beginPath();
                minimapCtx.arc(x, y, 1, 0, 2 * Math.PI);
                minimapCtx.fill();
            }
        });
    }

    // Dessiner les power-ups ensuite
    if (powerUps && powerUps.length > 0) {
        powerUps.forEach(powerUp => {
            const x = (powerUp.x / mapWidth) * minimapSize;
            const y = ((mapHeight - powerUp.y) / mapHeight) * minimapSize;
            minimapCtx.fillStyle = powerUp.properties.color;
            minimapCtx.beginPath();
            minimapCtx.arc(x, y, 3, 0, 2 * Math.PI);
            minimapCtx.fill();
            
            // Ajouter un effet de brillance
            minimapCtx.strokeStyle = 'white';
            minimapCtx.lineWidth = 1;
            minimapCtx.stroke();
        });
    }

    // Dessiner l'avatar du joueur en dernier pour qu'il soit au premier plan
    const myPlayerId = getMyPlayerId();
    if (myPlayerId && players[myPlayerId]) {
        const player = players[myPlayerId];
        const x = (player.x / mapWidth) * minimapSize;
        const y = ((mapHeight - player.y) / mapHeight) * minimapSize;
        
        const scaleFactor = 0.5;
        const minimapRadius = Math.max(3, Math.sqrt(player.size) / 2 * scaleFactor);
        
        // Ajouter un effet de halo pour mieux voir l'avatar
        minimapCtx.fillStyle = 'rgba(255, 0, 0, 0.3)';
        minimapCtx.beginPath();
        minimapCtx.arc(x, y, minimapRadius + 1, 0, 2 * Math.PI);
        minimapCtx.fill();
        
        // Dessiner l'avatar
        minimapCtx.fillStyle = 'red';
        minimapCtx.beginPath();
        minimapCtx.arc(x, y, minimapRadius, 0, 2 * Math.PI);
        minimapCtx.fill();
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
