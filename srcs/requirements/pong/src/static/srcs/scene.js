import * as THREE from '../js/three.module.js';

const scene = new THREE.Scene();
const loader = new THREE.TextureLoader();
const host = window.location.hostname;
const port = window.location.port;

loader.load(`http://${host}:${port}/api/pong/static/pong/texture/sunset.jpg`, function (texture) {
    scene.background = texture;
});


export default scene;
