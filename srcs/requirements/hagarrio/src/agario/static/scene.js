import * as THREE from './three/three.module.js';
import { mapHeight, mapWidth } from './main.js';

export let scene;


export function initScene() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);
    let aspect = window.innerWidth / window.innerHeight;
    const frustumSize = 1000;
    const camera = new THREE.OrthographicCamera(
        frustumSize * aspect / -2,
        frustumSize * aspect / 2,
        frustumSize / 2,
        frustumSize / -2,
        0.1,
        1000
    );
    // const camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 20000);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    createMapBorders(scene);
    createGrid();
    camera.position.set(0, 0, 500);
    camera.lookAt(0, 0, 0);
    return { scene, camera, renderer };
}

export function render(scene, camera, renderer) {
    renderer.render(scene, camera);
}

export function createMapBorders(scene) {
    const borderMaterial = new THREE.LineBasicMaterial({ color: 0xFFFFFF });
    const borderGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(mapWidth, 0, 0),
        new THREE.Vector3(mapWidth, mapHeight, 0),
        new THREE.Vector3(0, mapHeight, 0),
        new THREE.Vector3(0, 0, 0)
    ]);
    const borderLine = new THREE.Line(borderGeometry, borderMaterial);
    scene.add(borderLine);
}

export function updateCameraPosition(camera, player) {
    if (player && player.x !== undefined && player.y !== undefined) {
        //console.log('in updateCameraPosition, Updating camera position to:', player.x, player.y, camera.position.z);
        camera.position.set(player.x, player.y, camera.position.z);
        camera.lookAt(player.x, player.y, 0);
    }
    const zoomFactor = 1 + (player.size / 100);
    const frustumSize = 1000 * zoomFactor;
    const aspect = window.innerWidth / window.innerHeight;
    camera.left = frustumSize * aspect / -2;
    camera.right = frustumSize * aspect / 2;
    camera.top = frustumSize / 2;
    camera.bottom = frustumSize / -2;
    camera.updateProjectionMatrix();
}

export function getScene() {
    return scene;
}

export function createGrid() {
    const gridSize = mapHeight; // Taille totale de la grille
    const divisions = mapHeight / 200; // Nombre de divisions
    const gridHelper = new THREE.GridHelper(gridSize, divisions, 0x444444, 0x222222);
    
    // Rotation pour que la grille soit horizontale (X-Z plane)
    gridHelper.rotation.x = Math.PI / 2;
    
    // Position de la grille au centre de la scène
    gridHelper.position.set(gridSize/2, gridSize/2, -1);
    gridHelper.renderOrder = 0;
    
    scene.add(gridHelper);
}
