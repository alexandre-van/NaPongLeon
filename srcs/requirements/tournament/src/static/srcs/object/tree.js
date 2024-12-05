import * as THREE from '../../js/three.module.js';
import { renderer, camera, scene } from '../renderer.js';
import showParchment from './parchment.js'

const boxWidth = 10; // Largeur des rectangles
const boxHeight = 6; // Hauteur des rectangles
const boxDepth = 1.5; // Profondeur des rectangles
const verticalSpacing = 10; // Espacement vertical
const horizontalSpacing = 10; // Espacement horizontal
let team_size = 1

function generateTree(tree, nickname, data_team_size) {
    if (data_team_size) {
        team_size = data_team_size
    }
	for (let level = 0; level < tree.length; level++) {
		const currentLevel = tree[level];
		const y = -level * verticalSpacing; // Position verticale de ce niveau

		const totalWidth = currentLevel.length * (boxWidth * team_size + horizontalSpacing) - horizontalSpacing;
		const startX = -totalWidth / 2; // Centrer les rectangles

		currentLevel.forEach((branch, index) => {
			const x = startX + index * (boxWidth * team_size + horizontalSpacing);
			createMatchBox(branch, x, y, nickname);

			// Connecter avec le niveau précédent
			if (level > 0) {
				const parentIndex = Math.floor(index / 2); // Trouver le parent
				const previousLevel = tree[level - 1];
				const totalParentWidth = previousLevel.length * (boxWidth * team_size + horizontalSpacing) - horizontalSpacing;
				const parentX = -totalParentWidth / 2 + parentIndex * (boxWidth * team_size + horizontalSpacing);

				// Dessiner une ligne entre le parent et l'enfant
				drawConnection(parentX, -(level - 1) * verticalSpacing, x, y);
			}
		});
	}
}

function createMatchBox(branch, x, y, nickname) {
    const playerStatus = determinePlayerStatus(branch, nickname);
	console.log(playerStatus)
    const color = getBoxColor(branch, playerStatus);

    // Adjust box size for player's team
    const playerTeamMultiplier = playerStatus.isPlayerInTeam1 || playerStatus.isPlayerInTeam2
		|| playerStatus.isPlayerInBench? 1.2 : 1;
    const boxGeometry = new THREE.BoxGeometry(
        boxWidth * team_size, 
        boxHeight, 
        boxDepth
    );

    const boxMaterial = new THREE.MeshStandardMaterial({
        color: color,
        emissive: color,
        side: THREE.DoubleSide,
    });
    
    const box = new THREE.Mesh(boxGeometry, boxMaterial);
    box.scale.set(playerTeamMultiplier, playerTeamMultiplier, playerTeamMultiplier);
    box.position.set(x, y, 0);
    box.castShadow = true;
    box.userData.branch = branch;
    scene.add(box);
    return box;
}

function determinePlayerStatus(branch, nickname) {
    const status = {
        isPlayerInTeam1: false,
        isPlayerInTeam2: false,
        isPlayerInBench: false
    };

    if (branch.match) {
        const { team1, team2 } = branch.match;
        status.isPlayerInTeam1 = team1.players.some(player => player.nickname === nickname);
        status.isPlayerInTeam2 = team2.players.some(player => player.nickname === nickname);
    }

    if (branch.bench) {
        status.isPlayerInBench = branch.bench.players.some(player => player.nickname === nickname);
    }

    return status;
}

function getBoxColor(branch) {
    if (branch.match) return 0xffe333;
    if (branch.bench) return 0xffffff;
    return 0xA9A9A9;
}

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onClick(event) {
    // Calculer la position de la souris dans l'espace normalisé
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    // Effectuer le raycasting
    raycaster.setFromCamera(mouse, camera);
    
    // Filtrer uniquement les maillages avec des données de branche
    const boxesWithBranch = scene.children.filter(child => 
        child.isMesh && 
        child.userData.branch
    );

    // Vérifier les intersections avec seulement les boîtes ayant des données
    const intersects = raycaster.intersectObjects(boxesWithBranch);

    // Vérifier si un objet a été cliqué
    if (intersects.length > 0) {
        const clickedBox = intersects[0].object;
        showParchment(clickedBox.userData.branch);
    }
}
// Ajouter un écouteur pour les clics de souris
window.addEventListener('click', onClick);

function onMouseMove(event) {
    // Calculer la position de la souris dans l'espace normalisé
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    // Effectuer le raycasting
    raycaster.setFromCamera(mouse, camera);
    
    // Filtrer uniquement les maillages avec des données de branche
    const boxesWithBranch = scene.children.filter(child => 
        child.isMesh && 
        child.userData.branch && 
        child.material.emissive
    );

    // Réinitialiser l'émissivité de toutes les boîtes
    boxesWithBranch.forEach(box => {
        box.material.emissiveIntensity = 0.1;
    });

    // Vérifier les intersections avec seulement les boîtes ayant des données
    const intersects = raycaster.intersectObjects(boxesWithBranch);

    // Ajouter l'effet de surbrillance à la première boîte intersectée
    if (intersects.length > 0) {
        const hoveredBox = intersects[0].object;
        hoveredBox.material.emissiveIntensity = 0.5;
        console.log('Boîte survolée :', hoveredBox.userData.branch);
    }
}

// Ajouter un écouteur pour les mouvements de souris
window.addEventListener('mousemove', onMouseMove);

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

function updateTree(tree, nickname) {
    // Met à jour le contenu des branches sans recréer les objets
    tree.forEach((level, levelIndex) => {
        level.forEach((branch, index) => {

            const playerStatus = determinePlayerStatus(branch, nickname);
            const existingBox = scene.children.find(child => child.userData.branch && child.userData.branch.id === branch.id);

            if (existingBox) {
                // Mise à jour de la couleur et de la taille de la boîte
                const color = getBoxColor(branch);
                existingBox.userData.branch = branch
                existingBox.material.color.setHex(color);
                const playerTeamMultiplier = playerStatus.isPlayerInTeam1 || playerStatus.isPlayerInTeam2 || playerStatus.isPlayerInBench ? 1.2 : 1;
                console.log(team_size, "*", playerTeamMultiplier)
                existingBox.scale.set(playerTeamMultiplier, playerTeamMultiplier, playerTeamMultiplier);

                // Mise à jour du texte
                updateBoxText(existingBox, branch, playerStatus);
            } else {
                // Si la boîte n'existe pas, crée-la
                //const x = calculateXForBranch(level, index, levelIndex);
                //const y = -levelIndex * verticalSpacing;
                //createMatchBox(branch, x, y, nickname);
            }
        });
    });

    // Met à jour les connexions entre les niveaux
    //updateConnections(tree);
}

function updateBoxText(box, branch, playerStatus) {
    // Créez un nouveau canevas pour le texte
    const textCanvas = document.createElement('canvas');
    const ctx = textCanvas.getContext('2d');
    textCanvas.width = 256;
    textCanvas.height = 128;

    ctx.font = '30px Dancing Script';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'black';

    if (branch.match) {
        const { team1, team2 } = branch.match;
        ctx.font = playerStatus.isPlayerInTeam1 ? 'bold 40px Dancing Script' : '30px Dancing Script';
        ctx.fillText(team1.name, textCanvas.width / 2, textCanvas.height / 5);

        ctx.font = '30px Dancing Script';
        ctx.fillText("VS", textCanvas.width / 2, textCanvas.height / 2 * 1.05);

        ctx.font = playerStatus.isPlayerInTeam2 ? 'bold 40px Dancing Script' : '30px Dancing Script';
        ctx.fillText(team2.name, textCanvas.width / 2, textCanvas.height - textCanvas.height / 5);
    }

    if (branch.bench) {
        ctx.font = playerStatus.isPlayerInBench ? 'bold 40px Dancing Script' : '30px Dancing Script';
        ctx.fillText(branch.bench.name, textCanvas.width / 2, textCanvas.height / 2);
    }

    const textTexture = new THREE.CanvasTexture(textCanvas);
    const textMaterial = new THREE.MeshBasicMaterial({
        map: textTexture,
        transparent: true,
        side: THREE.DoubleSide
    });

    // Si le texte existe déjà, mettez à jour la texture
    if (box.textMesh) {
        box.textMesh.material.map = textTexture;
        box.textMesh.material.needsUpdate = true; // Forcer la mise à jour de la texture
    } else {
        // Si le texte n'existe pas, créez-le
        const textGeometry = new THREE.PlaneGeometry(boxWidth * team_size, boxHeight);
        box.textMesh = new THREE.Mesh(textGeometry, textMaterial);
        const zOffset = box.geometry.parameters.depth / 2 + 0.2;
        box.textMesh.position.set(box.position.x, box.position.y, zOffset);
        scene.add(box.textMesh);
    }
}



export { generateTree, clearTree, updateTree };
