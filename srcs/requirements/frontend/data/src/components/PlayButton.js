import api from '../services/api.js';
import { useState } from 'react';

const PlayButton = ({ gameMode, modifiers }) => {
	const [loading, setLoading] = useState(false);

    const handlePlayButton = async () => {
        try {
			setLoading(true);
            const mods = modifiers.join(",");
            const response = await api.get(`/game_manager/matchmaking/game_mode=${gameMode}?mods=${mods}`);
            const gameId = response.data['data']['game_id'];
            if (!gameId) throw new Error('Game ID is missing from the response.');

            if (!window.gameInfo) {
                window.gameInfo = {};
            }
            window.gameInfo.gameId = gameId;

            const host = window.location.hostname;
            const port = window.location.port;
            const scriptUrl = `http://${host}:${port}/api/pong/static/pong/main.js`;

            const script = document.createElement('script');
            script.type = 'module';
            script.src = scriptUrl;
            document.body.appendChild(script);
        } catch (error) {
            console.log(error.message);
        } finally {
			setLoading(false);
		}
    };

    return (
		<>
        	{!loading && <button onClick={handlePlayButton} style={{ marginTop: "10px" }}>
            	Play {gameMode}
        	</button>}
			{loading && <p>Is waiting</p>}
		</>
    );
};

export default PlayButton;
