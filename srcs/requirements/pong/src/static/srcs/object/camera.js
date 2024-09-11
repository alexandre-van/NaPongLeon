import * as THREE from '../../js/three.module.js';

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
//camera.position.z = 45;

camera.position.z = 25;
camera.position.y = -45;
camera.rotateX(45);

export default camera;