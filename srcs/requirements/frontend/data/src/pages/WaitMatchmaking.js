import { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { useNavigate } from 'react-router-dom';

export default function WaitMatchmaking() {
    const navigate = useNavigate();
    const location = useLocation();
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = window.location.port;
    const { gameMode, modifiers } = location.state || {};
    let game_found = false

    useEffect(() => {
        console.log("Initializing WebSocket connection...");
        const ws = new WebSocket(`${wsProtocol}//${host}${port ? `:${port}` : ''}/ws/matchmaking/`);

        ws.onopen = () => {
            console.log("WebSocket connected");
            ws.send(JSON.stringify({ "action": "join_matchmaking", "game_mode": gameMode, "modifiers": modifiers }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data);
            if (data.status === "game_found") {
                game_found = true
                console.log("game_found:", data);
                navigate("/pong/ingame", { state: { gameService: `${location.origin}/api/${data.service_name}`, gameId: data.game_id } });
            }
        };

        ws.onclose = () => {
            console.log("WebSocket closed");
            if (game_found == null)
                navigate("/pong")
        };

        return () => {
            console.log("Cleaning up WebSocket...");
            ws.close();
        };
    }, []);

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
                    <Link to="/pong">
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
