import { render } from './renderer.js';

let animationId;

export function animate() {
	animationId = requestAnimationFrame(animate);
	render();
}

export function stopAnimation() {
	cancelAnimationFrame(animationId);
}
