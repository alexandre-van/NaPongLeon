import * as THREE from '../../.js/three.module.js';
import { scene } from '../scene.js';

function printWinner(winner) {
	// Create a canvas to render text
	const canvas = document.createElement('canvas');
	canvas.width = 1024;
	canvas.height = 512;
	const context = canvas.getContext('2d');

	// Clear canvas and set styling
	context.clearRect(0, 0, canvas.width, canvas.height);
	context.font = 'Bold 100px Arial';
	context.fillStyle = 'white';
	context.textAlign = 'center';

	// Write the score
	context.fillText(`The ${winner} side wins`, canvas.width / 2, 256);

	// Create texture from canvas
	const texture = new THREE.CanvasTexture(canvas);
	
	// Create a sprite with the score
	const spriteMaterial = new THREE.SpriteMaterial({ 
		map: texture,
		transparent: true 
	});
	Text = new THREE.Sprite(spriteMaterial);

	// Position the score at the top of the screen
	Text.position.set(0, 0, 2);
	Text.scale.set(40, 20, 1);

	// Add to scene
	scene.add(Text);

	return Text;
}

export {printWinner};