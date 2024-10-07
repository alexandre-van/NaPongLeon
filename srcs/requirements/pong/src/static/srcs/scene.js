import * as THREE from '../js/three.module.js';

const scene = new THREE.Scene();
const loader = new THREE.TextureLoader();

loader.load('static/texture/sunset.jpg', function (texture) {
    scene.background = texture;
});


export default scene;
