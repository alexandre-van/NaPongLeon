import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext.js';
import { useState } from 'react';

export default function ConnectedNavigation() {
  const { logout } = useUser();
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogout = (e) => {
    e.preventDefault();
    setError(false);
    setLoading(true);
    try {
      logout();
    } catch (error) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div role="nav" className="nav-container">
      <div className="home-nav">
        <Link to="/">SPICE PONG</Link>
      </div>
      <div className="main-nav">
        <Link to='/'>MY PROFILE</Link>
        <Link to='/formations'>FORMATIONS</Link>
        <Link to='/game-modes'>GAME MODES</Link>
        <Link to='/leaderboard'>LEADERBOARD</Link>
      </div>
      <div className="right-nav">
        <Link to='/logout' onClick={handleLogout}>LOG OUT</Link>
        {loading && <p>Logging out...</p>}
        {error && <p>Error: could not log out</p>}
      </div>
    </div>
  );
}
