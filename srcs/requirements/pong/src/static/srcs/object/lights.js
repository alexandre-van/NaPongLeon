import * as THREE from '../../.js/three.module.js';
import { scene } from '../scene.js';

function createSunlight() {
	const pointLight = new THREE.PointLight(0xffaa00, 200000000, 50000);
	pointLight.position.set(5000, 5000, 2500);
	scene.add(pointLight);
	pointLight.castShadow = true;
	pointLight.shadow.mapSize.width = 1024;
	pointLight.shadow.mapSize.height = 1024;
}

function createPlateauLight()
{
	const pointLight = new THREE.PointLight(0xffffff, 4000, 1000);
	pointLight.position.set(0, 0, 100);
	scene.add(pointLight);
	pointLight.castShadow = true;
	pointLight.shadow.mapSize.width = 1024;
	pointLight.shadow.mapSize.height = 1024;
}

export { createSunlight, createPlateauLight };
