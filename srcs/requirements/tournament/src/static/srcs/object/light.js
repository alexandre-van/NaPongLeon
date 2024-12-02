import * as THREE from '../../js/three.module.js';
import { scene } from '../scene.js';

const light = new THREE.PointLight(0xffffff, 1, 100);
light.position.set(10, 10, 10);
scene.add(light);
const ambientLight = new THREE.AmbientLight(0x404040); // Lumière douce
scene.add(ambientLight);