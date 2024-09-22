import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

const useNicknameUpdate = () => {
  const { user, updateUser, updateNicknameVersion } = useUser();

  const updateNickname = async (nickname) => {
/*    if (typeof nickname !== 'string') {
      throw new Error('Nickname must be a string');
    }
    if (nickname.length > 30) {
      throw new Error('Nickname must be 30 characters or fewer');
    }*/

    //const uploadResponse = await api.patch('/authentication/update-nickname/', { nickname });

    const uploadResponse = await api.patch('/authentication/users/me/nickname/', { nickname });
    if (uploadResponse.data && uploadResponse.data.nickname) {
      updateUser({ nickname: uploadResponse.data.nickname });
      updateNicknameVersion();
    } /*else {
//      throw new Error("Failed to update nickname");
    }*/
  };

  return ({ updateNickname });
};

export default useNicknameUpdate;
