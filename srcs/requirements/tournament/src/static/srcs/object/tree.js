import * as THREE from '../../js/three.module.js';
import { scene } from '../scene.js';

function generateTree(tree) {
    const boxWidth = 8; // Largeur des rectangles représentant les matchs
    const boxHeight = 4; // Hauteur des rectangles augmentée à 4
    const boxDepth = 1.5; // Profondeur des rectangles pour leur donner une épaisseur
    const verticalSpacing = 6; // Espacement vertical entre les niveaux
    const horizontalSpacing = 6; // Espacement horizontal entre les cases d'un niveau

    // Parcourir les niveaux du tableau
    for (let level = 0; level < tree.length; level++) {
        const currentLevel = tree[level];
        const y = -level * verticalSpacing; // Position verticale de ce niveau

        let startX = 0;
        if (level > 1) {
            // Pour les autres niveaux, calculer la position horizontale en fonction du nombre de cases
            const totalWidth = currentLevel.length * (boxWidth + horizontalSpacing) - horizontalSpacing;
            startX = -totalWidth / 2; // Centrer horizontalement
        }

        // Si c'est le niveau 0 (vainqueur) ou niveau 1 (finale), ne pas diviser en plusieurs cases
        if (level === 0 || level === 1) {
            currentLevel.forEach((match, index) => {
                const x = startX + index * (boxWidth + horizontalSpacing);

                // Créer un rectangle en 3D pour le match (avec épaisseur)
                const boxGeometry = new THREE.BoxGeometry(boxWidth, boxHeight, boxDepth); 
                const boxMaterial = new THREE.MeshBasicMaterial({
                    color: match.length > 0 ? 0xffffff : 0xA9A9A9, // Blanc si le match existe, gris sinon
                    side: THREE.DoubleSide,
                });
                const box = new THREE.Mesh(boxGeometry, boxMaterial);
                box.position.set(x, y, 0); // Positionner le rectangle
                scene.add(box);

                // Ajouter du texte au centre de la case
                if (match.length > 0) {
                    const textCanvas = document.createElement('canvas');
                    const ctx = textCanvas.getContext('2d');
                    textCanvas.width = 256; // Largeur du canvas
                    textCanvas.height = 128; // Hauteur du canvas
                    ctx.font = '45px Arial'; // Augmenter la taille de la police
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = 'black';
                    ctx.fillText(match[0], textCanvas.width / 2, textCanvas.height / 2);

                    const textTexture = new THREE.CanvasTexture(textCanvas);
                    textTexture.minFilter = THREE.LinearFilter; // Améliorer la qualité de la texture

                    const textGeometry = new THREE.PlaneGeometry(boxWidth, boxHeight);
                    const textMaterial = new THREE.MeshBasicMaterial({ map: textTexture, transparent: true, side: THREE.DoubleSide });
                    const textMesh = new THREE.Mesh(textGeometry, textMaterial);

                    // Positionner le texte sur le rectangle
                    textMesh.position.set(x, y, boxDepth / 2); // Le texte doit être légèrement au-dessus de la case
                    scene.add(textMesh);
                }
            });
        } else {
            // Pour les autres niveaux (2 et au-delà), on génère normalement
            currentLevel.forEach((match, index) => {
                const x = startX + index * (boxWidth + horizontalSpacing);

                // Créer un rectangle en 3D pour le match (avec épaisseur)
                const boxGeometry = new THREE.BoxGeometry(boxWidth, boxHeight, boxDepth); 
                const boxMaterial = new THREE.MeshBasicMaterial({
                    color: match.length > 0 ? 0xffffff : 0xA9A9A9, // Blanc si le match existe, gris sinon
                    side: THREE.DoubleSide,
                });
                const box = new THREE.Mesh(boxGeometry, boxMaterial);
                box.position.set(x, y, 0); // Positionner le rectangle
                scene.add(box);

                // Ajouter du texte au centre de la case
                if (match.length > 0) {
                    const textCanvas = document.createElement('canvas');
                    const ctx = textCanvas.getContext('2d');
                    textCanvas.width = 256; // Largeur du canvas
                    textCanvas.height = 128; // Hauteur du canvas
                    ctx.font = '45px Arial'; // Augmenter la taille de la police
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = 'black';
                    ctx.fillText(match[0], textCanvas.width / 2, textCanvas.height / 2);

                    const textTexture = new THREE.CanvasTexture(textCanvas);
                    textTexture.minFilter = THREE.LinearFilter; // Améliorer la qualité de la texture

                    const textGeometry = new THREE.PlaneGeometry(boxWidth, boxHeight);
                    const textMaterial = new THREE.MeshBasicMaterial({ map: textTexture, transparent: true, side: THREE.DoubleSide });
                    const textMesh = new THREE.Mesh(textGeometry, textMaterial);

                    // Positionner le texte sur le rectangle
                    textMesh.position.set(x, y, boxDepth / 2); // Le texte doit être légèrement au-dessus de la case
                    scene.add(textMesh);
                }
            });
        }
    }

    // Dessiner les connexions entre les niveaux
    for (let level = 1; level < tree.length; level++) {
        const currentLevel = tree[level];
        const previousLevel = tree[level - 1];

        currentLevel.forEach((_, index) => {
            const parentIndex = Math.floor(index / 2); // Chaque case a un parent dans le niveau précédent
            if (previousLevel[parentIndex] !== undefined) {
                // Calculer la position exacte des parents et enfants
                const parentX = -((previousLevel.length * (boxWidth + horizontalSpacing)) / 2) + boxWidth / 2 + parentIndex * (boxWidth + horizontalSpacing);
                const parentY = -(level - 1) * verticalSpacing;

                const childX = -((currentLevel.length * (boxWidth + horizontalSpacing)) / 2) + boxWidth / 2 + index * (boxWidth + horizontalSpacing);
                const childY = -level * verticalSpacing;

                // Création des lignes de connexion avec une épaisseur augmentée
                const lineMaterial = new THREE.LineBasicMaterial({ 
                    color: 0xffffff, 
                    linewidth: 8 // Augmentation de l'épaisseur des lignes
                });
                const points = [
                    new THREE.Vector3(parentX - boxWidth / 8, parentY, 0),
                    new THREE.Vector3(childX - boxWidth / 8, childY, 0),
                ];
                const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
                const line = new THREE.Line(lineGeometry, lineMaterial);

                scene.add(line);
            }
        });
    }
}

function clearTree() {
    // Récupérer tous les objets de la scène
    const objectsToRemove = scene.children.filter(child => child instanceof THREE.Mesh || child instanceof THREE.Line);

    // Supprimer chaque objet
    objectsToRemove.forEach(object => {
        scene.remove(object); // Retirer l'objet de la scène
        object.geometry.dispose(); // Libérer la géométrie
        object.material.dispose(); // Libérer le matériau
    });
}

function updateTree(tree) {
    clearTree()
    generateTree(tree)
}

export { generateTree, clearTree, updateTree };
