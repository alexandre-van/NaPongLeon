import { Link } from 'react-router-dom';
import useLogout from '../hooks/useLogout.js';

export default function ConnectedNavigation() {
  const logout = useLogout();

  const handleLogout = (e) => {
    e.preventDefault();
    logout();
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
      </div>
    </div>
  );
}
