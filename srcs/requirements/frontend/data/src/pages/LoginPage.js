import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm.js';
import useLogin from '../hooks/useLogin.js';

export default function LoginPage() {
  const [loginStatus, setLoginStatus] = useState(null);
  const navigate = useNavigate();
  const { login } = useLogin();

  const handleLogin = async (userData) => {
    try {
      const success = await login(userData);
      if (success) {
        setLoginStatus('success');
        navigate('/leaderboard');
      } else {
        setLoginStatus('failure');
      }



/*      const response = await fetch(`/api/authentication/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        setLoginStatus('success');
        navigate('/');
      } else {
        setLoginStatus('failure');
      }*/
    } catch (error) {
      console.error('Error Login:', error);
      setLoginStatus('failure');
    }
  };
    return (
      <>
        {loginStatus === 'failure' && (<p>Error while trying to log in</p>)}
        <LoginForm onLogin={handleLogin} />
      </>
    );
}
