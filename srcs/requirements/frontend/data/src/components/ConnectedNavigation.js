import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext.js';
import { useState } from 'react';
import "./Navigation.css"
import logo from '../elements/logo.png'
import Avatar from '../components/Avatar.js';

export default function ConnectedNavigation() {
  const { logout } = useUser();
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);
  const { user, getAvatarUrl } = useUser();

  const handleLogout = (e) => {
    e.preventDefault();
    setError(false);
    setLoading(true);
    try {
      logout();
      navigate('/logout-success');
    } catch (error) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="topnav">
        <Link className="active" to="/"><img className="logo" src={logo}/></Link>
        <Link to="/pong">Pong</Link>
        <Link to="/hagarrio">Hagarrio</Link>
        <Link to="/leaderboard">Learderboard</Link>
        <Link onClick={handleLogout}>Logout</Link>
        <div className="right-profile">
          <Link className="avatarprofile" to="/profile"><Avatar user={{ ...user, avatar_url: getAvatarUrl() }} /></Link>
        </div>
      </div>
    </div>
  );
}
