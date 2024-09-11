import * as THREE from '../../js/three.module.js';
import { STLLoader } from '../../js/STLLoader.js';
import scene from '../scene.js';

let pad1, pad2;
let padX, padZ; 

function padels_init(data) {
    padX = data.pos.x;
    padZ = data.pos.z;
    const material = new THREE.MeshStandardMaterial({ color: 0x0000ff });
    const loader = new STLLoader();
    loader.load('/api/pong/static/models/pad.stl', function (geometry) {
        const mesh1 = new THREE.Mesh(geometry, material);
        mesh1.position.set(-data.pos.x, data.pos.y, data.pos.z);
        scene.add(mesh1);
        pad1 = mesh1;
    }, undefined, function (error) {
        console.error('Error loading pad1 STL:', error);
    });

    loader.load('/api/pong/static/models/pad.stl', function (geometry) {
        const mesh2 = new THREE.Mesh(geometry, material);
        mesh2.position.set(-data.pos.x, data.pos.y, data.pos.z);
        scene.add(mesh2);
        pad2 = mesh2;
    }, undefined, function (error) {
        console.error('Error loading pad2 STL:', error);
    });
}

function updatePadsPosition(position) {
    if (pad1 && pad2) {
        pad1.position.set(-padX, position['p1'], padZ);
        pad2.position.set(padX, position['p2'], padZ);
    } else {
        console.error('Pads are not yet loaded');
    }
}

export { padels_init, updatePadsPosition };
