import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm.js';
import { useUser } from '../contexts/UserContext.js';

export function RegisterPage() {
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { register, isAuthenticated } = useUser();
  const navigate = useNavigate();

  const handleRegister = async (userData) => {
    setLoading(true);
    setErrors({});
    try {
      await register(userData);
      navigate('/login');
    } catch (error) {
      if (error.response && error.response.data) {
        setErrors(error.response.data); // Capture les erreurs spécifiques
      } else {
        console.log('Unexpected error:', error);
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
      {loading && <p>Registering...</p>}
      <RegisterForm onRegister={handleRegister} errors={errors} />
    </div>
  );
}

export function RegisterSuccessPage() {
  return (
    <div>
      <p>You are now registered and you may now log in</p>
      <Link to="/login">Login Page</Link>
    </div>
  );
}
