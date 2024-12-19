import { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { useNavigate } from 'react-router-dom';

export default function WaitMatchmaking() {
	const navigate = useNavigate();
    const location = useLocation();
    const { gameMode, modifiers } = location.state || {};

    useEffect(() => {
        const ws = new WebSocket("wss://localhost:8443/ws/matchmaking/");

        ws.onopen = () => {
            console.log("WebSocket connected");
            ws.send(JSON.stringify({ "action": "join_matchmaking", "game_mode": gameMode, "modifiers": modifiers }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
			console.log(data);
            if (data.status === "game_found") {
                console.log("game_found:", data);
                navigate("/ingame", { state: { gameService: `https://localhost:8443/api/${data.service_name}`, gameId: data.game_id } });
            }
        };

        ws.onclose = () => {
            console.log("WebSocket closed");
        };

        return () => {
            ws.close();
        };
    }, [gameMode, modifiers]);

    const handleCancelMatchmaking = () => {
        console.log("Matchmaking cancelled");
    };

    return (
        <div>
            <div>
                <p>MATCHMAKING...</p>
            </div>
            <div>
                <p>
                    Waiting...
                    <Link to="/">
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
                    </Link>
                </p>
            </div>
        </div>
    );
}
