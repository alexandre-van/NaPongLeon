import { Link } from 'react-router-dom';
import CreateGameButton from '../components/CreateGameButton';

export default function PongPage() {
    return (
      <div>
        <div>
          <Link to="/ai-pong"><button className="play-button-mode btn btn-outline-warning" type="button">SOLO-AI</button></Link>
          <Link to="/solo-mode"><button className="play-button-mode btn btn-outline-warning" type="button">1 VS 1</button></Link>
          <Link to="/duo-mode"><button className="play-button-mode btn btn-outline-warning" type="button">2 VS 2</button></Link>
        </div>
        <div>
          <Link to="/classic-tournament"><button className="play-button-mode btn btn-outline-warning" type="button">Solo Tournament</button></Link>
          <Link to="/duo-tournament"><button className="play-button-mode btn btn-outline-warning" type="button">Duo Tournament</button></Link>
        </div>
      </div>
    );
}