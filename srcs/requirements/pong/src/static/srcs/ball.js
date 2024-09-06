import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.136.0/build/three.module.js';
import scene from './scene.js';

const ballRad = 1;
const geometry = new THREE.SphereGeometry(ballRad, 32, 32);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const ball = new THREE.Mesh(geometry, material);

ball.position.set(0, 0, 1);
ball.castShadow = false;
scene.add(ball);

function updateBallPosition(position) {
	ball.position.set(position.x, position.y, 1);
}

export { ball, updateBallPosition };