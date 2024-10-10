const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const socket = new WebSocket('ws://' + window.location.host + '/ws/game/');

socket.onmessage = function(e) {
    const gameState = JSON.parse(e.data);
    drawGame(gameState);
};

function updateGame() {
    if (player) {
        socket.send(JSON.stringify({
            'type': 'move',
            'x': player.x,
            'y': player.y
        }));
    }
}

function drawGame(gameState) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Dessiner la nourriture
    gameState.food.forEach(food => {
        ctx.fillStyle = 'green';
        ctx.beginPath();
        ctx.arc(food.x, food.y, 5, 0, 2 * Math.PI);
        ctx.fill();
    });

    // Dessiner les joueurs
    gameState.players.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = 'black';
        ctx.fillText(p.name, p.x, p.y);
    });
}

function gameLoop() {
    updateGame();
    drawGame();
    requestAnimationFrame(gameLoop);
}

gameLoop();
