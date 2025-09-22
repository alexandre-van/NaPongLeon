import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api.js';

const UserContext = createContext();

export function UserProvider({ children }) {
	const [user, setUser] = useState(null);
	const [notFrom42, setNotFrom42] = useState(true);
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [friends, setFriends] = useState([]);
	const [loading, setLoading] = useState(true);
	const [avatarVersion, setAvatarVersion] = useState(0);
	const [nicknameVersion, setNicknameVersion] = useState(0);
	const [error, setError] = useState(null);
	const navigate = useNavigate();

	const checkAuth = useCallback(async () => {
		try {
			setLoading(true);
			const response = await api.get('/authentication/users/me/'); // gets a "user" object
			setUser(response.data.user);
			setIsAuthenticated(true);
			setError(null);
			if (response.data.user.username.includes('_42')) {
				setNotFrom42(false);
			}
		} catch (err) {
			setUser(null);
			setIsAuthenticated(false);
			setError('Authentication failed');
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		checkAuth();
	}, [checkAuth]);



	const register = async (userData) => {
		const response = await api.post('/authentication/users/', userData);
	};

	const login = async (userData) => {
		const response = await api.post('/authentication/auth/login/', userData);
		if (response.data.requires_2fa) {
			window.location.href = `/login/2fa?token=${encodeURIComponent(response.data.temp_token)}`;
        	return ;
		}
		await checkAuth();
      	navigate('/');
		return false;
	};

	const login42 = () => {
		window.location.href = '/api/authentication/oauth/42/authorize';
	};

  	const resetPassword = async (email) => {
    	const response = await api.post('/authentication/users/password-reset/', email);
  	};

	const logout = async () => {
		await api.post('/authentication/auth/logout/');
		setUser(null);
		setIsAuthenticated(false);
		setNotFrom42(true);
		navigate('/login');
		await checkAuth();
	};

	const refreshAccessToken = useCallback(async () => {
		try {
		  const response = await api.get('/authentication/auth/token/refresh/');
		  if (!response.data || response.data.message !== "Token refreshed") {
			console.warn('Token refresh response invalid');
			return;
		  }
		} catch (error) {
		  console.error('Heartbeat token refresh failed:', error);
		  // Si le refresh échoue, déconnecter l'utilisateur
		  if (error.responsee?.status === 401) {
		  	await logout();
		  }
		}
	}, [logout]);

	useEffect(() => {
		let heartbeatInterval;
	
		if (isAuthenticated) {
		  heartbeatInterval = setInterval(async () => {
			await refreshAccessToken();
		  }, 60 * 1000); // 1 minute
		}
	
		// Cleanup
		return () => {
		  if (heartbeatInterval) {
			clearInterval(heartbeatInterval);
		  }
		};
	}, [isAuthenticated, refreshAccessToken]);

	const sendFriendRequest = async (target_username) => {
		const response = await api.post('/authentication/friends/requests/', {
			'target_user': target_username,
		});
		if (response.data && response.data.message !== "Friend request sent") {
			throw new Error('Could not send friend request');
		}
	};

	// For any user update
	const updateUser = useCallback((updates) => {
		setUser(prevUser => ({
			...prevUser,
			...updates
		}));
	}, []);

	// To force a reload of the avatar image and not use browser cache
	const updateAvatarVersion = useCallback(() => {
		setAvatarVersion(v => v + 1);
	}, []);

	const updateNicknameVersion = useCallback(() => {
		setNicknameVersion(v => v + 1);
	}, []);

	const getAvatarUrl = useCallback(() => {
		if (user?.avatar_url) {
			return `${user.avatar_url}?v=${avatarVersion}`;
		}
		return null;
	}, [user?.avatar_url, avatarVersion]);

  const value = {
    user,
    setUser,
    isAuthenticated,
    friends,
	setFriends,
    loading,
    error,
    login,
    login42,
    logout,
    checkAuth,
	notFrom42,
    register,
    resetPassword,
    sendFriendRequest,
    updateUser,
    updateAvatarVersion,
    updateNicknameVersion,
    getAvatarUrl
  };

	return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useUser() {
	const context = useContext(UserContext);
	if (context === undefined) {
		throw new Error('useUser must be used within a UserProvider');
	}
	return context;
}