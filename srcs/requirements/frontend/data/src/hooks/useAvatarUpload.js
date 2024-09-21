import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

const useAvatarUpload = () => {
  const { user, updateUser, updateAvatarVersion } = useUser();

  const updateAvatar = async (file) => {
    if (!file) {
      throw new Error("Please select a file first");
    }
    const formData = new FormData();
    formData.append('avatar', file);
    const uploadResponse = await api.post('/authentication/upload-avatar/', formData, {
      headers: {
        'Content-Type': "multipart/form-data",
      }
    });

    if (uploadResponse.data.message !== 'Avatar uploaded successfully') {
      throw new Error("Failed to update avatar");
    }

    const avatarResponse = await api.get('/authentication/get-avatar/');
    if (avatarResponse.data && avatarResponse.data.avatar_url) {
      updateUser({ avatar_url: avatarResponse.data.avatar_url});
      updateAvatarVersion();
    } else {
      throw new Error("Failed to get new avatar URL");
    }
  };

  return { updateAvatar };
};

export default useAvatarUpload;
