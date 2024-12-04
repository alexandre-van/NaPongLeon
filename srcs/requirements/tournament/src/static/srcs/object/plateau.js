import * as THREE from '../../js/three.module.js';
import { loadTexture } from '../load.js';
import { scene } from '../scene.js';

async function createPlateau(tree) {
    try {
        // Calculer la largeur et la hauteur du plateau en fonction de la taille de l'arbre
        const boxWidth = 8; // Largeur des rectangles (matches)
        const boxHeight = 4;
        const horizontalSpacing = 8; // Espacement horizontal
        const verticalSpacing = 8; // Espacement vertical

        // Calculer la largeur du plateau : en fonction du plus large niveau d'arbre
        let maxWidth = 0;
        for (let level = 0; level < tree.length; level++) {
            const currentLevel = tree[level];
            const levelWidth = currentLevel.length * (boxWidth + horizontalSpacing);
            if (levelWidth > maxWidth) {
                maxWidth = levelWidth;
            }
        }

        // Calculer la hauteur du plateau : en fonction du nombre de niveaux
        const maxHeight = tree.length * verticalSpacing + boxHeight / 2;

        // Charger la texture et créer le plateau
        const texture = await loadTexture('Napoleon.jpg');
        const plateauGeometry = new THREE.BoxGeometry(maxWidth, maxHeight, 2); // Adapter la taille en fonction de l'arbre
        const plateauMaterial = new THREE.MeshStandardMaterial({ map: texture });
        const plateau = new THREE.Mesh(plateauGeometry, plateauMaterial);
        plateau.position.set(-boxWidth/2, -maxHeight/2 + boxHeight, -1.5); // Placer le plateau juste en dessous de l'arbre
        scene.add(plateau);

        // Ajouter une lumière directionnelle
        const light = new THREE.DirectionalLight(0xffffff, 1); // couleur blanche, intensité 1
        light.position.set(10, 10, 10); // position de la lumière
        scene.add(light);

        // Ajouter une lumière ambiante pour éclairer plus uniformément la scène
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5); // lumière ambiante douce
        scene.add(ambientLight);

    } catch (error) {
        console.error('Error:', error);
    }
}

export { createPlateau };
