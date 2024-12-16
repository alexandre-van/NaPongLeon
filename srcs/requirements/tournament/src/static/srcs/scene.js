import * as THREE from '../js/three.module.js';
import { loadTexture } from './load.js';

let scene = null;
const backgroundPath = 'background_dark.png'

export function get_scene() {
	return scene;
}

export async function createScene() {
    if (scene) {
        return scene;
    }

    scene = new THREE.Scene();
    if (backgroundPath) {
        try {
            scene.background = await loadTexture(backgroundPath);
        } catch (error) {
            console.error("Erreur lors du chargement de la texture de fond :", error);
        }
    }
	return scene
}

export function cleanupScene() {
    if (!scene) {
        return;
    }
    scene.traverse(function (object) {
        if (object instanceof THREE.Mesh) {
            if (object.geometry) object.geometry.dispose();

            if (object.material) {
                if (object.material.isMaterial) {
                    disposeMaterial(object.material);
                } else if (Array.isArray(object.material)) {
                    object.material.forEach(disposeMaterial);
                }
            }
        }
    });
    const rendererElement = document.querySelector('canvas');
    if (rendererElement && rendererElement.parentNode) {
        rendererElement.parentNode.removeChild(rendererElement);
    }
    scene = null;
}

function disposeMaterial(material) {
    if (material.map) material.map.dispose();
    if (material.lightMap) material.lightMap.dispose();
    if (material.bumpMap) material.bumpMap.dispose();
    if (material.normalMap) material.normalMap.dispose();
    if (material.specularMap) material.specularMap.dispose();
    if (material.envMap) material.envMap.dispose();

    material.dispose();
}

export { scene };
