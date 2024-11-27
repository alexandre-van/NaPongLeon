import { Link } from "react-router-dom";
import PlayButton from "../components/PlayButton";
import api from "../services/api";

export default function WaitMatchmaking() {

  const handleCancelMatchmaking = async () => {
		try {
			const game_mode = "";
			await api.get(`/game_manager/matchmaking/game_mode=${game_mode}`);

			// Optionnel : retirer l'iframe en cas d'annulation
			const iframe = document.querySelector('#gameFrame');
			if (iframe) {
				iframe.remove();
			}
		} catch (error) {
			console.error("Failed to cancel matchmaking:", error.message);
		} finally {
		}
	};

    return (
      <div>
      <div><p> MATCHMAKING... </p></div>
      <div>
					<p>Waiting...
					<Link to="/"><button
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
					</button></Link></p>
      </div>
      </div>
    );
  }
  