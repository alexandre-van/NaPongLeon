import * as THREE from '../../js/three.module.js';
import { loadModelSTL } from '../load.js';
import scene from '../scene.js';

let pad1, pad2;
let padX, padZ; 

async function padels_init(data) {
    try {
        padX = data.pos.x;
        padZ = data.pos.z;
        const material1 = new THREE.MeshStandardMaterial({ color: 0x318CE7 });
        const geometry1 = await loadModelSTL('padel2.stl');
        const model1 = new THREE.Mesh(geometry1, material1);
        model1.position.set(-data.pos.x, data.pos.y, data.pos.z);
        model1.castShadow = false;
        model1.receiveShadow = false;
        scene.add(model1);
        pad1 = model1;
        const material2 = new THREE.MeshStandardMaterial({ color: 0x01D758 });
        const geometry2 = await loadModelSTL('padel1.stl');
        const model2 = new THREE.Mesh(geometry2, material2);
        model2.position.set(-data.pos.x, data.pos.y, data.pos.z);
        model2.castShadow = false;
        model2.receiveShadow = false;
        scene.add(model2);
        pad2 = model2;

    } catch (error) {
        console.error("Error: ", error);
    }
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
