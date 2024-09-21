import AvatarUpload from '../components/AvatarUpload.js';
import NicknameForm from '../components/NicknameForm.js';
import useAvatarUpload from '../hooks/useAvatarUpload.js';
import useNicknameUpdate from '../hooks/useNicknameUpdate.js';

import { Link } from 'react-router-dom';
//import { useUser } from '../contexts/UserContext.js';
import { useState } from 'react';

function UserPersonalizationPage() {
  const [error, setError] = useState(null);
  const { updateAvatar } = useAvatarUpload();
  const { updateNickname } = useNicknameUpdate();
//  const { user } = useUser();

  const handleNicknameSubmit = async ({ nickname, error }) => {
    if (error) {
      setError(error);
      return;
    }

    try {
      await updateNickname(nickname);
      console.log('Nickname uploaded successfully');
      setError(null);
    } catch (updateNicknameError) {
      setError(updateNicknameError.message);
    }
  };

  const handleAvatarUpload = async ({ file, error }) => {
    if (error) {
      setError(error);
      return;
    }

    try {
      await updateAvatar(file);
      console.log('Avatar uploaded successfully');
      setError(null);
    } catch (updateAvatarError) {
      setError(updateAvatarError.message);
    }
  };

  return (
    <div>
      <Link to="/">Back to Profile</Link>
      <NicknameForm onUpload={handleNicknameSubmit} onError={setError} />
      <AvatarUpload onUpload={handleAvatarUpload} onError={setError} />
      {error && <p>{error}</p>}
    </div>
  );
}

export default UserPersonalizationPage;
