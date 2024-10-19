/*import React, { createContext, useContext, useEffect, useState } from 'react';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { useUser } from './UserContext.js';

const WebSocketContext = createContext(null);

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const [authSocket, setAuthSocket] = useState(null);
  const { isAuthenticated, checkAuth } = useUser();

  const createSocket = useCallback((url) => {
    const socket = new ReconnectingWebSocket(url, [], {
      connectionTimeout: 10000,
    });

    socket.onopen = () => console.log(`WebSocket Connected: ${url}`);
    socket.onclose = () => console.log(`WebSocket Disconnected: ${url}`);

    return socket;
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      const authWs = createSocket(`ws://localhost:8080/ws/authentication/friend-requests/`);

      setAuthSocket(authWs);

      return () => {
        authWs.close();
      };
    }
  }, [isAuthenticated, createSocket]);

  const sendMessage = useCallback((socket, message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not open. Unable to send message.');
    }
  }, []);

  const sendAuthMessage = useCallback((message) => 
    sendMessage(authSocket, message), [sendMessage, authSocket]);

  return (
    <WebSocketContext.Provider value={{ authSocket, gameSocket, sendAuthMessage }}>
      {children}
    </WebSocketContext.Provider>
  );


};*/






import React, { useState, useEffect, createContext, useContext, useCallback, useRef } from 'react';
import { useUser } from './UserContext.js';
import api from '../services/api.js';

const WebSocketContext = createContext(null);

const getWindowURLinfo = () => {
  const host = window.location.hostname;
  const port = window.location.port;
  const protocol = window.location.protocol === 'http:' ? 'ws' : 'ws';

  return { host, port, protocol };
};

export const WebSocketProvider = ({ children }) => {
  const [friends, setFriends] = useState([]);
  const [socket, setSocket] = useState(null);
  const { isAuthenticated } = useUser();
  const socketRef = useRef(null);

  const createWebSocketConnection = useCallback(async () => {
    if (!isAuthenticated || socketRef.current) {
      return;
    }

    try {
      // Get access_token from back-end
      const response = await api.get('/authentication/auth/token/get-access/');
      const wsToken = response.data.token;
      const { host, port, protocol } = getWindowURLinfo();

      const newSocket = new WebSocket(`${protocol}://${host}:8080/ws/authentication/?token=${wsToken}/`);
      newSocket.onopen = () => {
        console.log('WebSocket connected');
        setSocket(newSocket);
        socketRef.current = newSocket;
      };

      newSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'friend_list_update') {
          setFriends(data.friends);
        }
      };

      newSocket.onclose = () => {
        console.log('WebSocket disconnected');
        setSocket(null);
        socketRef.current = null;
      }

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated && !socketRef.current) {
      createWebSocketConnection();
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [isAuthenticated, createWebSocketConnection]);
  
  const value = React.useMemo(() => ({
    socket,
    friends,
  }), [socket, friends]);

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => useContext(WebSocketContext);
