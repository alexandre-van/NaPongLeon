import { getScene } from './scene.js';
import * as THREE from './three/three.module.js';

let players = {};
let myPlayerId = null;
let playerAnimations = new Map();
let animationFrame;

export function updatePlayers(newPlayers, newMyPlayerId) {
    // console.log('Updating players:', newPlayers, 'with myPlayerId:', newMyPlayerId);
    const currentScene = getScene();
    if (!currentScene) return;
    // Mettre à jour les joueurs
    if (newPlayers && Object.keys(newPlayers).length > 0) {
        players = newPlayers;
        if (newMyPlayerId && !myPlayerId) myPlayerId = newMyPlayerId;
        // On met à jour les sprites des joueurs (positions etc)
        Object.values(players).forEach(player => updatePlayerSprite(player, currentScene));
    }
}

function updatePlayerSprite(player, scene) {
    let playerSprite = scene.getObjectByName(`player_${player.id}`);
    let textSprite = scene.getObjectByName(`text_${player.id}`);

    if (!playerSprite) {
        playerSprite = createPlayerSprite(player);
        scene.add(playerSprite);
        playerAnimations.set(player.id, {
            currentSize: player.size,
            targetSize: player.size
        });
    } else {
        const currentAnim = playerAnimations.get(player.id);
        currentAnim.targetSize = player.size;
    }
    if (!textSprite) {
        textSprite = createTextSprite(player);
        scene.add(textSprite);
    }
    playerSprite.position.set(player.x, player.y, 1);
    textSprite.position.set(player.x, player.y, 1.1);
}

export function createPlayerSprite(player) {
    const playerCanvas = document.createElement('canvas');
    const playerContext = playerCanvas.getContext('2d', {
        antialias: true,
        alpha: true
    });
    
    // Augmenter significativement la taille du canvas pour un meilleur rendu
    const size = player.size * 16;
    playerCanvas.width = size;
    playerCanvas.height = size;
    
    // Activer l'anti-aliasing
    playerContext.imageSmoothingEnabled = true;
    playerContext.imageSmoothingQuality = 'high';
    
    function shadeColor(color, percent) {
        const f = parseInt(color.slice(1), 16);
        const t = percent < 0 ? 0 : 255;
        const p = percent < 0 ? percent * -1 : percent;
        const R = f >> 16;
        const G = f >> 8 & 0x00FF;
        const B = f & 0x0000FF;
        const newColor = `#${(0x1000000 + (Math.round((t - R) * p) + R) * 0x10000 + (Math.round((t - G) * p) + G) * 0x100 + (Math.round((t - B) * p) + B)).toString(16).slice(1)}`;
        return newColor;
    }
    
    // Gradient de fond
    const gradient = playerContext.createRadialGradient(
        size/2, size/2, 0,
        size/2, size/2, size/2
    );
    gradient.addColorStop(0, player.color);
    gradient.addColorStop(0.8, player.color);
    gradient.addColorStop(1, shadeColor(player.color, 0.3));

    // Dessiner le cercle avec anti-aliasing amélioré
    playerContext.beginPath();
    playerContext.arc(size/2, size/2, size/2 - 2, 0, 2 * Math.PI);
    playerContext.fillStyle = gradient;
    
    // Ajouter un effet de lissage supplémentaire
    playerContext.shadowColor = player.color;
    playerContext.shadowBlur = 5;
    playerContext.fill();
    
    // Ajouter un contour subtil
    playerContext.strokeStyle = shadeColor(player.color, -0.2);
    playerContext.lineWidth = 2;
    playerContext.stroke();

    const playerTexture = new THREE.CanvasTexture(playerCanvas);
    playerTexture.minFilter = THREE.LinearMipmapLinearFilter;
    playerTexture.magFilter = THREE.LinearFilter;
    playerTexture.anisotropy = 16;

    const playerMaterial = new THREE.SpriteMaterial({ 
        map: playerTexture,
        transparent: true,
        depthTest: false,
        depthWrite: false,
        // renderOrder: 0
    });

    const playerSprite = new THREE.Sprite(playerMaterial);
    playerSprite.name = `player_${player.id}`;
    playerSprite.scale.set(player.size * 2, player.size * 2, 1);
    
    return playerSprite;
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
        text = text.substring(0, 11) + '...';
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
        depthTest: false,
        depthWrite: false,
        // renderOrder: 1
    });
    const textSprite = new THREE.Sprite(textMaterial);
    textSprite.name = `text_${player.id}`;
    textSprite.scale.set(120 * scaleFactor, 30 * scaleFactor, 1.1);
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
    
    if (playerAnimations.has(playerId)) {
        const playerAnim = playerAnimations.get(playerId);
        if (playerAnim.animation) {
            cancelAnimationFrame(playerAnim.animation);
        }
        playerAnimations.delete(playerId);
    }
}

export function getPlayers() {
    return players;
}

export function getMyPlayerId() {
    return myPlayerId;
}

function updateAnimations() {
    const currentScene = getScene();
    if (!currentScene) return;

    playerAnimations.forEach((anim, playerId) => {
        if (anim.targetSize && anim.targetSize !== anim.currentSize) {
            const playerSprite = currentScene.getObjectByName(`player_${playerId}`);
            const textSprite = currentScene.getObjectByName(`text_${playerId}`);
            if (!playerSprite) return;

            const delta = (anim.targetSize - anim.currentSize) * 0.1;
            anim.currentSize += delta;
            if (Math.abs(anim.targetSize - anim.currentSize) < 0.01) {
                anim.currentSize = anim.targetSize;
                anim.targetSize = null;
            }
            playerSprite.scale.set(anim.currentSize * 2, anim.currentSize * 2, 1);
            if (textSprite) {
                const textScale = anim.currentSize / 40;
                textSprite.scale.set(120 * textScale, 30 * textScale, 1.1);
            }
        }
    });
    animationFrame = requestAnimationFrame(updateAnimations);
}

export function initPlayers() {
    updateAnimations();
}

export function cleanup() {
    // Arrêter toutes les animations en cours
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
    }
    
    // Nettoyer les animations
    playerAnimations.clear();
    
    // Nettoyer les références aux joueurs
    players = {};
    myPlayerId = null;
}
