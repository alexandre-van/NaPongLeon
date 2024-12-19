import { useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function WaitMatchmaking() {
  const handleCancelMatchmaking = async () => {
    try {
      const game_mode = ""; // Ajuste le mode de jeu si nécessaire
      await api.get(`/game_manager/matchmaking/game_mode=${game_mode}`);
      console.log("Matchmaking canceled");
    } catch (error) {
      console.error("Failed to cancel matchmaking:", error.message);
    }
  };

  useEffect(() => {
    const handleRouteChange = () => {
      handleCancelMatchmaking(); // Appelle l'annulation lors du changement de route
    };

    const handleBeforeUnload = (event) => {
      handleCancelMatchmaking(); // Annule le matchmaking si l'utilisateur ferme/recharge la page
    };

    // Écoute les changements de navigation (back/forward) et les rechargements de la page
    window.addEventListener("popstate", handleRouteChange);
    window.addEventListener("beforeunload", handleBeforeUnload);

    // Nettoyage des écouteurs
    return () => {
      window.removeEventListener("popstate", handleRouteChange);
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  return (
    <div>
      <div>
        <p> MATCHMAKING... </p>
      </div>
      <div>
        <p>
          Waiting...
          <Link to="/">
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
