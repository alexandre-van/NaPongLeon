import "./Navigation.css"
import { Link } from 'react-router-dom';

import logo from '../elements/logo.png'
import { useUser } from '../contexts/UserContext.js';

function Navigation() {

  const { logout } = useUser(); // Récupérez la fonction logout

  const handleLogout = () => {
    logout(); // Appelle la fonction de déconnexion
  };
  return (
    <div>
      <div class="topnav">
        <Link className="active" to="/"><img className="logo" src={logo}/></Link>
        <Link to="/news">News</Link>
        <Link to="/game-modes">Game Modes</Link>
        <Link to="/gamehistory">Game History</Link>
        <Link to="/login">Log in</Link>
        <Link to="/register">Register</Link>
        <Link onClick={handleLogout}>Logout</Link>
        <Link to="/login">Profile</Link>
      </div>
    </div>
  );
}

export default Navigation;