import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api.js';

const UserContext = createContext();

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const checkAuth = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get('/authentication/check-auth/');
      setUser(response.data.user);
      setIsAuthenticated(true);
      setError(null);
    } catch (err) {
      setUser(null);
      setIsAuthenticated(false);
      setError('Authentication failed');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, []);

  const register = async (userData) => {
    const response = await api.post('/authentication/register/', userData);
    if (!response.ok) {
      console.log('register error');
      throw new Error("Registration failed");
    }
    //await login(userData);
  };

  const login = async (userData) => {
    const response = await api.post('/authentication/login/', userData);
    if (response.data.message !== "Login successful") {
      throw new Error("Login failed");
    };
    await checkAuth();
 //   return true;


/*    try {
      setLoading(true);
      const response = await api.post('/authentication/login/', userData);
      if (response.data.message === 'Login successful') {
        await checkAuth();
        return true;
      }
      setError('Login failed'):
      return false;
    } catch (err) {
      setError('Login failed');
      return false;
    } finally {
      setLoading(false);
    }*/
  };

  const logout = async () => {
    await api.post('/authentication/logout/');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/logout-success');
    await checkAuth();

/*    try {
      await api.post('/authentication/logout/');
      setUser(null);
      setIsAuthenticated(false);
      setError(null);
      navigate('/logout-success');
    } catch (err) {
      setError('Logout failed');
    } finally {
      await checkAuth();
    }*/
  };

  const value = {
    user,
    setUser,
    isAuthenticated,
    loading,
    error,
    login,
    logout,
    checkAuth,
    register
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
