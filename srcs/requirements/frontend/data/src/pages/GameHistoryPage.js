import { useState, useEffect } from "react";
import api from "../services/api.js";

export default function GameHistory() {
  const [history, setHistory] = useState([]); // Stores the game history
  const [error, setError] = useState(null); // Stores potential errors

  useEffect(() => {
    // Function to fetch data from the API
    const fetchHistory = async () => {
      try {
        const response = await api.get("/game_manager/get_history/");
        const gameHistory = response.data["game_history"];

        if (!gameHistory || Object.keys(gameHistory).length === 0) {
          setHistory([]); // No history found
        } else {
          // Transform the object into a list with the important information
          const formattedHistory = Object.entries(gameHistory).map(([date, data]) => ({
            game_date: new Date(date).toLocaleString("en-US"), // Formats the date
            game_mode: data.game_mode,
            status: data.status,
            scores: data.scores || { left: 0, right: 0 }, // Default values if scores are missing
            teams: {
              left: data.teams?.left || [], // Use an empty array if teams.left is undefined
              right: data.teams?.right || [], // Use an empty array if teams.right is undefined
            },
            winner: data.winner ? data.winner : "No winner",
          }));
          setHistory(formattedHistory);
        }
      } catch (err) {
        setError(err.message);
      }
    };

    fetchHistory();
  }, []); // [] means this function runs only on component mount

  return (
    <div>
      <h1>Game History</h1>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {history.length > 0 ? (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {history.map((game, index) => (
            <li
              key={index}
              style={{
                marginBottom: "15px",
                border: "1px solid #ddd",
                padding: "10px",
                borderRadius: "5px",
              }}
            >
              <p>
                <strong>Date:</strong> {game.game_date}
              </p>
              <p>
                <strong>Game Mode:</strong> {game.game_mode}
              </p>
              <p>
                <strong>Status:</strong>{" "}
                {game.status === "aborted" ? "Aborted" : "Completed"}
              </p>
              <p>
                <strong>Teams:</strong> Left (
                {game.teams.left.length > 0
                  ? game.teams.left.join(", ")
                  : "AI"}
                ) vs Right (
                {game.teams.right.length > 0
                  ? game.teams.right.join(", ")
                  : "AI"}
                )
              </p>
              <p>
                <strong>Score:</strong> {game.scores.left} - {game.scores.right}
              </p>
              <p>
                <strong>Winner:</strong> {game.winner}
              </p>
            </li>
          ))}
        </ul>
      ) : (
        <p>No game history found.</p>
      )}
    </div>
  );
}
