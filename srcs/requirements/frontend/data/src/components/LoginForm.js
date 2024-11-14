import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext.js'

const LoginForm = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
    totpToken: '',
  });
//  const [totpToken, setTotpToken] = useState('');
  const [step, setStep] = useState('credentials'); // 'credentials' or 'totp'
  const { login42 } = useUser();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    try {
      const has_2fa = onLogin(credentials);
      if (has_2fa) {
        setStep('totp');
      } else {
        console.log('Login successful');
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div>
      {step === 'credentials' ? (
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit">LOG IN</button>
          <button onClick={login42}>LOG IN WITH 42</button>
          <Link to="/register">REGISTER</Link>
        </form>) : (
          <form onSubmit={handleSubmit}>
            <div>
              <p>Enter the code from your authenticator app</p>
              <input 
                type="text"
                id="totpToken"
                name="totpToken"
                value={credentials.totpToken}
                onChange={handleChange}
                placeholder="Enter 2FA code"
              />
            </div>
            <button type="submit">Verify</button>
          </form>
        )}
    </div>
  );
}

export default LoginForm;
