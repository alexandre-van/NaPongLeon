import api from '../services/api.js';

const PlayButton = () => {
	
	const handlePlayButton = async () => {
		try {
			//const response = await api.get('/pong/');
			const response = await api.get('/game_manager/matchmaking/game_mode=PONG_CLASSIC?mods=random_speed');
			const gameId = response.data['data']['game_id'];
			if (!gameId)
				throw new Error('Game ID is missing from the response.');
            if (!window.gameInfo) {
                window.gameInfo = {};
            }
            window.gameInfo.gameId = gameId;
			const host = window.location.hostname;
			const port = window.location.port;
			// URL du script que vous souhaitez charger
			const scriptUrl = `http://${host}:${port}/api/pong/static/pong/main.js`; // Mettez ici votre URL de script

			// Créer et ajouter le script
			const script = document.createElement('script');
			script.type = 'module'; // Si votre script est un module
			script.src = scriptUrl;
			document.body.appendChild(script);
		} catch (error) {  
			console.log(error.message);
		}
	};

	return (
		<button onClick={handlePlayButton}>
			Play Button
		</button>
	);
};

export default PlayButton;