import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import api from "../services/api.js";

const styles = {
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    textAlign: "center",
    padding: "10px",
    borderBottom: "2px solid #ddd",
    backgroundColor: "#f2f2f2",
    fontWeight: "bold",
    color: "black",
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
    width: "80px",
  },
  hourCell: {
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
    width: "80px",
  },
  statusCell: (status) => ({
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
    color: status === "finished"
      ? "#4CAF50"  // vert
      : status === "aborted"
      ? "#f44336"  // rouge
      : status === "in_progress"
      ? "#2196F3"  // bleu
      : status === "loading" || status === "waiting"
      ? "#FFC107"  // jaune
      : "#ffffff",  // blanc par défaut
  }),
  gameModeCell: (gameModeColor) => ({
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
    backgroundColor: gameModeColor,
  }),
  resultCell: (result) => ({
    padding: "10px",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
    verticalAlign: "middle",
    color: result === "WIN"
      ? "#4CAF50"  // vert
      : result === "LOSE"
      ? "#f44336"  // rouge
      : result === "Equality"
      ? "#2196F3"  // bleu
      : "#ffffff",  // blanc pour "No result"
  }),
  row: (isExpanded) => ({
    cursor: "pointer",
    backgroundColor: "transparent",
    transition: "background-color 0.3s ease",
  }),
  teamName: (color) => ({
    padding: "4px 8px",
    borderRadius: "4px",
    backgroundColor: color,
    color: "black",
    fontWeight: "bold",
  }),
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

const getRandomPastelColor = () => {
  const hue = Math.floor(Math.random() * 360);
  return `hsl(${hue}, 70%, 90%)`;  // Soft pastel colors
};

export default function GameHistory() {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [filterMode, setFilterMode] = useState("all");
  const [expandedGame, setExpandedGame] = useState(null);
  const [hoveredGameId, setHoveredGameId] = useState(null);
  const [gameModeColors, setGameModeColors] = useState({});
  const [teamColors, setTeamColors] = useState({});
  const location = useLocation();

  // Récupérer le username du state ou des paramètres d'URL
  const username = location.state?.username || ""; // Par défaut, pas de username

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const endpoint = `/game_manager/get_history/username=${username}`
        const response = await api.get(endpoint);
        const gameHistory = response.data["game_history"];
        if (!gameHistory || Object.keys(gameHistory).length === 0) {
          setHistory([]);
        } else {
          const formattedHistory = Object.entries(gameHistory)
            .map(([date, data]) => ({
              game_date: new Date(data.game_date),
              game_time: new Date(data.game_date).toLocaleTimeString("fr-FR", {
                hour: "2-digit",
                minute: "2-digit",
              }),
              game_mode: data.game_mode,
              status: data.status,
              scores: data.scores || {},
              teams: data.teams || {},
              winner: data.winner && data.teams?.[data.winner]
                ? data.teams[data.winner].join(", ")
                : "No winner",
              result: data.self_team === data.winner
                ? "WIN"
                : data.winner && data.self_team !== data.winner
                ? "LOSE"
                : "No result",
              self_team: data.self_team,
              game_id: data.game_id,
            }))
            .sort((a, b) => b.game_date - a.game_date);
          setHistory(formattedHistory);
        }
      } catch (err) {
        setError(err.message);
      }
    };

    fetchHistory();
  }, [username]);

  useEffect(() => {
    const modes = Array.from(new Set(history.map((game) => game.game_mode)));
    const colors = {};
    modes.forEach((mode) => (colors[mode] = `#${Math.floor(Math.random() * 16777215).toString(16)}`));
    setGameModeColors(colors);

    const teamColorsMap = {};
    history.forEach((game) => {
      Object.keys(game.teams).forEach((team) => {
        if (!teamColorsMap[team]) {
          teamColorsMap[team] = getRandomPastelColor();
        }
      });
    });
    setTeamColors(teamColorsMap);
  }, [history]);

  const filteredHistory = history.filter((game) => {
    if (filterMode === "all") return true;
    return game.game_mode === filterMode;
  });

  const handleExpand = (gameId) => {
    setExpandedGame((prev) => (prev === gameId ? null : gameId));
  };

  const handleMouseEnter = (gameId) => {
    setHoveredGameId(gameId);
  };

  const handleMouseLeave = () => {
    setHoveredGameId(null);
  };

  const renderTeams = (game) => {
    const teams = Object.keys(game.teams).sort(
      (a, b) => game.scores[b] - game.scores[a]
    );

    return (
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ ...styles.th, backgroundColor: "black", width: "11%" }}></th>
            <th style={{ ...styles.th, width: "32%" }}>TEAM NAME</th>
            <th style={{ ...styles.th, width: "33%" }}>PLAYERS</th>
            <th style={{ ...styles.th, width: "24%" }}>SCORE</th>
          </tr>
        </thead>
        <tbody>
          {teams.map((team) => (
            <tr key={team}>
              <td style={{ ...styles.td, backgroundColor: "black", width: "80px" }}></td>
              <td style={{
                ...styles.td,
                backgroundColor: teamColors[team] || getRandomPastelColor(),
                color: "black",
                fontWeight: "bold",
              }}>
                {team.toUpperCase()}
              </td>
              <td style={{ ...styles.td, width: "35%", backgroundColor: "grey" }}>
                {game.teams[team].join(", ") || "AI"}
              </td>
              <td style={{ ...styles.td, width: "20%", backgroundColor: "grey" }}>
                {game.scores[team]}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div>
      <div className="profile" style={{ paddingTop: '50px' }}></div>
      <h1>
        {username ? `${username}'s Game History` : "Game History"}
      </h1>
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
        <div>
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
                    onMouseEnter={() => handleMouseEnter(game.game_id)}
                    onMouseLeave={handleMouseLeave}
                    style={{
                      ...styles.row(expandedGame === game.game_id),
                      backgroundColor: hoveredGameId === game.game_id ? "#f0f0f0" : "transparent",
                    }}
                  >
                    <td style={styles.dateCell}>
                      {game.game_date.toLocaleDateString("fr-FR")}
                    </td>
                    <td style={styles.hourCell}>{game.game_time}</td>
                    <td style={styles.gameModeCell(gameModeColors[game.game_mode])}>
                      {game.game_mode}
                    </td>
                    <td style={styles.statusCell(game.status)}>{game.status}</td>
                    <td style={styles.td}>{game.scores.left} - {game.scores.right}</td>
                    <td style={styles.resultCell(game.result)}>{game.result}</td>
                  </tr>
                  {expandedGame === game.game_id && (
                    <tr>
                      <td colSpan="6" style={{ padding: "0" }}>
                        {renderTeams(game)}
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