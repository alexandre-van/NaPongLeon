import * as THREE from '../../js/three.module.js';
import { renderer, camera, scene } from '../renderer.js';

function generateTree(tree, team_size) {
	const boxWidth = 10 * team_size; // Largeur des rectangles
	const boxHeight = 6; // Hauteur des rectangles
	const boxDepth = 1.5; // Profondeur des rectangles
	const verticalSpacing = 10; // Espacement vertical
	const horizontalSpacing = 10; // Espacement horizontal

	for (let level = 0; level < tree.length; level++) {
		const currentLevel = tree[level];
		const y = -level * verticalSpacing; // Position verticale de ce niveau

		const totalWidth = currentLevel.length * (boxWidth + horizontalSpacing) - horizontalSpacing;
		const startX = -totalWidth / 2; // Centrer les rectangles

		currentLevel.forEach((branch, index) => {
			const x = startX + index * (boxWidth + horizontalSpacing);
			createMatchBox(branch, x, y, boxWidth, boxHeight, boxDepth);

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

function createMatchBox(branch, x, y, boxWidth, boxHeight, boxDepth) {
	const boxGeometry = new THREE.BoxGeometry(boxWidth, boxHeight, boxDepth);
	const color = branch.match ? 0xffe333 : branch.bench ? 0xffffff : 0xA9A9A9
	const boxMaterial = new THREE.MeshStandardMaterial({
		color: color,
		emissive: color,
		side: THREE.DoubleSide,
	});
	const box = new THREE.Mesh(boxGeometry, boxMaterial);
	box.position.set(x, y, 0);
	box.castShadow = true;
	box.userData.branch = branch;
	scene.add(box);
	if (branch.match) {
		const textCanvas = document.createElement('canvas');
		const ctx = textCanvas.getContext('2d');
		textCanvas.width = 256;
		textCanvas.height = 128;
		ctx.font = '30px Arial';
		ctx.textAlign = 'center';
		ctx.textBaseline = 'middle';
		ctx.fillStyle = 'black';
		ctx.fillText(branch.match.team1.name, textCanvas.width / 2, textCanvas.height / 3);
		ctx.fillText(branch.match.team2.name, textCanvas.width / 2, textCanvas.height / 3 * 2);
		const textTexture = new THREE.CanvasTexture(textCanvas);
		const textGeometry = new THREE.PlaneGeometry(boxWidth, boxHeight);
		const textMaterial = new THREE.MeshBasicMaterial({ map: textTexture, transparent: true, side: THREE.DoubleSide });
		const textMesh = new THREE.Mesh(textGeometry, textMaterial);
		textMesh.position.set(x, y, boxDepth / 2); // Légèrement au-dessus du rectangle
		scene.add(textMesh);
	}
}


//import { Raycaster, Vector2 } from 'three';

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onClick(event) {
    // Calculer la position de la souris dans l'espace normalisé
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    // Effectuer le raycasting
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children);

    // Vérifier si un objet a été cliqué
    if (intersects.length > 0) {
        const clickedBox = intersects[0].object;

        // Vérifier si l'objet cliqué a des données de branche
        if (clickedBox.userData.branch) {
            const branch = clickedBox.userData.branch;

            // Afficher le parchemin avec les informations de branche
            showParchment(branch);
        }
    }
}

// Fonction pour afficher le parchemin avec les informations de la branche
function showParchment(branch) {
    // Récupérer l'élément du parchemin et le rendre visible
    const parchmentDiv = document.getElementById('parchment');
    parchmentDiv.style.display = 'block';

    // Afficher les informations de la branche dans le parchemin
    const branchInfoDiv = document.getElementById('branchInfo');
    branchInfoDiv.innerHTML = `
        <h2>Informations sur la branche</h2>
        <p><strong>Nom de l'équipe 1:</strong> ${branch.match ? branch.match.team1.name : 'N/A'}</p>
        <p><strong>Nom de l'équipe 2:</strong> ${branch.match ? branch.match.team2.name : 'N/A'}</p>
        <p><strong>Autre info:</strong> ${branch.otherInfo || 'Aucune info supplémentaire'}</p>
    `;
}
// Ajouter un écouteur pour les clics de souris
window.addEventListener('click', onClick);

function onMouseMove(event) {
	// Calculer la position de la souris dans l'espace normalisé
	mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
	mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

	// Effectuer le raycasting
	raycaster.setFromCamera(mouse, camera);
	const intersects = raycaster.intersectObjects(scene.children);

	// Réinitialiser l'émissivité des boîtes uniquement
	scene.children.forEach(child => {
		// Vérifier si l'objet est une boîte avant de réinitialiser son émissivité
		if (child.isMesh && child.material && child.material.emissive && child.userData.branch) {
			child.material.emissiveIntensity = 0.1; // Réinitialiser l'émissivité
		}
	});

	// Ajouter l'effet de surbrillance à la boîte survolée
	if (intersects.length > 0) {
		const hoveredBox = intersects[0].object;
		if (hoveredBox.userData.branch) {
			hoveredBox.material.emissiveIntensity = 0.5;
			console.log('Boîte survolée :', hoveredBox.userData.branch);
		}
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

function updateTree(tree) {
	clearTree();
	generateTree(tree);
}

export { generateTree, clearTree, updateTree };
