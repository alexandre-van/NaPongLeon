import * as THREE from './three/three.module.js';
import { initScene, render, updateCameraPosition } from './scene.js';
import { updatePlayers, getMyPlayerId, getPlayers } from './player.js';
import { initFood } from './food.js';
import { initNetwork, startGame } from './network.js';
import { initInput } from './input.js';
import { updateUI } from './ui.js';
import { throttle } from './utils.js';

let scene, camera, renderer;
export let mapHeight, mapWidth, max_food;

document.addEventListener('DOMContentLoaded', (event) => {
    if (typeof THREE === 'undefined') {
        console.error('Three.js is not loaded');
        return;
    }
    console.log('Three.js is available:', THREE.REVISION);
    const createGameBtn = document.getElementById('createGameBtn');
    createGameBtn.addEventListener('click', () => {
        startGame();
    });
    initNetwork();
});

export function startGameLoop(initialGameState) {
    mapHeight = initialGameState.mapHeight;
    mapWidth = initialGameState.mapWidth;
    max_food = initialGameState.maxFood;
    ({ scene, camera, renderer } = initScene());
    initFood(initialGameState.food);
    updateUI();
    initInput();
    updatePlayers(initialGameState.players, initialGameState.yourPlayerId);

    function gameLoop() {
        requestAnimationFrame(gameLoop);
        const myPlayer = getPlayers()[getMyPlayerId()];
        if (myPlayer) {
            updateCameraPosition(camera, myPlayer);
        }
        updateUI();
        render(scene, camera, renderer);
    }
    const throttledGameLoop = throttle(gameLoop, 16); // 60 FPS
    throttledGameLoop();
}
