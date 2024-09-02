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

let pad1Dir = 0;
let pad2Dir = 0;

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
function updatePadsPosition() {
	;
}

function setPad1Dir(dir) {
	pad1Dir = dir;
}

function setPad2Dir(dir) {
	pad2Dir = dir;
}

function getPad1Dir()
{
	return pad1Dir;
}

function getPad2Dir()
{
	return pad2Dir;
}

export { pad1, pad2, updatePadsPosition, setPad1Dir , setPad2Dir,
		 getPad1Dir, getPad2Dir };