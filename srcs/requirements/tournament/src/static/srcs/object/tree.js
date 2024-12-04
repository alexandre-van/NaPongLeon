import * as THREE from '../../js/three.module.js';
import { scene } from '../scene.js';

function generateTree(tree) {
    const boxWidth = 8; // Largeur des rectangles
    const boxHeight = 4; // Hauteur des rectangles
    const boxDepth = 1.5; // Profondeur des rectangles
    const verticalSpacing = 8; // Espacement vertical
    const horizontalSpacing = 8; // Espacement horizontal

    for (let level = 0; level < tree.length; level++) {
        const currentLevel = tree[level];
        const y = -level * verticalSpacing; // Position verticale de ce niveau

        const totalWidth = currentLevel.length * (boxWidth + horizontalSpacing) - horizontalSpacing;
        const startX = -totalWidth / 2; // Centrer les rectangles

        currentLevel.forEach((match, index) => {
            const x = startX + index * (boxWidth + horizontalSpacing);
            createMatchBox(match, x, y, boxWidth, boxHeight, boxDepth);

            // Connecter avec le niveau précédent
            if (level > 0) {
                const parentIndex = Math.floor(index / 2); // Trouver le parent
                const previousLevel = tree[level - 1];
                const totalParentWidth = previousLevel.length * (boxWidth + horizontalSpacing) - horizontalSpacing;
                const parentX = -totalParentWidth / 2 + parentIndex * (boxWidth + horizontalSpacing);

                // Dessiner une ligne entre le parent et l'enfant
                drawConnection(parentX, -(level - 1) * verticalSpacing, x, y);
            }
        });
    }
}

function createMatchBox(match, x, y, boxWidth, boxHeight, boxDepth) {
    const boxGeometry = new THREE.BoxGeometry(boxWidth, boxHeight, boxDepth);
    const boxMaterial = new THREE.MeshBasicMaterial({
        color: match?.length > 0 ? 0xffffff : 0xA9A9A9, // Blanc si le match existe, gris sinon
        side: THREE.DoubleSide,
    });
    const box = new THREE.Mesh(boxGeometry, boxMaterial);
    box.position.set(x, y, 0);
    scene.add(box);

    // Ajouter du texte si nécessaire
    if (match?.length > 0) {
        const textCanvas = document.createElement('canvas');
        const ctx = textCanvas.getContext('2d');
        textCanvas.width = 256;
        textCanvas.height = 128;
        ctx.font = '45px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = 'black';
        ctx.fillText(match[0], textCanvas.width / 2, textCanvas.height / 2);

        const textTexture = new THREE.CanvasTexture(textCanvas);
        const textGeometry = new THREE.PlaneGeometry(boxWidth, boxHeight);
        const textMaterial = new THREE.MeshBasicMaterial({ map: textTexture, transparent: true, side: THREE.DoubleSide });
        const textMesh = new THREE.Mesh(textGeometry, textMaterial);
        textMesh.position.set(x, y, boxDepth / 2); // Légèrement au-dessus du rectangle
        scene.add(textMesh);
    }
}

function drawConnection(x1, y1, x2, y2) {
    // Matériau de la ligne avec une épaisseur augmentée
    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0xffffff,
        linewidth: 3, // Épaisseur de la ligne
    });

    // Points de la ligne : du centre du parent au centre de l'enfant
    const points = [
        new THREE.Vector3(x1, y1, 0),
        new THREE.Vector3(x2, y2, 0),
    ];

    // Créer et ajouter la ligne à la scène
    const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(lineGeometry, lineMaterial);
    scene.add(line);
}

function clearTree() {
    // Supprimer les anciens objets de la scène
    const objectsToRemove = scene.children.filter(child => child instanceof THREE.Mesh || child instanceof THREE.Line);
    objectsToRemove.forEach(object => {
        scene.remove(object);
        object.geometry.dispose();
        object.material.dispose();
    });
}

function updateTree(tree) {
    clearTree();
    generateTree(tree);
}

export { generateTree, clearTree, updateTree };
