import * as THREE from '../../.js/three.module.js';
import { loadModelSTL } from '../load.js';
import { scene } from '../scene.js';

let padels = []; // Tableau pour stocker tous les padels
let padX, padZ;

function create_padel_data(model, data) {
	return {
		model: model,
		position: model.position,
		data: data
	};
}

async function padels_init(data, game_mode) {
	try {
		padX = data.pos.x;
		padZ = data.pos.z;

		// Matériaux pour les padels
		const materials = [
			new THREE.MeshStandardMaterial({ color: 0x318CE7 }), // Équipe gauche
			new THREE.MeshStandardMaterial({ color: 0x01D758 })  // Équipe droite
		];

		// Charger les géométries des modèles
		const geometry1 = await loadModelSTL('padel2.stl');
		const geometry2 = await loadModelSTL('padel1.stl');

		// Déterminer le nombre de padels et leur configuration selon le mode de jeu
		const numPadels = game_mode == 'PONG_DUO' ? 4 : 2;
		console.log("game_mode=", game_mode);
		for (let i = 0; i < numPadels; i++) {
			const material = i % 2 === 0 ? materials[0] : materials[1];
			const geometry = i % 2 === 0 ? geometry1 : geometry2;
			const model = new THREE.Mesh(geometry, material);

			// Positionner le padel initialement
			let xPos;
			if (game_mode == 'PONG_DUO') {
				// Mode PONG_DUO (2v2)
				xPos = i < 2 ? -padX : padX; // `pad1` et `pad3` à gauche, `pad2` et `pad4` à droite
			} else {
				// Mode PONG_CLASSIC (1v1)
				xPos = i === 0 ? -padX : padX; // `pad1` à gauche, `pad2` à droite
			}
			model.scale.set(data.size.x / 4, data.size.y / 12, data.size.z / 4);
			model.position.set(xPos, data.pos.y, padZ);
			model.castShadow = false;
			model.receiveShadow = false;
			scene.add(model);

			// Ajouter le padel au tableau
			const padel = create_padel_data(model, data);
			padels.push(padel);
			window[`pad${i + 1}`] = padel; // Pour garder la compatibilité avec ton ancien code (optionnel)
		}
	} catch (error) {
		console.error("Error: ", error);
	}
}

function updatePadsPosition(position) {
	if (padels.length > 0) {
		// Mettre à jour les positions des padels dynamiquement
		padels.forEach((padel, index) => {
			const padKey = `p${index + 1}`;
			if (position[padKey] !== undefined) {
				let xPos;
				if (padels.length === 2) {
					// Mode PONG_CLASSIC (1v1)
					xPos = index === 0 ? -padX : padX;
				} else {
					// Mode PONG_DUO (2v2)
					xPos = index < 2 ? -padX : padX;
				}
				padel.position.set(xPos, position[padKey], padZ);
			}
		});
	} else {
		console.error('Pads are not yet loaded');
	}
}

export { padels_init, updatePadsPosition };
