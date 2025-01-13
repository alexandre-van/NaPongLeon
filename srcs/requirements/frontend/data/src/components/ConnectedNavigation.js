import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext.js';
import { useState, useEffect, useRef } from 'react';
import "./Navigation.css";
import logo from '../elements/logo.png';
import Avatar from '../components/Avatar.js';

export default function ConnectedNavigation() {
  const { logout, user, getAvatarUrl } = useUser();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const handleLogout = (e) => {
    e.preventDefault();
    try {
      logout();
      navigate('/logout-success');
    } catch (error) {
      console.error("Logout failed", error);
    }
  };

  const toggleMenu = () => setMenuOpen((prev) => !prev);

  const isActive = (path) => location.pathname === path;

  return (
    <div className="topnav">
      <div className="nav-container">
        <Link className="logo-link" to="/">
          <img className="logo" src={logo} alt="Logo" />
        </Link>
        
        <Link 
          to="/pong" 
          className={`nav-link ${isActive('/pong') ? 'active' : ''}`}
        >
          Pong
        </Link>
        
        <Link 
          to="/hagarrio" 
          className={`nav-link ${isActive('/hagarrio') ? 'active' : ''}`}
        >
          Hagarrio
        </Link>
        
        <Link 
          to="/gamehistory" 
          className={`nav-link ${isActive('/gamehistory') ? 'active' : ''}`}
        >
          Game History
        </Link>
        
        <Link 
          to="/social-network" 
          className={`nav-link ${isActive('/social-network') ? 'active' : ''}`}
        >
          Social Network
        </Link>
        
        <div className="right-profile" ref={menuRef}>
        <div className="user-info" onClick={toggleMenu}>
          <Link 
            to="/profile" 
            className={`username ${isActive('/profile') || isActive('/user-personalization')  ? 'active' : ''}`}
          >
            {user?.username}
          </Link>
          <Avatar user={{ ...user, avatar_url: getAvatarUrl() }} />
        </div>

          
          
          {menuOpen && (
            <div className="dropdown-menu">
              <Link to="/profile">Profile</Link>
              <Link to="/user-personalization">Personalize Profile</Link>
              <button className="logout" onClick={handleLogout}>
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}