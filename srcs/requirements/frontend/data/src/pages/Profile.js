import { useEffect, useState } from 'react';
import api from "../services/api.js"; // Service API
import { useUser } from '../contexts/UserContext.js';
import { useNavigate } from 'react-router-dom';
import FriendsList from '../components/FriendsList.js';

export default function Formations() {
    const navigate = useNavigate();
    const { user, logout } = useUser();
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
    }, []);

    // Fonction pour déterminer la couleur du statut
    const getStatusColor = (status) => {
        switch (status) {
            case "inactive":
                return "green";
            case "pending":
                return "orange";
            case "in_queue":
            case "in_game":
                return "blue";
            case "waiting_for_players":
            case "loading_game":
                return "yellow";
            default:
                return "black";
        }
    };

    const getStatusTxt = (status) => {
        switch (status) {
            case "inactive":
                return "Online";
            case "pending":
                return "Expected in game";
            case "in_queue":
                return "In queue";
            case "in_game":
                return "In game";
            case "waiting_for_players":
                return "Waiting";
            case "loading_game":
                return "In game";
            default:
                return "with";
        }
    };

    const handleLogout = (e) => {
        e.preventDefault();
        try {
          logout();
          navigate('/logout-success');
        } catch (error) {
          console.error("Logout failed", error);
        }
      };

    return (
        <div className="profile" style={{ paddingTop: '50px' }}> {/* Ajout d'une marge en haut */}
    {/* Titre Profile à l'extérieur */}
    <h1 style={{ textAlign: 'center', marginBottom: '20px' }}>Profile</h1>

    <div style={{
        border: '2px solid #fff',  // Bordure blanche
        padding: '20px',
        borderRadius: '10px',
        backgroundColor: 'transparent',  // Fond transparent
        maxWidth: '600px',  // Largeur maximale pour que le cadre ne soit pas trop large
        margin: '0 auto',  // Centrage horizontal
        display: 'flex',  // Disposition en flex pour diviser en 2 parties égales
    }}>
        {/* Partie gauche pour l'image */}
        <div style={{
            flex: 1, // La partie gauche prend 1/2 de l'espace
            display: 'flex',
            justifyContent: 'center',  // Centrage horizontal de l'image
            alignItems: 'center',  // Centrage vertical de l'image
        }}>
            <img
                src={user.avatar_url} // Utilisation de l'URL de l'avatar
                alt={user.username}
                style={{
                    width: '200px',   // Taille agrandie de l'avatar
                    height: '200px',
                    borderRadius: '50%' // Avatar circulaire
                }}
                onError={(e) => {
                    console.error('Error loading image:', e);
                }}
            />
        </div>

        {/* Partie droite pour les informations */}
        <div style={{
            flex: 1, // La partie droite prend 1/2 de l'espace
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center', // Centrage vertical des informations
            alignItems: 'center', // Alignement à gauche
            paddingLeft: '20px',  // Espacement entre l'image et les informations
        }}>
            <h1>{user.username}</h1>
            <h2>{user.nickname && (
                <p style={{ fontSize: '24px', marginTop: '6px' }}>
                    {user.nickname}
                </p>
            )}
            </h2>
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

    {/* Titre Personalize Profile à l'extérieur */}
    <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <button className="Profilebutton personalize" onClick={() => navigate('/user-personalization')}>
            Personalize Profile
        </button>
    </div>

    {/* Bouton Logout avec classe CSS */}
    <div style={{ textAlign: 'center' }}>
        <button className="Profilebutton logout" onClick={handleLogout}>
            Logout
        </button>
    </div>
</div>


    );
}
