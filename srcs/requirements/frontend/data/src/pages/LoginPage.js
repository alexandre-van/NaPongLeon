import { useUser } from '../contexts/UserContext.js';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm.js';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useUser();
  const [error, setError] = useState(''); // Changement en `string` pour un message personnalisé
  const [loading, setLoading] = useState(false);

  const handleLogin = async (userData) => {
    setError('');
    setLoading(true);
    try {
      const response = await login(userData);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error); // Récupération du message d'erreur
      } else {
        setError('An unexpected error occurred.'); // Message d'erreur générique
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {loading && <p>Logging in...</p>}
      <LoginForm onLogin={handleLogin} error={error} />
    </div>
  );
}
