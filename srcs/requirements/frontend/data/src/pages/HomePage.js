import Avatar from '../components/Avatar.js';
import PlayButton from '../components/PlayButton.js';

import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext.js';
import FriendsList from '../components/FriendsList.js';

export default function HomePage({ isAuthenticated }) {
  if (!isAuthenticated) {
    return (
      <div></div>
    );
  }

  return <AuthenticatedHomePage />;
}

function AuthenticatedHomePage() {

  return (
    <div>
      <h1 className="title-home">Welcome to Napongleon</h1>
      <Link to="/pong"><button className="play-button btn btn-outline-warning" type="button">PLAY</button></Link>
    </div>
  );
}