import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from './contexts/UserContext';

const RedirectOnRefresh = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useUser();

  useEffect(() => {
    const handleBeforeUnload = () => {
      sessionStorage.setItem('lastPath', location.pathname);
      sessionStorage.setItem('wasAuthenticated', isAuthenticated);
    };

    const handleRedirect = () => {
      const lastPath = sessionStorage.getItem('lastPath');

      const gamePaths = ['/pong/matchmaking', '/pong/ingame'];
      if (gamePaths.some(path => lastPath?.startsWith(path))) {
        navigate('/pong');
        sessionStorage.clear();
        return;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    handleRedirect();

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [navigate, location, isAuthenticated]);

  return null;
};

export default RedirectOnRefresh;