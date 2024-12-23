import * as THREE from './three/three.module.js';
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
			return;
        } else {
            isInMatchmaking = false;
			updateButtons();
        }
	})
    leaveBtn.addEventListener('click', async () => {
		const success = await stopMatchmaking();
        if (success) {
			isInMatchmaking = false;
            updateButtons();
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
    updatePlayers(initialGameState.players, initialGameState.yourPlayerId);
    initPlayers();
    createHotbar();
    function gameLoop() {
        requestAnimationFrame(gameLoop);
        const myPlayer = getPlayers()[getMyPlayerId()];
        if (myPlayer) {
            updateCameraPosition(camera, myPlayer);
        }
        updateUI();
        render(scene, camera, renderer);
    }
    window.addEventListener('beforeunload', () => {
        cleanup();
    });
    const throttledGameLoop = throttle(gameLoop, 16);// 60 FPS
    throttledGameLoop();
}
