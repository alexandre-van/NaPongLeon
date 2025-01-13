import * as THREE from '../../js/three.module.js';
import { camera } from '../renderer.js';
import { create_interface, remove_interface} from '../init.js'
import { get_scene, scene } from '../scene.js';
import { spectate_game } from '../launch_game.js'
import { showParchment } from './parchment.js'
import { set_current_branch_inspect } from './tree.js'

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

const panels = [
    document.getElementById("teamParchment"),  // Remplacez par l'ID réel de votre fenêtre à gauche
    document.getElementById("parchment"),     // Remplacez par l'ID réel de votre fenêtre à droite
    document.getElementById("menu")           // Remplacez par l'ID réel de votre fenêtre en bas
];

// Vérifier si un élément est sous la souris
function isElementUnderMouse(element) {
    const rect = element.getBoundingClientRect();
    return (
        mouse.x >= (rect.left / window.innerWidth) * 2 - 1 &&
        mouse.x <= (rect.right / window.innerWidth) * 2 - 1 &&
        mouse.y >= -(rect.bottom / window.innerHeight) * 2 + 1 &&
        mouse.y <= -(rect.top / window.innerHeight) * 2 + 1
    );
}

// Vérifier si la souris est sur l'un des panneaux
function isMouseOnPanel() {
    return panels.some(panel => isElementUnderMouse(panel));
}

// Gérer les clics de souris
async function onClick(event) {
    if (isMouseOnPanel()) {
        return;
    }

    // Calculer la position de la souris dans l'espace normalisé
    updateMousePosition(event);

    // Effectuer le raycasting sur la scène Three.js
    raycaster.setFromCamera(mouse, camera);

    // Filtrer les objets interactifs dans la scène
    const interactiveObjects = getInteractiveObjects();
    if (interactiveObjects == null)
        return;
    const intersects = raycaster.intersectObjects(interactiveObjects);

    if (intersects.length > 0) {
        const clickedObject = intersects[0].object;
        await handleClickedObject(clickedObject);
    }
}

// Gérer les déplacements de souris
function onMouseMove(event) {
    updateMousePosition(event);

    // Mettre à jour les objets interactifs (pour highlight)
    raycaster.setFromCamera(mouse, camera);
    const interactiveObjects = getInteractiveObjects();
    if (interactiveObjects == null)
        return;
    // Réinitialiser la mise en surbrillance de tous les objets interactifs
    interactiveObjects.forEach(obj => resetHighlight(obj));
    if (isMouseOnPanel()) {
        return;
    }
    // Vérifier les intersections
    const intersects = raycaster.intersectObjects(interactiveObjects);
    if (intersects.length > 0) {
        const hoveredObject = intersects[0].object;
        highlightHoveredObject(hoveredObject);
    }
}

// Mettre à jour la position de la souris dans l'espace normalisé
function updateMousePosition(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

// Récupérer les objets interactifs dans la scène
function getInteractiveObjects() {
    let scene = get_scene();
    if (scene == null)
        return null;
    return scene.children.filter(child =>
        (child.isMesh && 
            (child.userData.branch || child.userData.isSpectateButton)) && 
            (child.material.emissive || 
                (Array.isArray(child.material) && child.userData.isSpectateButton))
    );
}

// Gérer le clic sur un objet
async function handleClickedObject(clickedObject) {
    if (clickedObject.userData.isSpectateButton) {
        console.log(`Spectating match ${clickedObject.userData.game}`);
        const game = clickedObject.userData.game;
        if (game)
            spectate_game(game);
            await remove_interface();
    } else {
        // Si l'objet cliqué est une boîte avec des données de branche
        set_current_branch_inspect(clickedObject.userData.branch);
        showParchment(clickedObject.userData.branch);
    }
}

// Réinitialiser la mise en surbrillance d'un objet interactif
function resetHighlight(obj) {
    if (obj.userData.isSpectateButton) {
        obj.material.forEach(mat => {
            if (mat.emissive) {
                mat.emissiveIntensity = 0.1;
            }
        });
    } else {
        obj.material.emissiveIntensity = 0.1;
    }
}

// Mettre en surbrillance un objet interactif
function highlightHoveredObject(obj) {
    if (obj.userData.isSpectateButton) {
        obj.material.forEach(mat => {
            if (mat.emissive) {
                mat.emissiveIntensity = 0.5; // Highlight
            }
        });
    } else {
        obj.material.emissiveIntensity = 0.5;
    }
}

export function setupEventListeners() {
    window.addEventListener('click', onClick);
    window.addEventListener('mousemove', onMouseMove);
}

export function removeEventListeners() {
    window.removeEventListener('click', onClick);
    window.removeEventListener('mousemove', onMouseMove);
}
