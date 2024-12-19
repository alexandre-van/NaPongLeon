import { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import api from "../services/api";

export default function WaitMatchmaking() {
  const location = useLocation();

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
    const handlePopState = () => {
      if (location.pathname !== "/matchmaking") {
        handleCancelMatchmaking();
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [location.pathname]);

  useEffect(() => {
    return () => {
      // Vérifie si la nouvelle destination n'est pas la page de matchmaking
      if (location.pathname !== "/matchmaking") {
        handleCancelMatchmaking();
      }
    };
  }, [location]);

  return (
    <div>
      <div>
        <p>MATCHMAKING...</p>
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