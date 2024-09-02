import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.136.0/build/three.module.js';
import scene from './scene.js';
import { borderTop, borderBottom, borderLeft, borderRight, arenaLength, arenaWidth, wallWidth } from './border.js';
import { checkCollisions } from './collisions.js';
import { getTimer } from './timer.js';

const	ballRay = 1;

let ballSpeed = 5;
let ballDirX = 1;
let ballDirY = 1;
let timer = getTimer() / 100;


const geometry = new THREE.SphereGeometry(ballRay, 32, 32);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const ball = new THREE.Mesh(geometry, material);

ball.position.set(0, 0, 1);
ball.castShadow = false;
scene.add(ball);

function reverseBallDirX() {
	ballDirX *= -1;
}

function reverseBallDirY() {
	ballDirY *= -1;
}

function updateBallPosition() {
	;
}

export { ball, updateBallPosition, reverseBallDirX, reverseBallDirY };