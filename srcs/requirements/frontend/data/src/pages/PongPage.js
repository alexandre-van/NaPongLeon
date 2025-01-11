import { Link } from 'react-router-dom';
import { useNavigate } from "react-router-dom";

export default function PongPage() {
    const navigate = useNavigate();
    const goToGameMode = (gameMode, title, hasCompetitors = false) => {
        navigate("/pong/game-mode", {
        state: { gameMode, title, hasCompetitors },
      });
    };
    return (
      <div>
        <div>
          <Link to="/pong/ai-pong">
          <button 
                    className="play-button-mode btn btn-outline-warning"
                    type="button"
                >
                    SOLO-AI
          </button>
          </Link>
          <button
                    className="play-button-mode btn btn-outline-warning"
                    type="button"
                    onClick={() => goToGameMode("PONG_CLASSIC", "1 VS 1")}
                >
                    1 VS 1
          </button>
          <button
                    className="play-button-mode btn btn-outline-warning"
                    type="button"
                    onClick={() => goToGameMode("PONG_DUO", "2 VS 2")}
                 >
                    2 VS 2
          </button>
          </div>
          <div>
          <button
                    className="play-button-mode btn btn-outline-warning"
                    type="button"
                    onClick={() => goToGameMode("PONG_CLASSIC_TOURNAMENT", "Solo Tournament", true)}
                >
                    Solo Tournament
          </button>
          <button
                    className="play-button-mode btn btn-outline-warning"
                    type="button"
                    onClick={() => goToGameMode("PONG_DUO_TOURNAMENT", "Duo Tournament", true)}
                >
                    Duo Tournament
          </button>
        </div>
      </div>
    );
}