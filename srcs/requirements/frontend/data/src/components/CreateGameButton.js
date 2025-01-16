import { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';
import { useNavigate } from "react-router-dom";

const CreateGameButton = ({ gameMode, modifiers }) => {
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState(null);
    const { user } = useUser();
    const navigate = useNavigate();

    const handlePlayButton = async () => {
        try {
            setLoading(true);
            setErrorMessage(null); // Reset error message before starting

            const mods = modifiers.join(",");
            const gameParams = {
                gameMode: 'PONG_CLASSIC_AI',
                modifiers: mods,
                playersList: [user.username],
                ia_authorizes: true,
            };

            const response = await api.post('/game_manager/create_game/', gameParams);
            const data = response.data.data;
            navigate("/pong/ingame", { state: { gameService: `${location.origin}/api/${data.service_name}`, gameId: data.game_id } });
            
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
            await api.get('/game_manager/matchmaking/cancel');
            
            const iframe = document.querySelector('#gameFrame');
            if (iframe) iframe.remove();

            // Re-enable scrolling if iframe is removed
            document.documentElement.style.overflow = "auto";
            document.body.style.overflow = "auto";
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
                const iframe = document.querySelector('#gameFrame');
                if (iframe) iframe.remove();

                // Re-enable scrolling when game ends
                document.documentElement.style.overflow = "auto";
                document.body.style.overflow = "auto";
            }
        };

        window.addEventListener('message', handleGameFinished);

        return () => {
            window.removeEventListener('message', handleGameFinished);
            const iframe = document.querySelector('#gameFrame');
            if (iframe) iframe.remove();

            // Cleanup scrolling behavior
            document.documentElement.style.overflow = "auto";
            document.body.style.overflow = "auto";
        };
    }, []);

    return (
        <>
            {!loading && (
                <button
                    className="play-button-mode btn btn-outline-warning"
                    onClick={handlePlayButton}
                    style={{ marginTop: "10px" }}
                >
                    Play VS AI
                </button>
            )}

            {loading && (
                <>
                    <p>
                        Waiting...
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
                        </button>
                    </p>
                </>
            )}

            {errorMessage && <p style={{ color: 'red' }}>Error: {errorMessage}</p>}
        </>
    );
};

export default CreateGameButton;
