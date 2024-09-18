import { useState } from 'react';
import api from '../services/api.js';

const useNicknameUpdate = () => {
  const [error, setError] = useState('');

  const updateNickname = async ({ nickname }) => {
    if (nickname.length > 30) {
      setError('Nickname must be 30 characters or fewer');
      return false;
    }

    try {
      const response = await api.post('/authentication/update-nickname/');
      const data = await response.json();
      if (response.ok) {
        setError('');
        return true;
      }
      setError(data.error);
      return false;
    } catch (error) {
      setError('Network error');
      return false;
    }
  };

  return ({ updateNickname, error });
};

export default useNicknameUpdate;
