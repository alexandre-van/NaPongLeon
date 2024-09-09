import { useState } from 'react';
import api from '../services/api.js';

const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await api.get('/authentication/check-auth');
        setIsAuthenticated(true);
        setUser(response.data);
      } catch (error) {

      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);
  return ({ isAuthenticated, user, loading });
};

export default useAuth;
