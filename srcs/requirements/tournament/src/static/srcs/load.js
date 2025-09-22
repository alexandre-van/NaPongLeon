import * as THREE from '../js/three.module.js';
import { GLTFLoader } from '../js/GLTFLoader.js';
import { STLLoader } from '../js/STLLoader.js';

function loadModelGLT(url) {
    return new Promise((resolve, reject) => {
        const loader = new GLTFLoader();
        
        loader.load(`${location.origin}/api/tournament/static/tournament/models/` + url, function (gltf) {
            resolve(gltf);
        }, undefined, function (error) {
            reject(error);
        });
    });
}

function loadModelSTL(url) {
    return new Promise((resolve, reject) => {
        const loader = new STLLoader();
        loader.load(`${location.origin}/api/tournament/static/tournament/models/` + url, resolve, undefined, reject);
    });
};

function loadTexture(url) {
    
    return new Promise((resolve, reject) => {
        const loader = new THREE.TextureLoader();
        
        loader.load(`${location.origin}/api/tournament/static/tournament/texture/` + url, function (texture) {
            resolve(texture);
        }, undefined, function (error) {
            reject(error);
        });
    });
}

export { loadModelGLT, loadModelSTL, loadTexture };