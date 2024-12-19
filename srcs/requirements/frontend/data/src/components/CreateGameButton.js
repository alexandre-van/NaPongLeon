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
                gameMode: 'PONG_CLASSIC',
                modifiers: mods,
                playersList: [user.username],
                teamsList: [[user.username], []],
                ia_authorizes: true,
            };

            const response = await api.post('/game_manager/create_game/', gameParams);
            const gameId = response.data.data.game_id;
            if (!gameId) throw new Error('Game ID is missing from the response.');

            const gameServiceName = response.data.data.service_name;
            if (!gameServiceName) throw new Error('Game service name is missing from the response.');

            if (!window.gameInfo) window.gameInfo = {};
            window.gameInfo.gameId = gameId;

            const gameUrl = `${location.origin}/api/${gameServiceName}/?gameId=${gameId}`;

            // Remove existing iframe if any
            const existingIframe = document.querySelector('#gameFrame');
            if (existingIframe) existingIframe.remove();

            // Create and configure the iframe
            const iframe = document.createElement('iframe');
            iframe.src = gameUrl;
            iframe.id = "gameFrame";
            iframe.style.position = "fixed";
            iframe.style.top = "75px";
            iframe.style.left = "0";
            iframe.style.width = "100vw";
            iframe.style.height = "calc(100vh - 75px)";
            iframe.style.border = "none";
            iframe.style.zIndex = "9999";
            iframe.sandbox = "allow-scripts allow-same-origin";

            // Disable scrolling inside the iframe
            iframe.scrolling = "no";

            // Prevent scrolling on the page
            document.documentElement.style.overflow = "hidden";
            document.body.style.overflow = "hidden";
            document.body.style.margin = "0";
            document.body.style.padding = "0";

            // Add the iframe to the document
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
