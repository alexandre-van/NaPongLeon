import * as THREE from '../../js/three.module.js';
import { scene } from '../scene.js';

function generateTree(tree) {
    // Dimensions pour les cubes
    const cubeSize = 1;
    const spacing = 2; // Espace horizontal entre les nœuds
    const verticalSpacing = 3; // Espace vertical entre les niveaux

    tree.forEach((level, levelIndex) => {
        const y = -levelIndex * verticalSpacing; // Déplacement vertical pour chaque niveau

        level.forEach((node, nodeIndex) => {
            if (node.length === 0) return; // Sauter les nœuds vides

            const x = (nodeIndex - (level.length - 1) / 2) * spacing; // Centrer les nœuds horizontalement
            const z = 0;

            // Créer un cube pour représenter le nœud
            const geometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
            const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
            const cube = new THREE.Mesh(geometry, material);

            // Positionner le cube
            cube.position.set(x, y, z);

            // Ajouter une étiquette texte pour identifier le nœud (si nécessaire)
            if (node[0]) {
                const label = createTextLabel(node[0]);
                label.position.set(x, y - cubeSize, z);
                scene.add(label);
            }

            // Ajouter le cube à la scène
            scene.add(cube);
        });
    });
}

// Fonction pour créer un label texte
function createTextLabel(text) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    context.font = '48px Arial';
    context.fillStyle = 'black';
    context.fillText(text, 0, 50);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);

    return sprite;
}

export default generateTree;
