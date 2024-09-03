import { createContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [accessToken, setAccessToken] = useState(null);
    const [user, setUser] = useState(null);

    // [] as the second props makes it checks only once
    useEffect(() => {
        const initAuth = async () => {
            const token = await refreshAccessToken();
            if (token) {
                setAccessToken(token);
                setUser({ id: 'userId' });
            }
        };
    initAuth();
    }, []);

    const login = async (username, password) => {
        try {
        const response = await fetch();
        if (!response.ok)
            throw new Error ()

        }
    };    
};