import { Link } from 'react-router-dom';

export default function Navigation() {
    return (
        <div role='nav' className="nav-container">
            <div className="home-nav">
                <Link to="/">SPICE PONG</Link>
                <img src="/images/pinpoint.png" alt="test-image" />
            </div>
            <div className="main-nav">
                <Link to="/">HOME</Link>
                <Link to="/news">NEWS</Link>
                <Link to="/game-modes">GAME MODES</Link>
                <Link to="/leaderboard">LEADERBOARD</Link>
            </div>
            <div className="right-nav">
                <Link to="/login">LOG IN</Link>
            </div>
        </div>
    );
}
