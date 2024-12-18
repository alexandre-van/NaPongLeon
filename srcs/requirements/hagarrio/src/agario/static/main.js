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

document.addEventListener('DOMContentLoaded', () => {
	const joinBtn = document.getElementById('joinMatchmakingBtn');
	const leaveBtn = document.getElementById('leaveMatchmakingBtn');

	initNetwork()

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
	joinBtn.addEventListener('click', () => {
		isInMatchmaking = true;
		if (startMatchmaking())
			updateButtons();
		console.log('Joining matchmaking...');
	});
	leaveBtn.addEventListener('click', () => {
		isInMatchmaking = false;
		if (stopMatchmaking())
			updateButtons();
		console.log('Leaving matchmaking...');
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
