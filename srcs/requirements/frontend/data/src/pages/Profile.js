import Avatar from '../components/Avatar.js';
import PlayButton from '../components/PlayButton.js';
import { useUser } from '../contexts/UserContext.js';
import { Link } from 'react-router-dom';
import FriendsList from '../components/FriendsList.js';

export default function Formations() {
    const { user, getAvatarUrl } = useUser();
    return (
        <div className="profile">
        <h2>{user.username}'s Profile</h2>
        <Link to="/user-personalization">Personalize Profile</Link>

        {user.nickname ? <h3>My nickname: {user.nickname}</h3> : <p>No nickname yet</p>}
        <FriendsList/>
      </div>
    );
  }
  