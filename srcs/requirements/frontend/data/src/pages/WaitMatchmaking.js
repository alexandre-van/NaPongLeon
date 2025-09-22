import { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { useNavigate } from "react-router-dom";

export default function WaitMatchmaking() {
    const navigate = useNavigate();
    const location = useLocation();
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.hostname;
    const port = window.location.port;
    const { gameMode, modifiers, hasCompetitors, checkedBox } = location.state || {};
    let game_found = false;

    useEffect(() => {
        console.log("Initializing WebSocket connection...");
        const ws = new WebSocket(`${wsProtocol}//${host}${port ? `:${port}` : ""}/ws/matchmaking/`);

        ws.onopen = () => {
            console.log("WebSocket connected");
            ws.send(
                JSON.stringify({
                    action: "join_matchmaking",
                    game_mode: gameMode,
                    modifiers: modifiers,
                    number_of_players: checkedBox,
                })
            );
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data);
            if (data.status === "game_found") {
                game_found = true;
                console.log("game_found:", data, window.location.protocol);
                navigate("/pong/ingame", {
                    state: {
                        gameService: `${window.location.protocol}/api/${data.service_name}`,
                        gameId: data.game_id,
                    },
                });
            }
        };

        ws.onclose = () => {
            console.log("WebSocket closed");
            if (!game_found) navigate("/pong");
        };

        return () => {
            ws.close();
        };
    }, []);

    const handleCancelMatchmaking = () => {
        console.log("Matchmaking cancelled");
    };

    return (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%" }}>
            <div style={{ textAlign: "center" }}>
                <h1>MATCHMAKING...</h1>
                <div style={{ marginBottom: "20px" }}>
                    <p>Game Mode: {gameMode || "N/A"}</p>
                    <p>Modifiers: {modifiers || "None"}</p>
                </div>
                {hasCompetitors && (
                    <div style={{ marginBottom: "20px" }}>
                        <p>Number of team: {checkedBox}</p>
                    </div>
                )}
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
        </div>
    );
}
