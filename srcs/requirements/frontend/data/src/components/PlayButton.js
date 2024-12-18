import { useState, useEffect } from 'react';
import api from '../services/api.js';
import { useNavigate } from "react-router-dom";


const PlayButton = ({ gameMode, modifiers, number='' }) => {
	const [loading, setLoading] = useState(false);
	const [errorMessage, setErrorMessage] = useState(null);
	const navigate = useNavigate();

	const handlePlayButton = async () => {
		try {
			setLoading(true);
			setErrorMessage(null);

			let mods = modifiers.join(",");
			const response = await api.get(`/game_manager/matchmaking/game_mode=${gameMode}?mods=${mods}&playernumber=${number}`, 3600000);
			const gameId = response.data['data']['game_id'];
			if (!gameId) return;
			const gameServiceName = response.data['data']['service_name'];
			if (!gameServiceName) throw new Error('Game service name is missing from the response.');
			if (!window.gameInfo) {
				window.gameInfo = {};
			}
			window.gameInfo.gameId = gameId;

			const gameUrl = `${location.origin}/api/${gameServiceName}/?gameId=${gameId}`;

			navigate("/ingame");

			console.log(gameUrl);
			const iframe = document.createElement('iframe');
			iframe.src = gameUrl;
			iframe.style.position = "fixed";
			iframe.style.top = "75px";
			iframe.style.left = "0";
			iframe.style.width = "100vw";
			iframe.style.height = "93vh";
			iframe.style.border = "none";
			iframe.style.zIndex = "9999";
			iframe.sandbox = "allow-scripts allow-same-origin";

			const existingIframe = document.querySelector('#gameFrame');
			if (existingIframe) {
				existingIframe.remove();
			}
			iframe.id = "gameFrame";
			document.body.appendChild(iframe);
		} catch (error) {
			console.error(error.message);
			setErrorMessage(error.message);
		} finally {
			setLoading(false);
		}
	};

	const handleCancelMatchmaking = async () => {
		try {
			setLoading(true);
			setErrorMessage(null);
			const game_mode = "";
			await api.get(`/game_manager/matchmaking/game_mode=${game_mode}`);
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
					Play {gameMode}
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

export default PlayButton;