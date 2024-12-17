import { useState, useEffect } from "react";
import api from "../services/api.js";

export default function GameHistory() {
  const [history, setHistory] = useState([]); // Stocke l'historique des jeux
  const [error, setError] = useState(null); // Stocke les erreurs éventuelles

  useEffect(() => {
    // Fonction pour récupérer les données depuis l'API
    const fetchHistory = async () => {
      try {
        const response = await api.get("/game_manager/get_history/");
        const gameHistory = response.data["game_history"];

        if (!gameHistory || Object.keys(gameHistory).length === 0) {
          setHistory([]); // Aucun historique trouvé
        } else {
          // Transformer l'objet en liste avec les informations importantes
          const formattedHistory = Object.entries(gameHistory).map(([date, data]) => ({
            game_date: new Date(date).toLocaleString("fr-FR"), // Formate la date
            game_mode: data.game_mode,
            status: data.status,
            scores: data.scores || { left: 0, right: 0 }, // Valeurs par défaut si scores manquent
            teams: {
              left: data.teams?.left || [], // Utilise un tableau vide si teams.left est undefined
              right: data.teams?.right || [], // Utilise un tableau vide si teams.right est undefined
            },
            winner: data.winner ? data.winner : "Aucun gagnant",
          }));
          setHistory(formattedHistory);
        }
      } catch (err) {
        setError(err.message);
      }
    };

    fetchHistory();
  }, []); // [] signifie que cette fonction ne s'exécute qu'au montage du composant

  return (
    <div>
      <h1>Historique des Parties</h1>
      {error && <p style={{ color: "red" }}>Erreur: {error}</p>}
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
                <strong>Date :</strong> {game.game_date}
              </p>
              <p>
                <strong>Mode de jeu :</strong> {game.game_mode}
              </p>
              <p>
                <strong>Statut :</strong>{" "}
                {game.status === "aborted" ? "Annulé" : "Terminé"}
              </p>
              <p>
                <strong>Équipes :</strong> Gauche (
                {game.teams.left.length > 0
                  ? game.teams.left.join(", ")
                  : "IA"}
                ) vs Droite (
                {game.teams.right.length > 0
                  ? game.teams.right.join(", ")
                  : "IA"}
                )
              </p>
              <p>
                <strong>Score :</strong> {game.scores.left} - {game.scores.right}
              </p>
              <p>
                <strong>Gagnant :</strong> {game.winner}
              </p>
            </li>
          ))}
        </ul>
      ) : (
        <p>Aucun historique de jeu trouvé.</p>
      )}
    </div>
  );
}
