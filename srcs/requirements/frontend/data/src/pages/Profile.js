import PlayButton from '../components/PlayButton.js';
import { useUser } from '../contexts/UserContext.js';
import { Link } from 'react-router-dom';
import FriendsList from '../components/FriendsList.js';

export default function Formations() {
    const { user } = useUser();

    return (
        <div className="profile">
            <div className="profile-header" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                {/* Avatar avec styles en ligne */}
                <div style={{ marginRight: '20px', marginLeft: '-100px' }}>
                    <img
                        src={user.avatar_url}  // Utilisation de l'URL de l'avatar
                        alt={user.username}
                        style={{
                            width: '150px',   // Taille agrandie de l'avatar
                            height: '150px',
                            borderRadius: '50%'  // Avatar circulaire
                        }}
                        onError={(e) => {
                            console.error('Error loading image:', e);
                        }}
                    />
                </div>
                <h2>{user.username}'s Profile</h2>
            </div>
            <Link to="/user-personalization">Personalize Profile</Link>

            {user.nickname ? <h3>My nickname: {user.nickname}</h3> : <p>No nickname yet</p>}
            <FriendsList/>
        </div>
    );
}
