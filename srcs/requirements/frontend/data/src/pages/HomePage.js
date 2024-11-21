import Avatar from '../components/Avatar.js';
import PlayButton from '../components/PlayButton.js';

import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext.js';
import FriendsList from '../components/FriendsList.js';

export default function HomePage({ isAuthenticated }) {
  if (!isAuthenticated) {
    return (
      <>
        <p>Find your inner peace<br /> With your friends Here</p>
        <p>Play pong the majestic way. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non vulputate arcu. Duis et dui nec justo auctor imperdiet sed eu urna. Ut vitae lacinia turpis. Etiam et nunc rhoncus, efficitur tellus at, varius felis. Etiam mollis, turpis et dictum varius, quam nisi rhoncus felis, eu blandit erat risus bibendum nisi. Curabitur ullamcorper eleifend risus vestibulum tempor.</p>
      </>
    );
  }

  return <AuthenticatedHomePage />;
}

function AuthenticatedHomePage() {


  return (
    <div className="backgroundpage">
      <h1 className="title-home">Welcome to Napongleon</h1>
      <Link to="/game-modes"><button className="play-button btn btn-outline-warning" type="button">PLAY</button></Link>
    </div>
  );
}

