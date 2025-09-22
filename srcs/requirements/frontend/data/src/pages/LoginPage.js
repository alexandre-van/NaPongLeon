import { useUser } from '../contexts/UserContext.js';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm.js';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useUser();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (userData) => {
    setError('');
    setLoading(true);
    try {
      const response = await login(userData);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="login-page">
      {loading && <p>Logging in...</p>}
      <LoginForm onLogin={handleLogin} error={error} />
    </div>
  );
}
