import { useState, useEffect } from 'react'; // Ajouter useEffect ici
import api from '../services/api.js';

const PlayButton = ({ gameMode, modifiers }) => {
	const [loading, setLoading] = useState(false);
	const [errorMessage, setErrorMessage] = useState(null);

	const handlePlayButton = async () => {
		try {
			setLoading(true);
			setErrorMessage(null); // Reset error message before starting

			const mods = modifiers.join(",");
			const response = await api.get(`/game_manager/matchmaking/game_mode=${gameMode}?mods=${mods}`, 3600000);
			const gameId = response.data['data']['game_id'];
			if (!gameId) throw new Error('Game ID is missing from the response.');

			// Stocker le gameId dans window.gameInfo
			if (!window.gameInfo) {
				window.gameInfo = {};
			}
			//window.gameInfo.gameId = gameId;

			// Construire l'URL du jeu avec le gameId
			const host = window.location.hostname;
			const port = window.location.port;
			const gameUrl = `http://${host}:${port}/api/pong?gameId=${gameId}`;

			// Créer une iframe pour afficher le jeu
			const iframe = document.createElement('iframe');
			iframe.src = gameUrl;
			iframe.style.position = "fixed"; // Fixe pour qu'il reste à la même position
			iframe.style.top = "0";         // Aligner en haut de la page
			iframe.style.left = "0";        // Aligner à gauche de la page
			iframe.style.width = "100vw";   // Largeur : 100% de la fenêtre
			iframe.style.height = "100vh";  // Hauteur : 100% de la fenêtre
			iframe.style.border = "none";   // Supprimer les bordures

			// Supprimer l'ancienne iframe s'il en existe une
			const existingIframe = document.querySelector('#gameFrame');
			if (existingIframe) {
				existingIframe.remove();
			}

			iframe.id = "gameFrame";
			document.body.appendChild(iframe);
		} catch (error) {
			console.error(error.message);
			setErrorMessage(error.message); // Afficher l'erreur à l'utilisateur
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		const handleGameFinished = (event) => {
			if (event.data === 'game_end') {
				// Supprimer l'iframe lorsque le jeu est terminé
				const iframe = document.querySelector('#gameFrame');
				if (iframe) {
					iframe.remove();
				}
			}
		};

		// Ajouter l'écouteur d'événements
		window.addEventListener('message', handleGameFinished);

		// Nettoyer l'écouteur d'événements lorsqu'on quitte le composant
		return () => {
			window.removeEventListener('message', handleGameFinished);
		};
	}, []);

	return (
		<>
			{!loading && (
				<button onClick={handlePlayButton} style={{ marginTop: "10px" }}>
					Play {gameMode}
				</button>
			)}
			{loading && <p>Waiting...</p>}
			{errorMessage && <p style={{ color: 'red' }}>Error: {errorMessage}</p>}
		</>
	);
};

export default PlayButton;