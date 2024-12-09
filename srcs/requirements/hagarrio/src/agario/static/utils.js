import { joinGame } from './network.js';

export function throttle(func, limit) {
    let lastFunc;
    let lastRan;
    return function() {
        const context = this;
        const args = arguments;
        if (!lastRan) {
            func.apply(context, args);
            lastRan = Date.now();
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(function() {
                if ((Date.now() - lastRan) >= limit) {
                    func.apply(context, args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    }
}

export function getRandomColor() {
    return '#' + Math.floor(Math.random()*16777215).toString(16);
}

export function updateGameInfo(data) {
    const gameList = document.getElementById('gameList');
    if (!gameList) return;
    gameList.innerHTML = '';

    const games = Array.isArray(data.games) ? data.games : [];

    if (games.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="3" style="text-align: center;">No games available</td>';
        gameList.appendChild(row);
        return;
    }

    games.forEach((game, index) => {
        const row = document.createElement('tr');
        const playerNames = Array.isArray(game.players) ? game.players.map(player => player.name).join(', ') : '';
        
        row.innerHTML = `
            <td>Game ${index + 1}</td>
            <td>${playerNames}</td>
            <td>
                <button class="joinGameBtn" data-gameid="${game.gameId}">
                    ${game.status === 'custom' ? 'Join' : 'Watch'}
                </button>
            </td>
        `;
        gameList.appendChild(row);
    });

    console.log('Apres Game Info');
    // Ajouter les écouteurs d'événements pour les boutons
    document.querySelectorAll('.joinGameBtn').forEach(button => {
        button.addEventListener('click', () => {
            const gameId = button.dataset.gameid;
            joinGame(gameId);
        });
    });
}

export function showGameOverMessage(message) {
    const overlay = document.createElement('div');
    overlay.className = 'game-over-overlay';
    
    const content = document.createElement('div');
    content.className = 'game-over-content';
    
    const title = document.createElement('div');
    title.className = 'game-over-title';
    title.textContent = 'GAME OVER';
    
    const messageText = document.createElement('div');
    messageText.className = 'game-over-score';
    messageText.textContent = message;
    
    content.appendChild(title);
    content.appendChild(messageText);
    overlay.appendChild(content);
    document.body.appendChild(overlay);
    
    // Attendre 3 secondes avant de rediriger vers la waiting room
    setTimeout(() => {
        overlay.style.animation = 'fadeOut 0.5s ease-out';
        overlay.addEventListener('animationend', () => {
            if (overlay && overlay.parentNode) {
                overlay.remove();
                // Afficher la waiting room
                document.getElementById('waitingRoom').style.display = 'flex';
                document.getElementById('gameContainer').style.display = 'none';
            }
        });
    }, 3000);
}
