import Avatar from '../components/Avatar.js';
import PlayButton from '../components/PlayButton.js';

import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext.js';

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
  const { user, getAvatarUrl } = useUser();

  return (
    <div className="profile">
      <h2>{user.username}'s Profile</h2>
      <Link to="/user-personalization">Personalize Profile</Link>
      <Avatar user={{ ...user, avatar_url: getAvatarUrl() }} />
      {user.nickname ? <h3>My nickname: {user.nickname}</h3> : <p>No nickname yet</p>}
      <PlayButton />
    </div>
  );
}

