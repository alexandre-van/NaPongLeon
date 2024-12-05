import { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';
import { useNavigate } from "react-router-dom";

const CreateGameButton = ({ gameMode, modifiers }) => {
	const [loading, setLoading] = useState(false);
	const [errorMessage, setErrorMessage] = useState(null);
	const { user, getAvatarUrl } = useUser();
	const navigate = useNavigate();

	const handlePlayButton = async () => {
		try {
			setLoading(true);
			setErrorMessage(null); // Reset error message before starting

			const mods = modifiers.join(",");
			const game_params = {
				'gameMode': 'PONG_CLASSIC',
				'modifiers': mods,
				'playersList': [user.username],
				'teamsList': [[user.username],[]],
				'ia_authorizes': true
			};
			const response = await api.post('/game_manager/create_game/', game_params)
			const gameId = response.data['data']['game_id'];
			if (!gameId) throw new Error('Game ID is missing from the response.');
			const gameServiceName = response.data['data']['service_name'];
			if (!gameServiceName) throw new Error('Game service name is missing from the response.');
			// Stocker le gameId dans window.gameInfo
			if (!window.gameInfo) {
				window.gameInfo = {};
			}
			window.gameInfo.gameId = gameId;

			// Construire l'URL du jeu avec le gameId
			const host = window.location.hostname;
			const port = window.location.port;
			const gameUrl = `http://${host}:${port}/api/${gameServiceName}?gameId=${gameId}`;

			//navigate("/ingame");

			// Créer une iframe pour afficher le jeu
			const iframe = document.createElement('iframe');
			iframe.src = gameUrl;
			iframe.style.position = "fixed"; // Fixe pour qu'il reste à la même position
			iframe.style.top = "75px";                 // Aligner en haut de la page
			iframe.style.left = "0";                // Aligner à gauche de la page
			iframe.style.width = "100vw";           // Largeur : 100% de la fenêtre
			iframe.style.height = "93vh"; // Hauteur : 100% de la fenêtre moins la hauteur de la barre
			iframe.style.border = "none";           // Supprimer les bordures
			iframe.style.zIndex = "9999";           // Mettre l'iframe au premier plan


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

	const handleCancelMatchmaking = async () => {
		try {
			setLoading(true);
			setErrorMessage(null); // Reset error message before starting
			const game_mode = "";
			await api.get(`/game_manager/matchmaking/game_mode=${game_mode}`);

			// Optionnel : retirer l'iframe en cas d'annulation
			const iframe = document.querySelector('#gameFrame');
			if (iframe) {
				iframe.remove();
			}
		} catch (error) {
			console.error("Failed to cancel matchmaking:", error.message);
			setErrorMessage(error.message);
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
			const existingIframe = document.querySelector('#gameFrame');
			if (existingIframe) {
			  existingIframe.remove();
			}
		};
	}, []);

	return (
		<>
			{/* Bouton "Play" visible uniquement quand pas en chargement */}
			{!loading && (
				<button onClick={handlePlayButton} style={{ marginTop: "10px" }}>
					Play VS AI
				</button>
			)}

			{/* Bouton en croix visible uniquement pendant le chargement */}
			{loading && (
				<>
					<p>Waiting...
					<button
						onClick={handleCancelMatchmaking}
						style={{
							marginLeft: "10px",
							background: "red",
							color: "white",
							border: "none",
							borderRadius: "50%",
							width: "30px",
							height: "30px",
							cursor: "pointer",
						}}
					>
						X
					</button></p>
				</>
			)}

			{/* Message d'erreur */}
			{errorMessage && <p style={{ color: 'red' }}>Error: {errorMessage}</p>}
		</>
	);
};

export default CreateGameButton;