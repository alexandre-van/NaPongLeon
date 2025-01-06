import { useEffect, useState } from 'react';
import api from "../services/api.js"; // Service API
import { useUser } from '../contexts/UserContext.js';
import { Link } from 'react-router-dom';
import FriendsList from '../components/FriendsList.js';

export default function Formations() {
    const { user } = useUser();
    const [playerStatus, setPlayerStatus] = useState('Loading...'); // État pour le statut du joueur
    const [gameMode, setGameMode] = useState(null); // État pour le mode de jeu
    const [error, setError] = useState(null);

    useEffect(() => {
        let intervalId; // ID de l'intervalle

        const fetchPlayerStatus = () => {
            api.get(`/game_manager/get_status/username=`)
                .then((response) => {
                    const { status, game_mode } = response.data.data;
                    setPlayerStatus(status); // Mise à jour du statut
                    setGameMode(game_mode || null); // Mise à jour du mode de jeu si disponible
                    setError(null); // Réinitialiser l'erreur en cas de succès
                })
                .catch((err) => {
                    console.error('Erreur lors de la récupération du statut:', err);
                    setError('Impossible de récupérer le statut');
                });
        };

        // Appel initial pour récupérer immédiatement le statut
        fetchPlayerStatus();

        // Définir l'intervalle pour mettre à jour toutes les 10 secondes
        intervalId = setInterval(fetchPlayerStatus, 10000);

        // Nettoyage de l'intervalle à la fin du composant
        return () => clearInterval(intervalId);
    }, [user.username]);

    // Fonction pour déterminer la couleur du statut
    const getStatusColor = (status) => {
        switch (status) {
            case "inactive":
                return "gray";
            case "pending":
                return "orange";
            case "in_queue":
            case "in_game":
                return "blue";
            case "waiting":
            case "loading_game":
                return "yellow";
            default:
                return "black";
        }
    };

    const getStatusTxt = (status) => {
      switch (status) {
          case "inactive":
              return "Inactive";
          case "pending":
              return "Expected in game";
          case "in_queue":
              return "In queue";
          case "in_game":
              return "In game";
          case "waiting":
              return "Waiting";
          case "loading_game":
              return "In game";
          default:
              return "with";
      }
  };

    return (
        <div className="profile">
            <div className="profile-header" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                {/* Avatar avec styles en ligne */}
                <div style={{ marginRight: '20px', marginLeft: '-100px' }}>
                    <img
                        src={user.avatar_url} // Utilisation de l'URL de l'avatar
                        alt={user.username}
                        style={{
                            width: '150px',   // Taille agrandie de l'avatar
                            height: '150px',
                            borderRadius: '50%' // Avatar circulaire
                        }}
                        onError={(e) => {
                            console.error('Error loading image:', e);
                        }}
                    />
                </div>
                <div>
                    <h2>{user.username}</h2>
                    <h3>
                    {error ? (
                        <p style={{ color: 'red' }}>{error}</p>
                    ) : (
                        <p style={{ color: getStatusColor(playerStatus), margin: 0 }}>
                            {playerStatus !== "inactive" && gameMode 
                                ? `${getStatusTxt(playerStatus)} - ${gameMode}` 
                                : getStatusTxt(playerStatus)}
                        </p>
                    )}
                    </h3>
                </div>
            </div>
            <Link to="/user-personalization">Personalize Profile</Link>

            {user.nickname ? <h3>My nickname: {user.nickname}</h3> : <p>No nickname yet</p>}

            <FriendsList />
        </div>
    );
}
