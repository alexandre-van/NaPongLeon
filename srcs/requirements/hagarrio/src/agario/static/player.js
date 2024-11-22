import { getScene } from './scene.js';
import { getRandomColor } from './utils.js';
import * as THREE from './three/three.module.js';

let players = {};
let myPlayerId = null;

export function updatePlayers(newPlayers, newMyPlayerId) {
    const currentScene = getScene();
    if (!currentScene) return;

    // Supprimer les joueurs qui ne sont plus présents
    Object.keys(players).forEach(playerId => {
        if (!newPlayers[playerId]) {
            const playerSprite = currentScene.getObjectByName(`player_${playerId}`);
            const textSprite = currentScene.getObjectByName(`text_${playerId}`);
            
            if (playerSprite) {
                playerSprite.material.dispose();
                playerSprite.removeFromParent();
            }
            if (textSprite) {
                textSprite.material.dispose();
                textSprite.removeFromParent();
            }
        }
    });

    // Mettre à jour les joueurs
    if (newPlayers && Object.keys(newPlayers).length > 0) {
        players = newPlayers;
        if (newMyPlayerId && !myPlayerId) myPlayerId = newMyPlayerId;
        Object.values(players).forEach(player => updatePlayerSprite(player, currentScene));
    }
}

export function createPlayerSprite(player) {
    const playerCanvas = document.createElement('canvas');
    const playerContext = playerCanvas.getContext('2d');
    const size = player.size * 2;
    playerCanvas.width = size;
    playerCanvas.height = size;
    
    // Gradient de fond
    const gradient = playerContext.createRadialGradient(
        size/2, size/2, 0,
        size/2, size/2, size/2
    );
    gradient.addColorStop(0, player.color || getRandomColor());
    gradient.addColorStop(0.8, player.color || getRandomColor());
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0.3)');

    // Cercle principal
    playerContext.beginPath();
    playerContext.arc(size/2, size/2, size/2, 0, 2 * Math.PI);
    playerContext.fillStyle = gradient;
    playerContext.fill();

    // Effet de brillance
    const highlight = playerContext.createRadialGradient(
        size/3, size/3, 0,
        size/3, size/3, size/3
    );
    highlight.addColorStop(0, 'rgba(255, 255, 255, 0.4)');
    highlight.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    playerContext.beginPath();
    playerContext.arc(size/3, size/3, size/3, 0, 2 * Math.PI);
    playerContext.fillStyle = highlight;
    playerContext.fill();

    // // Bordure
    // playerContext.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    // playerContext.lineWidth = size/20;
    // playerContext.stroke();

    const playerTexture = new THREE.CanvasTexture(playerCanvas);
    playerTexture.minFilter = THREE.LinearFilter;
    playerTexture.magFilter = THREE.LinearFilter;
    const playerMaterial = new THREE.SpriteMaterial({ 
        map: playerTexture,
        transparent: true
    });
    const playerSprite = new THREE.Sprite(playerMaterial);
    playerSprite.name = `player_${player.id}`;
    playerSprite.scale.set(player.size * 2, player.size * 2, 1);
    
    return playerSprite;
}

function updatePlayerSprite(player, scene) {
    let playerSprite = scene.getObjectByName(`player_${player.id}`);
    let textSprite = scene.getObjectByName(`text_${player.id}`);
    
    if (!playerSprite) {
        playerSprite = createPlayerSprite(player);
        scene.add(playerSprite);
    }
    if (!textSprite) {
        textSprite = createTextSprite(player);
        scene.add(textSprite);
    }
    
    playerSprite.position.set(player.x, player.y, 0);
    playerSprite.scale.set(player.size * 2, player.size * 2, 1);
    

    const textScale = player.size / 40;//Math.min(7, Math.max(1, player.size / 20));
    textSprite.position.set(player.x, player.y, 0.1);
    textSprite.scale.set(120 * textScale, 30 * textScale, 1);
}

function createTextSprite(player) {
    const textCanvas = document.createElement('canvas');
    const textContext = textCanvas.getContext('2d');
    const baseTextSize = 70;
    
    const scaleFactor = player.size / 40;//Math.min(7, Math.max(1, player.size / 20));
    const actualTextSize = baseTextSize * scaleFactor;
    
    textCanvas.width = actualTextSize * 8;
    textCanvas.height = actualTextSize * 2;

    textContext.font = `bold ${actualTextSize}px Arial`;
    textContext.fillStyle = 'white';
    textContext.strokeStyle = 'rgba(0, 0, 0, 0.8)';
    textContext.lineWidth = actualTextSize / 15;
    textContext.textAlign = 'center';
    textContext.textBaseline = 'middle';

    let text = player.name;
    const maxWidth = textCanvas.width * 0.8;
    if (textContext.measureText(text).width > maxWidth) {
        text = text.substring(0, 15) + '...';
    }

    // Effet d'ombre portée
    textContext.shadowColor = 'rgba(0, 0, 0, 0.5)';
    textContext.shadowBlur = actualTextSize / 10;
    textContext.shadowOffsetX = actualTextSize / 20;
    textContext.shadowOffsetY = actualTextSize / 20;

    textContext.strokeText(text, textCanvas.width / 2, textCanvas.height / 2);
    textContext.fillText(text, textCanvas.width / 2, textCanvas.height / 2);

    const textTexture = new THREE.CanvasTexture(textCanvas);
    textTexture.minFilter = THREE.LinearFilter;
    textTexture.magFilter = THREE.LinearFilter;
    const textMaterial = new THREE.SpriteMaterial({ 
        map: textTexture,
        transparent: true,
        depthTest: false
    });
    const textSprite = new THREE.Sprite(textMaterial);
    textSprite.name = `text_${player.id}`;
    
    return textSprite;
}

export function removePlayer(playerId) {
    const currentScene = getScene();
    if (!currentScene) return;
    
    const playerSprite = currentScene.getObjectByName(`player_${playerId}`);
    const textSprite = currentScene.getObjectByName(`text_${playerId}`);
    
    if (playerSprite) {
        if (playerSprite.material.map) {
            playerSprite.material.map.dispose();
        }
        playerSprite.material.dispose();
        playerSprite.removeFromParent();
    }
    if (textSprite) {
        if (textSprite.material.map) {
            textSprite.material.map.dispose();
        }
        textSprite.material.dispose();
        textSprite.removeFromParent();
    }
    
    if (players[playerId]) {
        delete players[playerId];
    }
}

export function getPlayers() {
    return players;
}

export function getMyPlayerId() {
    return myPlayerId;
}
