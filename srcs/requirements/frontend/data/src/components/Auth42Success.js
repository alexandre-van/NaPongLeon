import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';

const AuthSuccess = () => {
  const navigate = useNavigate();
  const { checkAuth } = useUser();

  useEffect(() => {
    const initAuth = async () => {
      try {
        await checkAuth();
        navigate('/');  // ou dashboard, ou autre
      } catch (err) {
        navigate('/login', { 
          state: { error: 'Authentication failed' } 
        });
      }
    };

    initAuth();
  }, [checkAuth, navigate]);

  return (
    <div>
        <h2>Finalizing login...</h2>
    </div>
  );
};

export default AuthSuccess;