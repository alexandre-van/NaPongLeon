const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const socket = new WebSocket('ws://' + window.location.host + '/ws/game/');

let players = {};
let food = [];
let myPlayerId = null;
let keys = { w: false, a: false, s: false, d: false };

socket.onmessage = function(e) {
    const gameState = JSON.parse(e.data);
    players = gameState.players;
    food = gameState.food;
    if (gameState.yourPlayerId) {
        myPlayerId = gameState.yourPlayerId;
    }
};

function updateGame() {
    if (myPlayerId && players[myPlayerId]) {
        let dx = 0, dy = 0;
        if (keys.w) dy -= 5;
        if (keys.s) dy += 5;
        if (keys.a) dx -= 5;
        if (keys.d) dx += 5;

        if (dx !== 0 || dy !== 0) {
            const newX = Math.max(0, Math.min(canvas.width, players[myPlayerId].x + dx));
            const newY = Math.max(0, Math.min(canvas.height, players[myPlayerId].y + dy));

            socket.send(JSON.stringify({
                'type': 'move',
                'x': newX,
                'y': newY
            }));
        }
    }
}

function drawGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Dessiner la nourriture
    food.forEach(f => {
        ctx.fillStyle = 'green';
        ctx.beginPath();
        ctx.arc(f.x, f.y, 5, 0, 2 * Math.PI);
        ctx.fill();
    });

    // Dessiner les joueurs
    Object.values(players).forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = 'black';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        let displayName = p.name.length > 8 ? p.name.substring(0, 8) + '.' : p.name;
        ctx.fillText(displayName, p.x, p.y);
    });
}

function gameLoop() {
    updateGame();
    drawGame();
    requestAnimationFrame(gameLoop);
}

document.addEventListener('keydown', (event) => {
    if (event.key === 'w' || event.key === 'W') keys.w = true;
    if (event.key === 'a' || event.key === 'A') keys.a = true;
    if (event.key === 's' || event.key === 'S') keys.s = true;
    if (event.key === 'd' || event.key === 'D') keys.d = true;
});

document.addEventListener('keyup', (event) => {
    if (event.key === 'w' || event.key === 'W') keys.w = false;
    if (event.key === 'a' || event.key === 'A') keys.a = false;
    if (event.key === 's' || event.key === 'S') keys.s = false;
    if (event.key === 'd' || event.key === 'D') keys.d = false;
});

gameLoop();
