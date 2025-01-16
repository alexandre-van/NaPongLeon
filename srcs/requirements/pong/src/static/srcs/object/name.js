import * as THREE from '../../.js/three.module.js';
import { scene } from '../scene.js';

let nameTextLeft = null;
let nameTextRight = null;

function createName(data) {

    function createPlayerNameCanvas(name) {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 128;
        const context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);

        // Initial font size
        let fontSize = 60;
        context.font = `Bold ${fontSize}px Arial`;

        // Dynamically reduce font size if text is too wide
        while (context.measureText(name).width > canvas.width - 20 && fontSize > 10) {
            fontSize -= 2;
            context.font = `Bold ${fontSize}px Arial`;
        }

        context.fillStyle = 'white';
        context.textAlign = 'center';
        context.fillText(name, canvas.width / 2, canvas.height / 2 + fontSize / 3);

        return new THREE.CanvasTexture(canvas);
    }

    // Création pour le joueur de gauche
    const textureLeft = createPlayerNameCanvas(data.left);
    const spriteMatLeft = new THREE.SpriteMaterial({
        map: textureLeft,
        transparent: true,
    });

    const nameTextLeft = new THREE.Sprite(spriteMatLeft);
    nameTextLeft.position.set(-35, 40, 2);
    nameTextLeft.scale.set(15, 12.5, 1);
    scene.add(nameTextLeft);

    // Création pour le joueur de droite
    const textureRight = createPlayerNameCanvas(data.right);
    const spriteMatRight = new THREE.SpriteMaterial({
        map: textureRight,
        transparent: true,
    });

    const nameTextRight = new THREE.Sprite(spriteMatRight);
    nameTextRight.position.set(35, 40, 2);
    nameTextRight.scale.set(15, 12.5, 1);
    scene.add(nameTextRight);

    return { nameTextLeft, nameTextRight };
}

export { createName };