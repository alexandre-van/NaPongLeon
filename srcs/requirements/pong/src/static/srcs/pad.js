import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.136.0/build/three.module.js';
import scene from './scene.js';

//Variable for paddles
const	padWidth = 1
const	padLength = 8;
const	padHeight = 2;

const	padColor = 0x0000ff 

let padX = 35;
let padY = 0;
let padZ = 1;

//Create the paddles
const geometry = new THREE.BoxGeometry(padWidth, padLength, padHeight);
const material = new THREE.MeshStandardMaterial({ color: padColor });
const pad1 = new THREE.Mesh(geometry, material);
const pad2 = new THREE.Mesh(geometry, material);
pad1.position.set(-padX, padY, padZ);
pad2.position.set(padX, padY, padZ);
scene.add(pad1);
scene.add(pad2);

//Function for paddles
function updatePadsPosition(position) {
	pad1.position.set(-padX, position['p1'], padZ);
	pad2.position.set(padX, position['p2'], padZ);
}
export { pad1, pad2,updatePadsPosition };