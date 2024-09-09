import { useState } from 'react';
import { Link , useNavigate } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm.js';

import { API_BASE_URL } from '../config.js';

export function RegisterPage() {
  const [registrationStatus, setRegistrationStatus] = useState(null);
  const navigate = useNavigate();

  const handleRegister = async (userData) => {
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
  };

  return (
    <>
      {registrationStatus === 'failure' && (<p>An user with this name already exists</p>)}
      <RegisterForm onRegister={handleRegister} />
    </>
  );
}

export function RegisterSuccessPage() {
  return (
    <>
      <p>You are now registered, you may now log in</p>
      <Link to="login">Login Page</Link>
    </>
  );
}
