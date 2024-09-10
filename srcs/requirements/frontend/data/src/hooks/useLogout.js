import { useNavigate } from 'react-router-dom';
import api from '../services/api.js';

const useLogout = () => {
  const navigate = useNavigate();

  const logout = async () => {
    try {
      await api.post('/authentication/logout/');
      navigate('/');
    } catch (error) {
      console.error('Error when logging out:', error);
    }
  };

  return logout;
};

export default useLogout;
