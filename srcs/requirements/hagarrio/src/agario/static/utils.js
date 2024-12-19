import { joinGame } from './network.js';
import { getScene } from './scene.js';
import { stopGameLoop } from './main.js';
import { cleanup as cleanupPlayers, getMyPlayerId } from './player.js';

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

export function showGameEndScreen(data) {
    // 1. Nettoyage commun
    stopGameLoop();
    cleanupPlayers();
    cleanupScene();
    cleanupGameElements();

    // 2. Déterminer le type d'écran à afficher
    const myId = getMyPlayerId();
    const isWinner = data.winner === myId;

    // 3. Créer l'overlay approprié
    const overlay = document.createElement('div');
    overlay.className = isWinner ? 'game-win-overlay' : 'game-over-overlay';
    overlay.style.animation = 'fadeIn 0.5s ease-in';
    
    const content = document.createElement('div');
    content.className = isWinner ? 'game-win-content' : 'game-over-content';
    
    const title = document.createElement('div');
    title.className = isWinner ? 'game-win-title' : 'game-over-title';
    
    const messageText = document.createElement('div');
    messageText.className = isWinner ? 'game-win-score' : 'game-over-score';

    // 4. Personnaliser le contenu selon le cas
    if (data.reason === 'forfeit') {
        if (isWinner) {
            title.textContent = 'VICTOIRE PAR FORFAIT!';
            messageText.textContent = `Score final: ${data.winner_score}`;
        }
    } else if (data.reason === 'victory') {
        if (isWinner) {
            title.textContent = 'VICTOIRE!';
            messageText.textContent = `Vous avez gagné avec un score de ${data.winner_score}!`;
        } else {
            title.textContent = 'DÉFAITE';
            messageText.textContent = `Vous avez perdu avec un score de ${data.loser_score}`;
        }
    }
    
    // 5. Ajouter des détails supplémentaires si disponibles
    if (data.message) {
        const additionalInfo = document.createElement('div');
        additionalInfo.className = isWinner ? 'game-win-message' : 'game-over-message';
        additionalInfo.textContent = data.message;
        content.appendChild(additionalInfo);
    }
    
    content.appendChild(title);
    content.appendChild(messageText);
    overlay.appendChild(content);
    document.body.appendChild(overlay);
    
    // 6. Retour à la waiting room après délai
    setTimeout(() => {
        overlay.style.animation = 'fadeOut 0.5s ease-out forwards';
        overlay.addEventListener('animationend', () => {
            if (overlay && overlay.parentNode) {
                overlay.remove();
                const waitingRoom = document.getElementById('waitingRoom');
                if (waitingRoom) {
                    waitingRoom.style.display = 'block';
                }
            }
        }, { once: true });
    }, 3000);
}

function cleanupScene() {
    const currentScene = getScene();
    if (currentScene) {
        while(currentScene.children.length > 0) { 
            const object = currentScene.children[0];
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
            if (object.geometry) {
                object.geometry.dispose();
            }
            currentScene.remove(object);
        }
    }
}

function cleanupGameElements() {
    const gameContainer = document.getElementById('gameContainer');
    const hotbar = document.getElementById('hotbar');
    const renderer = document.querySelector('canvas');
    
    if (hotbar) hotbar.remove();
    if (renderer) renderer.remove();
    if (gameContainer) {
        gameContainer.style.display = 'none';
        gameContainer.innerHTML = '';
    }
}


