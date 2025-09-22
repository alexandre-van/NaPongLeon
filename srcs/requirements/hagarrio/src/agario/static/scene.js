import * as THREE from './three/three.module.js';
import { mapHeight, mapWidth } from './main.js';

export let scene;

let currentZoom = 1;
let targetZoom = 1;
const ZOOM_SMOOTHING = 0.008;

export function initScene() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);
    let aspect = window.innerWidth / window.innerHeight;
    const frustumSize = 800;
    const camera = new THREE.OrthographicCamera(
        frustumSize * aspect / -2,
        frustumSize * aspect / 2,
        frustumSize / 2,
        frustumSize / -2,
        0.1,
        800
    );
    
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    
    // Ajouter l'écouteur de redimensionnement
    window.addEventListener('resize', () => {
        const newAspect = window.innerWidth / window.innerHeight;
        
        // Mettre à jour le renderer
        renderer.setSize(window.innerWidth, window.innerHeight);
        
        // Mettre à jour la caméra
        camera.left = frustumSize * newAspect / -2;
        camera.right = frustumSize * newAspect / 2;
        camera.top = frustumSize / 2;
        camera.bottom = frustumSize / -2;
        camera.updateProjectionMatrix();
    });

    createGrid();
    createMapBorders(scene);
    return { scene, camera, renderer };
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

export function render(scene, camera, renderer) {
    renderer.render(scene, camera);
}

export function createMapBorders(scene) {
    const borderMaterial = new THREE.LineBasicMaterial({ color: 0xFFFFFF });
    const borderGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, -1),
        new THREE.Vector3(mapWidth, 0, -1),
        new THREE.Vector3(mapWidth, mapHeight, -1),
        new THREE.Vector3(0, mapHeight, -1),
        new THREE.Vector3(0, 0, -1)
    ]);
    const borderLine = new THREE.Line(borderGeometry, borderMaterial);
    scene.add(borderLine);
}

export function updateCameraPosition(camera, player) {
    // Mettre à jour le regard de la caméra par rapport au player
    if (player && player.x !== undefined && player.y !== undefined) {
        camera.position.set(player.x, player.y, 200);
        camera.lookAt(player.x, player.y, 0);
    }

    const maxZoom = 4; // Limite maximale du zoom
    // Calculer le zoom cible avec une limite maximale
    targetZoom = Math.min(maxZoom, 1 + (player.size / 100));

    // Limiter la vitesse maximale de changement de zoom
    const maxZoomChange = 0.01;
    const zoomDelta = (targetZoom - currentZoom) * ZOOM_SMOOTHING;
    const clampedZoomDelta = Math.max(-maxZoomChange, Math.min(maxZoomChange, zoomDelta));
    currentZoom += clampedZoomDelta;

    // Mettre à jour la taille de la vue
    const frustumSize = 800 * currentZoom;
    const aspect = window.innerWidth / window.innerHeight;

    // Mettre à jour les paramètres de la caméra
    camera.left = frustumSize * aspect / -2;
    camera.right = frustumSize * aspect / 2;
    camera.top = frustumSize / 2;
    camera.bottom = frustumSize / -2;
    
    camera.updateProjectionMatrix();
}

export function getScene() {
    return scene;
}
