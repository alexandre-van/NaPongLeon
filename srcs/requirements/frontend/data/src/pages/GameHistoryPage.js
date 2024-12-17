import { useState, useEffect } from 'react';
import api from '../services/api.js';

export default function GameHistory() {
  const [history, setHistory] = useState([]); // Stocke l'historique des jeux
  const [error, setError] = useState(null);  // Stocke les erreurs éventuelles

  useEffect(() => {
    // Fonction pour récupérer les données depuis l'API
    const fetchHistory = async () => {
      try {
        const response = await api.get("/game_manager/get_history/");
        console.log(response.data['game_history']); // Debug
        const gameHistory = response.data['game_history']; // Récupère la propriété 'game_history'
        if (!gameHistory || Object.keys(gameHistory).length === 0) {
          setHistory([]); // Aucun historique trouvé
        } else {
          // Transforme l'objet en une liste triée par date
          const formattedHistory = Object.entries(gameHistory).map(([date, data]) => ({
            game_date: date,
            ...data,
          }));
          setHistory(formattedHistory);
        }
      } catch (err) {
        setError(err.message); // Capture les erreurs
      }
    };

    fetchHistory();
  }, []); // [] signifie que cette fonction ne s'exécute qu'au montage du composant

  return (
    <div>
      <h1>Game History</h1>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      <ul>
        {history.length > 0 ? (
          history.map((game, index) => (
            <li key={index}>
              <strong>{game.game_date}:</strong> {JSON.stringify(game)}
            </li>
          ))
        ) : (
          <p>No game history found.</p>
        )}
      </ul>
    </div>
  );
}
