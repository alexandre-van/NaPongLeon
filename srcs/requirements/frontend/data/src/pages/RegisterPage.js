import { useState } from 'react';
import { Link , useNavigate } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm.js';
import { useUser } from '../contexts/UserContext.js';

export function RegisterPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const { register } = useUser();
  const navigate = useNavigate();


  const handleRegister = async (userData) => {
    setLoading(true);
    setError(false);
    try {
      await register(userData);
      navigate('/login');
    } catch (error) {
      setError(true);
      console.log('Error during registering:', error.response);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='login-page'>
      {loading && <p>Registering...</p>}
      {error && <p>An user with this name already exists</p>}
      <RegisterForm onRegister={handleRegister} />
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

