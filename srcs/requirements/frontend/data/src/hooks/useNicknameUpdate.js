import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

const useNicknameUpdate = () => {
  const { user, updateUser, updateNicknameVersion } = useUser();

  const updateNickname = async (nickname) => {
/*    if (typeof nickname !== 'string') {
      throw new Error('Nickname must be a string');
    }
    if (nickname.length > 20) {
      throw new Error('Nickname must be 20 characters or fewer');
    }*/
    const response = await api.patch('/authentication/users/me/nickname/', { nickname });
    if (response.status !== 200) {
      throw new Error("Could not update nickname");
    }
    if (response.data) {
      updateUser({ nickname: response.data.nickname });
      updateNicknameVersion();
    } else {
      throw new Error("Nickname not found in response");
    }
  };

  return ({ updateNickname });
};

export default useNicknameUpdate;
