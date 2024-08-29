import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.136.0/build/three.module.js';
import scene from './scene.js';

const pointLight = new THREE.PointLight(0xffffff, 1);
pointLight.position.set(0, 0, 10);
pointLight.castShadow = true;

pointLight.shadow.mapSize.width = 512;
pointLight.shadow.mapSize.height = 512;
pointLight.shadow.camera.near = 0.5;
pointLight.shadow.camera.far = 500;

scene.add(pointLight);

export default pointLight;