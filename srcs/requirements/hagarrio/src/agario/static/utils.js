import { getScene } from './scene.js';
import { stopGameLoop, isGameRunning } from './main.js';
import { cleanup as cleanupPlayers } from './player.js';

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
    // console.log('games:', games);

    // Check if all games are finished/aborted
    const hasActiveGames = games.some(game => 
        game.status !== 'finished' && game.status !== 'aborted'
    );

    if (!hasActiveGames) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="width: 50%; text-align: center; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 5px;">No games available</td>
            <td style="width: 50%; text-align: center; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 5px;">No players</td>
        `;
        gameList.appendChild(row);
        return;
    }

    let index = 0;
    games.forEach((game) => {
        // Ne pas afficher les parties terminées
        if (game.status === 'finished' || game.status === 'aborted') return;
        
        const row = document.createElement('tr');
        const playerNames = Array.isArray(game.players) ? game.players.map(player => player.name).join(', ') : '';
        
        row.innerHTML = `
            <td>${index + 1} - Game 1v1 :</td>
            <td>${playerNames}</td>
        `;
        gameList.appendChild(row);
        index++;
    });
}

export function showGameEndScreen(data) {
    // S'assurer qu'il n'y a pas déjà un overlay
    const existingOverlay = document.querySelector('.game-end-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    
    // Cacher la waiting room pendant l'affichage de l'overlay
    const waitingRoom = document.getElementById('waitingRoom');
    if (waitingRoom) waitingRoom.style.display = 'none';
    
    const overlay = document.createElement('div');
    overlay.className = 'game-end-overlay';
    overlay.style.animation = 'fadeIn 0.5s ease-in';
    document.body.appendChild(overlay);
    
    const content = document.createElement('div');
    content.className = 'game-end-content';
    
    const title = document.createElement('h2');
    title.className = 'game-end-title';
    const isWinner = data.winner === true;
    title.textContent = isWinner ? '🏆 Victory !' : '💀 Defeat';
    title.style.color = isWinner ? '#FFD700' : '#FF6B6B';
    
    const messageText = document.createElement('p');
    messageText.className = 'game-end-message';
    messageText.textContent = data.message;
    
    const menuButton = document.createElement('button');
    menuButton.className = 'menu-button';
    menuButton.textContent = 'Main Menu';
    menuButton.onclick = () => {
        window.parent.postMessage('refresh', '*');
        // Vérifier si le jeu est encore en cours
        if (isGameRunning()) {
            stopGameLoop();
        }
        
        // Animation de sortie
        overlay.style.animation = 'fadeOut 0.5s ease-out forwards';
        overlay.addEventListener('animationend', () => {
            // Nettoyage complet
            cleanupAll();
            
            // Reset de la waiting room
            resetWaitingRoom();
            
            // Retour à la waiting room seulement après la fin de l'animation
            if (waitingRoom) waitingRoom.style.display = 'block';
            const gameContainer = document.getElementById('gameContainer');
            if (gameContainer) gameContainer.style.display = 'none';
            
            // Supprimer l'overlay
            overlay.remove();
        }, { once: true });
    };
    
    content.appendChild(title);
    content.appendChild(messageText);
    content.appendChild(menuButton);
    overlay.appendChild(content);
}

function cleanupAll() {
    // Nettoyer la scène
    cleanupScene();
    
    // Nettoyer les éléments du jeu
    cleanupGameElements();
    
    // Nettoyer l'UI
    cleanupUI();
    
    // Nettoyer les joueurs
    cleanupPlayers();
    
    // Réinitialiser les variables globales si nécessaire
    resetGameState();
}

function cleanupUI() {
    const elementsToRemove = [
        'scoreboard',
        'minimap',
        'speedometer',
        'hotbar'
    ];
    
    elementsToRemove.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.remove();
    });
}

function resetGameState() {
    // Réinitialiser toutes les variables globales du jeu
    window.players = {};
    window.myPlayerId = null;
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

function resetWaitingRoom() {
    // Reset des boutons de matchmaking
    const joinBtn = document.getElementById('joinMatchmakingBtn');
    const leaveBtn = document.getElementById('leaveMatchmakingBtn');
    if (joinBtn) joinBtn.style.display = 'block';
    if (leaveBtn) leaveBtn.style.display = 'none';

    // Reset de la game info
    const gameList = document.getElementById('gameList');
    if (gameList) {
        gameList.innerHTML = '<tr><td colspan="3" style="text-align: center;">No games available</td></tr>';
    }

    // Reset du game info container
    const gameInfoContainer = document.getElementById('gameInfoContainer');
    if (gameInfoContainer) {
        gameInfoContainer.style.display = 'block';
    }
}


