import { useNavigate } from 'react-router-dom';
import api from '../services/api.js';
import useAuth from '../hooks/useAuth.js';

const useLogout = () => {
  const navigate = useNavigate();
  const { checkAuth } = useAuth();

  const logout = async () => {
    try {
      await api.post('/authentication/logout/');
      await checkAuth();
      navigate('/logout-success');
    } catch (error) {
      console.error('Error when logging out:', error);
    }
  };

  return logout;
};

export default useLogout;
