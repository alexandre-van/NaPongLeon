// import * as THREE from './three/three.module.js';
import { initScene, render, updateCameraPosition } from './scene.js';
import { initPlayers, updatePlayers, getMyPlayerId, getPlayers } from './player.js';
import { initFood } from './food.js';
import { initNetwork, startMatchmaking, stopMatchmaking } from './network.js';
import { initInput } from './input.js';
import { initUI, updateUI } from './ui.js';
import { throttle } from './utils.js';
import { createHotbar } from './hotbar.js';

let scene, camera, renderer;
export let mapHeight, mapWidth, max_food;
let gameLoopId = null;

document.addEventListener('DOMContentLoaded', async () => {
    const joinBtn = document.getElementById('joinMatchmakingBtn');
    const leaveBtn = document.getElementById('leaveMatchmakingBtn');

    initNetwork(); // Suppose que initNetwork est aussi async

    let isInMatchmaking = false;

    function updateButtons() {
        if (isInMatchmaking) {
            joinBtn.style.display = 'none';
            leaveBtn.style.display = 'block';
        } else {
            joinBtn.style.display = 'block';
            leaveBtn.style.display = 'none';
        }
    }

    joinBtn.addEventListener('click', async () => {
		isInMatchmaking = true;
		updateButtons();
		const success = await startMatchmaking();
        if (success) {
			console.log('Successfully entered matchmaking queue.');
        } else {
            isInMatchmaking = false;
			updateButtons();
        }
	});

    leaveBtn.addEventListener('click', async () => {
		isInMatchmaking = false;
		updateButtons();
        const success = await stopMatchmaking();
        if (success) {
            console.log('Left the matchmaking queue and disconnected.');
        } else {
            console.log('Failed to leave the matchmaking queue.');
        }
    });

    updateButtons();
});

export function startGameLoop(initialGameState) {
    mapHeight = initialGameState.mapHeight;
    mapWidth = initialGameState.mapWidth;
    max_food = initialGameState.maxFood;
    ({ scene, camera, renderer } = initScene());
    initFood(initialGameState.food);
    initUI();
    initInput();
    // console.log("yourPlayerId:", initialGameState.yourPlayerId);
    updatePlayers(initialGameState.players, initialGameState.yourPlayerId);
    initPlayers();
    createHotbar();
    function gameLoop() {
        gameLoopId = requestAnimationFrame(gameLoop);
        const myPlayer = getPlayers()[getMyPlayerId()];
        if (myPlayer) {
            updateCameraPosition(camera, myPlayer);
        }
        updateUI();
        render(scene, camera, renderer);
    }
    const throttledGameLoop = throttle(gameLoop, 8);// 120 FPS
    throttledGameLoop();
}

export function isGameRunning() {
    return gameLoopId !== null;
}

export function stopGameLoop() {
    if (gameLoopId !== null) {
        cancelAnimationFrame(gameLoopId);
        gameLoopId = null;
    }
}
