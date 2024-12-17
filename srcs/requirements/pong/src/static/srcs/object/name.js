import * as THREE from '../../js/three.module.js';
import { scene } from '../scene.js';

function createName {
	// Create a canvas to render text
	const canvas = document.createElement('canvas');
	canvas.width = 256;
	canvas.height = 128;
	const context = canvas.getContext('2d');

	// Clear canvas and set styling
	context.clearRect(0, 0, canvas.width, canvas.height);
	context.font = 'Bold 60px Arial';
	context.fillStyle = 'white';
	context.textAlign = 'center';
}