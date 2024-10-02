import api from '../services/api.js';

const PlayButton = () => {
    
    const handlePlayButton = async () => {
        try {
            //const response = await api.get('/pong/');
            const response = await api.get('/game_manager/matchmaking/');
            const script = document.createElement('script');
            script.type = 'module';
            script.src = response.data.match(/src="([^"]+)"/)[1]; // Extrait le chemin du script
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