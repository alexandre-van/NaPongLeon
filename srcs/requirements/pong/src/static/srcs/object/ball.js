import * as THREE from '../../.js/three.module.js';

import { scene } from '../scene.js';

let ball = null;

function create_ball_data(model, data) {
	return {
		model: model,
		position: model.position,
		data: data
	}
}

function ball_init(ball_data) {
	const geometry = new THREE.SphereGeometry(ball_data.rad, 32, 32);
	const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
	const model = new THREE.Mesh(geometry, material);

	model.position.set(ball_data.pos.x, ball_data.pos.y, ball_data.pos.z);
	model.castShadow = false;
	scene.add(model);
	ball = create_ball_data(model, ball_data);
	window.ball = ball;
}

function updateBallPosition(position) {
	ball.position.set(position.x, position.y, position.z);
}

export { updateBallPosition, ball_init };