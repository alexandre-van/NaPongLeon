import * as THREE from '../../js/three.module.js';
import { get_scene } from '../scene.js';
import { updateBranchParchment } from './parchment.js'

let scene = null;
let current_branch_inspect = null;

const boxWidth = 10;
const boxHeight = 6;
const boxDepth = 1.5;
const verticalSpacing = 10;
const horizontalSpacing = 10;
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
		const y = -level * verticalSpacing;

		const totalWidth = currentLevel.length * (boxWidth * team_size + horizontalSpacing) - horizontalSpacing;
		const startX = -totalWidth / 2;

		currentLevel.forEach((branch, index) => {
			const x = startX + index * (boxWidth * team_size + horizontalSpacing);
			createMatchBox(branch, x, y, nickname);

			if (level > 0) {
				const parentIndex = Math.floor(index / 2);
				const previousLevel = tree[level - 1];
				const totalParentWidth = previousLevel.length * (boxWidth * team_size + horizontalSpacing) - horizontalSpacing;
				const parentX = -totalParentWidth / 2 + parentIndex * (boxWidth * team_size + horizontalSpacing);

				drawConnection(parentX, -(level - 1) * verticalSpacing, x, y);
			}
		});
	}
	updateTree(tree, nickname)
}

function createMatchBox(branch, x, y, nickname) {
	const playerStatus = determinePlayerStatus(branch, nickname);
	const color = getBoxColor(branch, playerStatus);

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
                return 0xffe333;
            case 'Game aborted':
                return 0xff4444;
            case 'Game finished':
                return 0x4CAF50;
            default:
                return 0xffe333;
        }
    }
    if (branch.bench) return 0xADD8E6;
    return 0xA9A9A9;
}

function drawConnection(x1, y1, x2, y2) {
	const lineMaterial = new THREE.LineBasicMaterial({
		color: 0xffffff,
		linewidth: 100,
	});
	const points = [
		new THREE.Vector3(x1, y1, 0),
		new THREE.Vector3(x2, y2, 0),
	];
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
	tree.forEach((level, levelIndex) => {
		level.forEach((branch, index) => {

			const playerStatus = determinePlayerStatus(branch, nickname);
			const existingBox = scene.children.find(child => child.userData.branch && child.userData.branch.id === branch.id);

			if (existingBox) {
				if (current_branch_inspect && existingBox.userData.branch.id == current_branch_inspect)
					updateBranchParchment(branch);
				const color = getBoxColor(branch);
				existingBox.userData.branch = branch
				existingBox.material.color.setHex(color);
				let playerTeamMultiplier = playerStatus.isPlayerInTeam1 || playerStatus.isPlayerInTeam2 || playerStatus.isPlayerInBench ? 1.25 : 1;
				existingBox.scale.set(playerTeamMultiplier, playerTeamMultiplier, playerTeamMultiplier);
				updateBoxText(existingBox, branch, playerStatus, playerTeamMultiplier);
			}
		});
	});
}

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
		playerTeamMultiplier = 1.25;
		box.scale.set(playerTeamMultiplier, playerTeamMultiplier, playerTeamMultiplier);
		const zOffset = box.position.z + box.geometry.parameters.depth / 2 + 0.2;

		if (box.textMesh) {
			box.textMesh.position.set(box.position.x, box.position.y + boxHeight / 8, zOffset);
		}

		if (!box.spectateButton) {
			const buttonGeometry = new THREE.BoxGeometry(boxWidth, boxHeight / 4, 0.2);
			const buttonCanvas = document.createElement('canvas');
			const ctx = buttonCanvas.getContext('2d');
			buttonCanvas.width = 128;
			buttonCanvas.height = 64;

			ctx.fillStyle = buttonColor;
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
				emissive: new THREE.Color(buttonColor),
				emissiveIntensity: 0.1,
				transparent: true,
				side: THREE.FrontSide
			});
			const materials = [
				new THREE.MeshStandardMaterial({ color: buttonColor }),
				new THREE.MeshStandardMaterial({ color: buttonColor }),
				new THREE.MeshStandardMaterial({ color: buttonColor }),
				new THREE.MeshStandardMaterial({ color: buttonColor }),
				buttonMaterial,
				new THREE.MeshStandardMaterial({ color: buttonColor })
			];

			box.spectateButton = new THREE.Mesh(buttonGeometry, materials);
			box.spectateButton.position.set(box.position.x, box.position.y - boxHeight / 2.25, zOffset);
			box.spectateButton.userData.isSpectateButton = true;
			box.spectateButton.userData.game = branch.match.game;
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
	for (const level of tree) {
		if (Array.isArray(level)) {
			for (const cell of level) {
				if (cell.id === cell_id) {
					return cell;
				}
			}
		}
	}
	return null;
}

export function set_current_branch_inspect(branch) {
	current_branch_inspect = branch.id;
}
