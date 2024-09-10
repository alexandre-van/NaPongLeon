import { useState } from 'react';
import api from '../services/api.js';

const useLogin = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  const login = async (userData) => {
    try {
      const response = await api.post('/authentication/login/', userData);
      if (response.data.message === 'Login successful') {
        setIsAuthenticated(true);
        setUser(userData.username);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      setIsAuthenticated(false);
      setUser(null);
      return false;
    }
  };

  return { isAuthenticated, user, login };
};

export default useLogin;
