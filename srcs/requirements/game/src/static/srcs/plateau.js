import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.136.0/build/three.module.js';
import scene from './scene.js';

let plateau

const arenaWidth = 80;
const arenaHeight = 60;


const plateauGeometry = new THREE.BoxGeometry(arenaWidth, arenaHeight, 0.1);
const plateauMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
plateau = new THREE.Mesh(plateauGeometry, plateauMaterial);
plateau.position.set(0, 0, -0.1);
plateau.castShadow = false;
scene.add(plateau);

export default plateau;