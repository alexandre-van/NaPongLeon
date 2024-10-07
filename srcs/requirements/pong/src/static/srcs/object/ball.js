import * as THREE from '../../js/three.module.js';

import scene from '../scene.js';

let ball = null;

function ball_init(ball_data) {
	const geometry = new THREE.SphereGeometry(ball_data.rad, 32, 32);
	const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
	ball = new THREE.Mesh(geometry, material);

	ball.position.set(ball_data.pos.x, ball_data.pos.y, ball_data.pos.z);
	ball.castShadow = false;
	scene.add(ball);
}

function updateBallPosition(position) {
	ball.position.set(position.x, position.y, position.z);
}

export { updateBallPosition, ball_init };