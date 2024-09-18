import AvatarUpload from '../components/AvatarUpload.js';
import NicknameForm from '../components/NicknameForm.js';
import useNicknameUpdate from '../hooks/useNicknameUpdate.js';
import Avatar from '../components/Avatar.js';

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
  const { user } = useUser();

  return (
    <div className="profile">
      <h2>{user.username}'s Profile</h2>
      <AvatarUpload /> 
    </div>
  );
}

      //<Avatar user={user} />
/*  if (isAuthenticated) {
    const { updateNickname, error } = useNicknameUpdate();

    const handleNicknameUpdate = async (nickname) {
      try {
        const success = await updateNickname(nickname);
        if (success) {

        }
      } catch (error) {

      }
    };
    

    const handleAvatarUpdate = (newAvatarUrl) => {
      console.log("Avatar updated", newAvatarUrl);
    };

    return (
      <>
        <div className="profile">
          <h2>{user.username}'s Profile</h2>
          <h4>Nickname: <stong>{user.nickname ? <user.nickname> : No nickname}</strong><h4>
          <NicknameForm user={user}/>
          <AvatarUpload user={user} onAvatarUpdate={handleAvatarUpdate} />

        </div>
        <p> YOU ARE CONNECTED, THIS THE HOME PAGE </p>
      </>
    );
  }
  return (

}*/
