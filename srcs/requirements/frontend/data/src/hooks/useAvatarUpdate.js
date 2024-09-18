import { useState } from 'react';
import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

const useAvatarUpload = () => {
  const { user, setUser, checkAuth } = useUser();
  const [loading, setLoading] = useState(false);

  const updateAvatar = async (file) => {
    if (!file) {
      throw new Error("Please select a file first"); // Catch in AvatarUpload > handleUpdate
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('avatar', file);
    const uploadResponse = await api.post('/authentication/upload-avatar/', formData, {
      headers: {
        'Content-Type': "multipart/form-data",
      }
    });

    if (uploadResponse.data.message !== 'Avatar uploaded successfully') {
      throw new Error("Failed to update avatar"); // Catch in AvatarUpload > handleUpdate
    }
    setUser(prevUser => ({
      ...prevUser,
      avatar_url: uploadResponse.data.avatar_url
    }));
    await checkAuth();
    setLoading(false);
  };

  return { updateAvatar, loading };
};

export default useAvatarUpload;
