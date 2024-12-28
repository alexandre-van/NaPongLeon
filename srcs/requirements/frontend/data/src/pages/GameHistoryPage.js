import React, { useState, useEffect } from "react";
import api from "../services/api.js";

const styles = {
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    textAlign: "center",
    padding: "10px",
    borderBottom: "1px solid #ddd",
    backgroundColor: "#f2f2f2",
    fontWeight: "bold",
    color: "black", // Titres en noir
  },
  td: {
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
  },
  dateCell: {
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
    width: "80px", // Reduced width for date
  },
  hourCell: {
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
    width: "80px", // Reduced width for hour
  },
  statusCell: (status) => ({
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
    backgroundColor:
      status === "finished"
        ? "green"
        : status === "aborted"
        ? "red"
        : status === "in_progress"
        ? "blue"
        : status === "loading" || status === "waiting"
        ? "yellow"
        : "transparent",
    color: "white", // Text color to contrast the background
  }),
  gameModeCell: (gameModeColor) => ({
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
    backgroundColor: gameModeColor,
  }),
  row: (isExpanded) => ({
    cursor: "pointer",
    backgroundColor: isExpanded ? "white" : "transparent",
    color: isExpanded ? "black" : "inherit",
    border: isExpanded ? "1px solid #ccc" : "none",
    boxShadow: isExpanded ? "0px 4px 6px rgba(0, 0, 0, 0.1)" : "none",
    transition: "background-color 0.3s ease, box-shadow 0.3s ease",
  }),
  expandedCell: {
    padding: "10px",
    borderBottom: "1px solid #ddd",
    backgroundColor: "#f9f9f9",
    border: "1px solid #ddd",
    borderRadius: "5px",
    color: "#333",
    fontSize: "14px",
  },
  filterDropdown: {
    margin: "10px auto",
    padding: "8px 15px",
    fontSize: "16px",
    backgroundColor: "#222",
    color: "white",
    border: "1px solid #444",
    borderRadius: "5px",
    cursor: "pointer",
    display: "block",
    width: "200px",
    textAlign: "center",
  },
};

const containerStyle = {
  marginBottom: "30px",
};

export default function GameHistory() {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [filterMode, setFilterMode] = useState("all");
  const [expandedGame, setExpandedGame] = useState(null);
  const [gameModeColors, setGameModeColors] = useState({});

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get("/game_manager/get_history/");
        const gameHistory = response.data["game_history"];
        if (!gameHistory || Object.keys(gameHistory).length === 0) {
          setHistory([]);
        } else {
          const formattedHistory = Object.entries(gameHistory).map(
            ([date, data]) => ({
              game_date: new Date(data.game_date).toLocaleDateString("fr-FR"),
              game_time: new Date(data.game_date).toLocaleTimeString("fr-FR", {
                hour: "2-digit",
                minute: "2-digit",
              }),
              game_mode: data.game_mode,
              status: data.status,
              scores: data.scores || { left: 0, right: 0 },
              teams: {
                left: data.teams?.left || [],
                right: data.teams?.right || [],
              },
              winner:
                data.winner && data.teams?.[data.winner]
                  ? data.teams[data.winner].join(", ")
                  : "No winner",
              result:
                data.winner === "left"
                  ? "WIN"
                  : data.winner === "right"
                  ? "LOOSE"
                  : "No result",
              game_id: data.game_id,
            })
          );
          setHistory(formattedHistory);
        }
      } catch (err) {
        setError(err.message);
      }
    };

    fetchHistory();
  }, []);

  useEffect(() => {
    const modes = Array.from(new Set(history.map((game) => game.game_mode)));
    const colors = {};
    modes.forEach(
      (mode) => (colors[mode] = `#${Math.floor(Math.random() * 16777215).toString(16)}`)
    );
    setGameModeColors(colors);
  }, [history]);

  const filteredHistory = history.filter((game) => {
    if (filterMode === "all") return true;
    return game.game_mode === filterMode;
  });

  const handleExpand = (gameId) => {
    setExpandedGame((prev) => (prev === gameId ? null : gameId));
  };

  const getScoreColor = (team) => (team === "left" ? "green" : "red");
  const getResultColor = (result) => (result === "WIN" ? "green" : "red");

  return (
    <div>
      <h1>Game History</h1>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <div style={{ marginBottom: "20px" }}>
        <label>
          Filter by Mode:
          <select
            value={filterMode}
            onChange={(e) => setFilterMode(e.target.value)}
            style={styles.filterDropdown}
          >
            <option value="all">All</option>
            {Array.from(new Set(history.map((game) => game.game_mode))).map((mode) => (
              <option key={mode} value={mode}>
                {mode}
              </option>
            ))}
          </select>
        </label>
      </div>

      {filteredHistory.length > 0 ? (
        <div style={containerStyle}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>DATE</th>
                <th style={styles.th}>HOUR</th>
                <th style={styles.th}>GAME MODE</th>
                <th style={styles.th}>STATUS</th>
                <th style={styles.th}>SCORE</th>
                <th style={styles.th}>RESULT</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.map((game) => (
                <React.Fragment key={game.game_id}>
                  <tr
                    onClick={() => handleExpand(game.game_id)}
                    style={styles.row(expandedGame === game.game_id)}
                  >
                    <td style={styles.dateCell}>{game.game_date}</td>
                    <td style={styles.hourCell}>{game.game_time}</td>
                    <td
                      style={styles.gameModeCell(gameModeColors[game.game_mode])}
                    >
                      {game.game_mode}
                    </td>
                    <td
                      style={{
                        ...styles.td,
                        color: game.status === "finished"
                          ? "green"
                          : game.status === "aborted"
                          ? "red"
                          : game.status === "in_progress"
                          ? "blue"
                          : game.status === "loading" || game.status === "waiting"
                          ? "yellow"
                          : "black", // couleur par défaut
                      }}
                    >
                      {game.status}
                    </td>
                    <td
                      style={{
                        ...styles.td,
                        color: getScoreColor(game.winner),
                      }}
                    >
                      {game.scores.left} - {game.scores.right}
                    </td>
                    <td
                      style={{
                        ...styles.td,
                        color: getResultColor(game.result),
                      }}
                    >
                      {game.result}
                    </td>
                  </tr>
                  {expandedGame === game.game_id && (
                    <tr>
                      <td colSpan="6" style={styles.expandedCell}>
                        <strong>Team Left:</strong> {game.teams.left.join(", ") || "AI"}{" "}
                        (Score: {game.scores.left})
                        <br />
                        <strong>Team Right:</strong> {game.teams.right.join(", ") || "AI"}{" "}
                        (Score: {game.scores.right})
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>No game history found.</p>
      )}
    </div>
  );
}
