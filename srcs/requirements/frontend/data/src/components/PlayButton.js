import { useState, useEffect, useRef } from 'react';
import { useNavigate } from "react-router-dom";

const PlayButton = ({ gameMode, modifiers, number = '' }) => {
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState(null);
    const navigate = useNavigate();
    const wsRef = useRef(null);

    useEffect(() => {
        // Nettoyage lors du démontage du composant
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            const existingIframe = document.querySelector('#gameFrame');
            if (existingIframe) {
                existingIframe.remove();
            }
        };
    }, []);

    const connectWebSocket = () => {
        const ws = new WebSocket(`ws://${window.location.host}/ws/matchmaking/`);
        
        ws.onopen = () => {
            console.log('WebSocket connection established');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);

            switch(data.status) {
                case 'queued':
                    console.log('En file d\'attente...');
                    break;
                case 'game_found':
                    handleGameFound(data);
                    break;
                case 'error':
                    setErrorMessage(data.message);
                    setLoading(false);
                    break;
                default:
                    console.log('Message non géré:', data);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setErrorMessage('Connection error');
            setLoading(false);
        };

        ws.onclose = () => {
            console.log('WebSocket connection closed');
            setLoading(false);
        };

        return ws;
    };

    const handleGameFound = (data) => {
        const { game_id, service_name } = data;
        if (!game_id || !service_name) {
            setErrorMessage('Invalid game data received');
            setLoading(false);
            return;
        }

        // Sauvegarder l'ID de la partie
        if (!window.gameInfo) {
            window.gameInfo = {};
        }
        window.gameInfo.gameId = game_id;

        // Créer et ajouter l'iframe
        navigate("/ingame");
        const gameUrl = `${location.origin}/api/${service_name}/?gameId=${game_id}`;
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
        iframe.scrolling = "no";
        iframe.id = "gameFrame";

        const existingIframe = document.querySelector('#gameFrame');
        if (existingIframe) {
            existingIframe.remove();
        }

        document.body.appendChild(iframe);
        setLoading(false);
    };

    const handlePlayButton = () => {
        try {
            setLoading(true);
            setErrorMessage(null);

            if (wsRef.current) {
                wsRef.current.close();
            }

            wsRef.current = connectWebSocket();
            wsRef.current.onopen = () => {
                wsRef.current.send(JSON.stringify({
                    action: 'join_matchmaking',
                    game_mode: gameMode,
                    modifiers: modifiers.join(','),
                    number_of_players: number
                }));
            };
        } catch (error) {
            console.error(error.message);
            setErrorMessage(error.message);
            setLoading(false);
        }
    };

    const handleCancelMatchmaking = () => {
        if (wsRef.current) {
            wsRef.current.send(JSON.stringify({
                action: 'leave_matchmaking'
            }));
            wsRef.current.close();
            wsRef.current = null;
        }
        setLoading(false);

        const iframe = document.querySelector('#gameFrame');
        if (iframe) {
            iframe.remove();
        }
    };

    useEffect(() => {
        const handleGameFinished = (event) => {
            if (event.data === 'game_end') {
                const iframe = document.querySelector('#gameFrame');
                if (iframe) {
                    iframe.remove();
                }
                if (wsRef.current) {
                    wsRef.current.close();
                    wsRef.current = null;
                }
            }
        };

        window.addEventListener('message', handleGameFinished);
        return () => {
            window.removeEventListener('message', handleGameFinished);
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
                    Play {gameMode}
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

export default PlayButton;