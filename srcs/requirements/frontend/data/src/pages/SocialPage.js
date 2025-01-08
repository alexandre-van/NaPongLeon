import FriendsList from '../components/FriendsList.js';

export default function SocialPage() {
    return (
        <div className="profile" style={{ paddingTop: '50px' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Social Network</h2>
          <FriendsList />
        </div>
      );
}
