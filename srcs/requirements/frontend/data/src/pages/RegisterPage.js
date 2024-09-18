import { useState } from 'react';
import { Link , useNavigate } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm.js';
import { useUser } from '../contexts/UserContext.js';

//import { API_BASE_URL } from '../config.js';

export function RegisterPage() {
//  const [registrationStatus, setRegistrationStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const { register } = useUser();
  const navigate = useNavigate();


  const handleRegister = async (userData) => {
    setLoading(true);
    setError(false);
    try {
      await register(userData);
      navigate('/register-success');
    } catch (error) {
      setError(true);
      console.log('Error during registering:', error.response);
    } finally {
      setLoading(false);
    }
  };

/*  const handleRegister = async (userData) => {
    try {
      const response = await fetch(`/api/authentication/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        setRegistrationStatus('success');
        navigate('/register-success');
      } else {
        setRegistrationStatus('failure');
      }
    } catch (error) {
      console.error('Error while sign up:', error);
      setRegistrationStatus('failure');
    }
  };*/

  return (
    <>
      {loading && <p>Registering...</p>}
      {error && <p>An user with this name already exists</p>}
      <RegisterForm onRegister={handleRegister} />
    </>
  );
}

export function RegisterSuccessPage() {
  return (
    <>
      <p>You are now registered and you may now log in</p>
      <Link to="/login">Profile Page</Link>
    </>
  );
}

