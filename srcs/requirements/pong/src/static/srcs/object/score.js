import * as THREE from '../../.js/three.module.js';
import { scene } from '../scene.js';

let scoreText = null;

function createScore(playerScore = 0, opponentScore = 0) {
    // Remove existing score text if it exists
    if (scoreText) {
        scene.remove(scoreText);
    }

    // Create a canvas to render text
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 128;
    const context = canvas.getContext('2d');

    // Clear canvas and set styling
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.font = 'Bold 60px Arial';
    context.fillStyle = 'white';
    context.textAlign = 'center';

    // Write the score
    context.fillText(`${playerScore} : ${opponentScore}`, canvas.width / 2, 80);

    // Create texture from canvas
    const texture = new THREE.CanvasTexture(canvas);
    
    // Create a sprite with the score
    const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true 
    });
    scoreText = new THREE.Sprite(spriteMaterial);

    // Position the score at the top of the screen
    scoreText.position.set(0, 40, 2);
    scoreText.scale.set(15, 12.5, 1);

    // Add to scene
    scene.add(scoreText);

    return scoreText;
}

// Function to update score
function updateScore(playerScore, opponentScore) {
    createScore(playerScore, opponentScore);
}

export { createScore, updateScore };
