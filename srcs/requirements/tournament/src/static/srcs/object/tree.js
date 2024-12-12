import * as THREE from '../../js/three.module.js';
import { get_scene } from '../scene.js';

let scene = null

const boxWidth = 10; // Largeur des rectangles
const boxHeight = 6; // Hauteur des rectangles
const boxDepth = 1.5; // Profondeur des rectangles
const verticalSpacing = 10; // Espacement vertical
const horizontalSpacing = 10; // Espacement horizontal
let team_size = 1
let tree = []

export function generateTree(newtree, nickname, data_team_size=null) {
	scene = get_scene()
	if (scene == null)
		return;
	if (newtree)
		tree = newtree
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
	updateTree(tree, nickname)
}

function createMatchBox(branch, x, y, nickname) {
	const playerStatus = determinePlayerStatus(branch, nickname);
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
	scene = get_scene()
    if (scene)
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
    if (branch.match) {
        switch (branch.match.status) {
            case 'Game in progress':
                return 0xffe333; // Jaune par défaut
            case 'Game aborted':
                return 0xff4444; // Rouge pour un match annulé
            case 'Game finished':
                return 0x4CAF50; // Vert pour un match terminé
            default:
                return 0xffe333; // Jaune par défaut si statut inconnu
        }
    }
    if (branch.bench) return 0xADD8E6; // Bleu clair pour le bench
    return 0xA9A9A9; // Gris par défaut pour les cellules vides
}

function drawConnection(x1, y1, x2, y2) {
	// Matériau de la ligne avec une épaisseur augmentée
	const lineMaterial = new THREE.LineBasicMaterial({
		color: 0xffffff,
		linewidth: 100, // Épaisseur de la ligne
	});

	// Points de la ligne : du centre du parent au centre de l'enfant
	const points = [
		new THREE.Vector3(x1, y1, 0),
		new THREE.Vector3(x2, y2, 0),
	];

	// Créer et ajouter la ligne à la scène
	const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
	const line = new THREE.Line(lineGeometry, lineMaterial);
	scene = get_scene()
    if (scene)
		scene.add(line);
}

export function clearTree() {
	scene = get_scene()
    if (scene == null)
        return;
	// Supprimer les anciens objets de la scène
	const objectsToRemove = scene.children.filter(child => child instanceof THREE.Mesh || child instanceof THREE.Line);
	objectsToRemove.forEach(object => {
		scene.remove(object);
		object.geometry.dispose();
		object.material.dispose();
	});
}

export function updateTree(newtree, nickname) {
	if (newtree)
		tree = newtree
	scene = get_scene()
    if (scene == null)
        return;
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
				let playerTeamMultiplier = playerStatus.isPlayerInTeam1 || playerStatus.isPlayerInTeam2 || playerStatus.isPlayerInBench ? 1.25 : 1;
				existingBox.scale.set(playerTeamMultiplier, playerTeamMultiplier, playerTeamMultiplier);

				// Mise à jour du texte
				updateBoxText(existingBox, branch, playerStatus, playerTeamMultiplier);
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

// Fonction pour déterminer si une équipe est perdante
const isLosingTeam = (teamName, winner, status) => {
    return (status === "Game aborted" || status === "Game finished") && teamName !== winner;
};

// Fonction pour dessiner du texte avec style spécifique
const drawText = (ctx, text, x, y, options = {}) => {
    const {
        font = '30px Dancing Script',
        color = 'black',
        strikeThrough = false
    } = options;

    ctx.font = font;
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);

    if (strikeThrough) {
        const textWidth = ctx.measureText(text).width;
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.moveTo(x, y - 15); // Ligne au milieu du texte
        ctx.lineTo(x + textWidth, y - 15);
        ctx.stroke();
    }
};

function renderMatchText(ctx, textCanvas, playerStatus, match) {
    const isLoserTeam = (teamName) => 
        (match.status === 'Game finished' || match.status === 'Game aborted') && 
        teamName !== match.winner;

    const renderTeamText = (teamName, isTop) => {
        const isPlayerInTeam = isTop 
            ? playerStatus.isPlayerInTeam1 
            : playerStatus.isPlayerInTeam2;

        ctx.font = isPlayerInTeam ? 'bold 40px Dancing Script' : '30px Dancing Script';
        
        const yPosition = isTop 
            ? textCanvas.height / 5 
            : textCanvas.height - textCanvas.height / 5;

        if (isLoserTeam(teamName)) {
            ctx.fillStyle = 'red';
            ctx.save();
            
            ctx.fillText(teamName, textCanvas.width / 2, yPosition);
            
            const textWidth = ctx.measureText(teamName).width;
            
            ctx.beginPath();
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 2;
            ctx.moveTo(
                textCanvas.width / 2 - textWidth / 2, 
                yPosition
            );
            ctx.lineTo(
                textCanvas.width / 2 + textWidth / 2, 
                yPosition
            );
            ctx.stroke();
            
            ctx.restore();
        } else {
            ctx.fillStyle = 'black';
            ctx.fillText(teamName, textCanvas.width / 2, yPosition);
        }
    };

    if (match) {
        const { team1, team2 } = match;

        renderTeamText(team1.name, true);

        ctx.font = '30px Dancing Script';
        ctx.fillStyle = 'black';
        ctx.fillText("VS", textCanvas.width / 2, textCanvas.height / 2 * 1.05);

        renderTeamText(team2.name, false);
    }
}


function updateBoxText(box, branch, playerStatus, playerTeamMultiplier) {
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
		renderMatchText(ctx, textCanvas, playerStatus, branch.match);
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

	if (box.textMesh) {
		box.textMesh.material.map = textTexture;
		box.textMesh.material.needsUpdate = true;
	} else {
		const textGeometry = new THREE.PlaneGeometry(boxWidth * team_size, boxHeight);
		box.textMesh = new THREE.Mesh(textGeometry, textMaterial);
		const zOffset = box.geometry.parameters.depth / 2 + 0.2;
		box.textMesh.position.set(box.position.x, box.position.y, zOffset);
		scene = get_scene()
    	if (scene)
			scene.add(box.textMesh);
	}
	manageSpectateButton(box, branch, playerTeamMultiplier);
}


function manageSpectateButton(box, branch, playerTeamMultiplier) {
	const matchInProgress = branch.match && branch.match.status === "Game in progress...";
	const buttonColor = '#F08080';

	if (matchInProgress && playerTeamMultiplier == 1) {
		// Agrandir la boîte pour faire de la place au bouton
		playerTeamMultiplier = 1.25;
		box.scale.set(playerTeamMultiplier, playerTeamMultiplier, playerTeamMultiplier);
		const zOffset = box.position.z + box.geometry.parameters.depth / 2 + 0.2;

		if (box.textMesh) {
			box.textMesh.position.set(box.position.x, box.position.y + boxHeight / 8, zOffset);
		}

		if (!box.spectateButton) {
			// Créer la géométrie du bouton avec une épaisseur
			const buttonGeometry = new THREE.BoxGeometry(boxWidth, boxHeight / 4, 0.2); // 0.2 pour l'épaisseur
			const buttonCanvas = document.createElement('canvas');
			const ctx = buttonCanvas.getContext('2d');
			buttonCanvas.width = 128;
			buttonCanvas.height = 64;

			// Style du bouton
			ctx.fillStyle = buttonColor; // Couleur de fond du bouton
			ctx.fillRect(0, 0, buttonCanvas.width, buttonCanvas.height);
			ctx.font = 'bold 35px Dancing Script';
			ctx.fillStyle = 'black';
			ctx.textAlign = 'center';
			ctx.textBaseline = 'middle';
			ctx.fillText('Spectate', buttonCanvas.width / 2, buttonCanvas.height / 2);

			const buttonTexture = new THREE.CanvasTexture(buttonCanvas);
			const buttonMaterial = new THREE.MeshStandardMaterial({
				map: buttonTexture,
				color: buttonColor,
				emissive: new THREE.Color(buttonColor), // Couleur émissive
				emissiveIntensity: 0.1, // Intensité de l'émissivité
				transparent: true,
				side: THREE.FrontSide
			});

			// Matériaux pour toutes les faces du bouton
			const materials = [
				new THREE.MeshStandardMaterial({ color: buttonColor }), // Faces latérales
				new THREE.MeshStandardMaterial({ color: buttonColor }), // Faces latérales
				new THREE.MeshStandardMaterial({ color: buttonColor }), // Faces latérales
				new THREE.MeshStandardMaterial({ color: buttonColor }), // Faces latérales
				buttonMaterial, // Face supérieure (avec texte)
				new THREE.MeshStandardMaterial({ color: buttonColor })  // Face inférieure
			];

			box.spectateButton = new THREE.Mesh(buttonGeometry, materials);
			box.spectateButton.position.set(box.position.x, box.position.y - boxHeight / 2.25, zOffset);
			box.spectateButton.userData.isSpectateButton = true; // Identifie le bouton
			scene = get_scene()
    		if (scene)
				scene.add(box.spectateButton);

		}
	} else if (box.spectateButton) {
		scene.remove(box.spectateButton);
		box.spectateButton.geometry.dispose();
		box.spectateButton.material.forEach(mat => mat.dispose());
		box.spectateButton = null;
		const zOffset = box.geometry.parameters.depth / 2 + 0.2;
		box.textMesh.position.set(box.position.x, box.position.y, zOffset);
	}
}



export function findCellByCellId(cell_id) {
	console.log(tree)
	// Parcours de tous les niveaux de l'arbre
	for (const level of tree) {
		// Vérification que le niveau est bien un tableau
		if (Array.isArray(level)) {
			// Parcours des cellules du niveau
			for (const cell of level) {
				// Vérification de l'ID du jeu dans la cellule
				if (cell.id === cell_id) {
					return cell; // Cellule trouvée
				}
			}
		}
	}
	// Si aucune correspondance n'a été trouvée
	return null;
}
