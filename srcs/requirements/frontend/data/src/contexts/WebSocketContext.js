import React, { useState, useEffect, createContext, useContext, useCallback, useRef } from 'react';
import { useUser } from './UserContext.js';
import { useNavigate } from 'react-router-dom';
import api from '../services/api.js';


const WebSocketContext = createContext(null);

const getWindowURLinfo = () => {
  const host = window.location.hostname;
  const port = window.location.port;
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';

  return { host, port, protocol };
};

export const WebSocketProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [socket, setSocket] = useState(null);
  const [friends, setFriends] = useState([]);
  const { user, isAuthenticated, updateUser } = useUser();
  const socketRef = useRef(null);
  const navigate = useNavigate();

  const createWebSocketConnection = useCallback(async () => {
    if (!isAuthenticated || socketRef.current) {
      return;
    }

    try {
      // Get access_token from back-end
      const response = await api.get('/authentication/auth/token/get-access/');
      const wsToken = response.data.token;
      const { host, port, protocol } = getWindowURLinfo();

      const newSocket = new WebSocket(`${protocol}://${host}:${port}/ws/authentication/?token=${wsToken}/`);
      newSocket.onopen = () => {
        console.log('WebSocket connected');
        setSocket(newSocket);
        socketRef.current = newSocket;
      };

      newSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'friend_list_user_update':

            setFriends(prevFriends => {
              const newFriends = [...prevFriends];

              if (!newFriends.some(n => n.id === data.user.id)) {
                newFriends.push(data.user);
              }
              return newFriends;
            });
            break;

          case 'friend_status':
      
              if (user?.friends) {

                // Met à jour le statut de l'ami en fonction de son username
                const updatedFriends = user.friends.map((friend) =>
                  friend.username === data.friend  // Compare en fonction du nom de l'ami
                    ? { 
                        ...friend, 
                        status: data.status ? 'online' : 'offline',  // Met à jour le statut
                        is_online: data.status  // Ajoute is_online pour faciliter la gestion de l'état
                      }
                    : friend
                );
                updateUser({ friends: updatedFriends });  // Met à jour l'état de l'utilisateur

                // Etat local websocket
                setFriends(prevFriends => prevFriends.map(friend =>
                  friend.username === data.friend
                  ? {
                      ...friend,
                      status: data.status ? 'online' : 'offline',
                      is_online: data.status,
                      avatar: data.avatar
                  }
                  : friend
                ));
              }
              break;
      
          case 'friend_deleted': 

            if (!data.friend_id) {
                console.error("Invalid friend ID received:", data.friend_id);
                break;
            }
        
            if (user?.friends) {
                const updatedFriends = [...user.friends].filter(
                  friend => friend.id !== data.friend_id
                );

                setFriends(updatedFriends);
                updateUser(prevUser => ({
                  ...prevUser,
                  friends: updatedFriends
                }));

            } else {
                console.warn("User does not have a friends list or user object is null.");
            }
            break;

          case 'notification':
            setNotifications(prevNotifs => {
              const newNotifs = [...prevNotifs];
              // Vérifier si la notification n'existe pas déjà
              if (!newNotifs.some(n => n.id === data.id)) {
                newNotifs.push(data);
              }
              return newNotifs;
            });
            break;
          default:
            console.log('Unknown message type: ', data.type);
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
    setFriends,
    notifications,
    setNotifications
  }), [socket, friends, notifications]);

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => useContext(WebSocketContext);
