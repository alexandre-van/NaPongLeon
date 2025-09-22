import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from "../services/api.js"; // Service API

export default function LeaveButton() {
    const navigate = useNavigate();
    const [playerStatus, setPlayerStatus] = useState('Loading...'); // État pour le statut du joueur
    const [error, setError] = useState(null);
    const [isStatusVisible, setIsStatusVisible] = useState(false); // État pour afficher/masquer la fenêtre de statut
    const buttonRef = useRef(null); // Référence pour gérer les clics en dehors
    const [isInGame, setIsInGame] = useState(false); // Statut pour savoir si le joueur est en jeu

    useEffect(() => {
        const fetchPlayerStatus = () => {
            api.get(`/game_manager/get_status/username=`)
                .then((response) => {
                    const { status } = response.data.data;
                    setPlayerStatus(status);
                    setIsInGame(status === 'in_game'); // Met à jour si le joueur est en jeu
                    setError(null);

                    // Si le statut devient "inactive", fermer la fenêtre de statut
                    if (status === 'inactive' || status === 'spectate') {
                        setIsStatusVisible(false);
                    }
                })
                .catch((err) => {
                    console.error('Erreur lors de la récupération du statut:', err);
                    setError('Impossible de récupérer le statut');
                });
        };

        // Appel initial
        fetchPlayerStatus();

        // Intervalle pour mettre à jour toutes les 10 secondes
        const intervalId = setInterval(fetchPlayerStatus, 1000);

        // Nettoyage à la fin du composant
        return () => clearInterval(intervalId);
    }, []);

    const handleButtonClick = (e) => {
        e.stopPropagation(); // Empêche la propagation de l'événement et évite de fermer la fenêtre
        if (playerStatus === 'inactive' || playerStatus === 'spectate') {
            handleQuitGame(); // Si le statut est "inactive", quitter la partie immédiatement
        } else {
            setIsStatusVisible(!isStatusVisible); // Affiche ou cache le menu de statut
        }
    };

    const handleQuitGame = () => {
        navigate("/pong");
    };

    const handleOutsideClick = (e) => {
        if (buttonRef.current && !buttonRef.current.contains(e.target)) {
            setIsStatusVisible(false);
        }
    };

    useEffect(() => {
        if (isStatusVisible) {
            document.addEventListener('click', handleOutsideClick);
        } else {
            document.removeEventListener('click', handleOutsideClick);
        }

        return () => document.removeEventListener('click', handleOutsideClick);
    }, [isStatusVisible]);

    const buttonStyle = {
        position: 'fixed',
        bottom: '20px',
        left: '20px', // Déplace le bouton à gauche
        width: '50px',
        height: '50px',
        borderRadius: '50%',
        backgroundColor: '#333', // Même couleur que pour le bouton des notifications
        color: 'white',
        border: 'none',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '24px',
        zIndex: 1000,
        boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
    };

    const statusBoxStyle = {
        position: 'fixed',
        bottom: '80px',
        left: '20px', // Positionne la fenêtre contextuelle à gauche
        backgroundColor: '#333', // Fond sombre comme celui du bouton
        borderRadius: '8px',
        padding: '10px',
        zIndex: 1000,
        boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
    };

    const statusTextStyle = {
        color: 'white', // Texte en blanc
    };

    return (
        <div>
            <button onClick={handleButtonClick} style={buttonStyle} ref={buttonRef}>
                {(playerStatus === 'inactive' || playerStatus === 'spectate') ? '❌' : '🏁'}
            </button>
            {isStatusVisible && (
                <div style={statusBoxStyle}>
                    {error ? (
                        <p style={{ ...statusTextStyle, color: 'red' }}>{error}</p>
                    ) : (
                        <p style={statusTextStyle}>Status: {playerStatus}</p>
                    )}
                    <button
                        onClick={handleQuitGame}
                        style={{
                            backgroundColor: "#ff4444",
                            color: "white",
                            border: "none",
                            padding: "5px 10px",
                            borderRadius: "5px",
                            cursor: "pointer",
                            marginTop: "10px",
                            width: "100%",
                        }}
                    >
                        Give Up
                    </button>
                </div>
            )}
        </div>
    );
}
