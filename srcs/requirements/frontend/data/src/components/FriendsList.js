import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext.js';
import AddFriendButton from './AddFriendButton.js';
import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

const FriendsList = () => {
  const { user, setUser, friends, setFriends, checkFriends } = useUser();
  const { notifications, setNotifications } = useWebSocket();
  const [localNotifications, setLocalNotifications] = useState([]); // État local pour les notifications

  // Synchroniser l'état local avec les notifications du contexte
  useEffect(() => {
    if (Array.isArray(notifications)) {
      setLocalNotifications(notifications);
    }
  }, [notifications]);
  
  useEffect(() => {
    checkFriends()
  }, [checkFriends]);

  const loadExistingNotifications = useCallback(async () => {
    try {
      console.log('loadExistingNotifications');
      const response = await api.get('/authentication/notifications/');
      console.log(response);
      const formattedNotifications = response.data.data.map(notif => ({
        ...notif,
        notification_type: notif.notification_type || 'unknown'
      }));
      setNotifications(formattedNotifications);
    } catch (err) {
      console.error(err);
    }
  }, [setNotifications]);

  useEffect(() => {
    loadExistingNotifications();
  }, [loadExistingNotifications]);

  const handleAcceptFriendRequest = async (notificationId) => {
    try {
      console.log('handleAcceptFriendRequest');
      const data = {
        notificationId: notificationId,
      };
      const response = await api.patch('/authentication/friends/requests/', data);
      setNotifications(prev => 
        prev.filter(notif => notif.id !== notificationId)
      );
      checkFriends();
      console.log(response);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRejectFriendRequest = async (notificationId) => {
    try {
      console.log('handleRejectFriendRequest');
      const response = await api.delete('/authentication/friends/requests/', {
        data: {
          id: notificationId,
        }
      });
      setNotifications(prev => 
        prev.filter(notif => notif.id !== notificationId)
      );
      console.log(response);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteFriend = async (friendId) => {
    try {
      console.log('handleDeleteFriend');
      const response = await api.delete('/authentication/friends/', {
        data: {
          friendId: friendId,
        }
      });
      if (response.status === 200) {
        console.log('bonjour response status === 200');
        const updatedFriends = [...user.friends].filter(
          friend => friend.id !== friendId
        );

        setFriends(updatedFriends);
        updateUser(prevUser => ({
          ...prevUser,
          friends: updatedFriends
        }));
      }
      console.log(response);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteNotification = async (notificationId) => {
    try {
      console.log('handleDeleteNotification');
      const response = await api.delete('/authentication/notifications/', {
        data: {
          id: notificationId,
        }
      });
      setNotifications(prev => 
        prev.filter(notif => notif.id !== notificationId)
      );
      console.log(response);
    } catch (err) {
      console.error(err);
    }
  };

  /*




  useEffect(() => {
    if (socket) {
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(`data :\ndata.type = ${data.type}`);
        switch (data.type) {
          case 'notification':
            console.log(`New notification: ${data.content}`);
            console.log(`notification_type: ${data.notification_type}`)

            setNotifications(prev => [...prev, data]);
            break;
          case 'error':
            console.error(data.message);
            break;
          default:Friend request from user ID: avan￼Accept￼Reject
            console.log(data.message);
            break;
        }
        console.log(`notifications.length = ${notifications.length}`);
      };
    }
  }, [socket]);

  const handleMessage = useCallback((event) => {
    const data = JSON.parse(event.data);
    console.log(`data :\ndata.type = ${data.type}`);
    switch (data.type) {
      case 'notification':
        console.log(`New notification: ${data.content}`);
        console.log(`notification_type: ${data.notification_type}`)
        setNotifications(prev => [...prev, data]);
        break;
      case 'error':
        console.error(data.message);
        break;
      default:
        console.log(data.message);
        break;
    }
    console.log(`notifications.length = ${notifications.length}`);

    Friend request from user ID: avan￼Accept￼Reject
  });

  useEffect(() => {
    if (socket) {
      socket.addEventListener('message', handleMessage);
      return (
        socket.removeEventListener('message', handleMessage)
      );
    }
  }, [socket, handleMessage]);
  */

  return (
    <div>
      <h3>Friends list</h3>
      <AddFriendButton />
      {friends.length === 0 ? (
        <p>No friends yet.</p>
      ) : (
        <ul>
          {friends.map((friend) => (
            <li key={friend.id}>
              <span>{friend.username}</span>
              {friend.is_online ? (  // Utilisez is_online pour afficher le statut en ligne
                <span style={{ color: 'green', marginLeft: '10px' }}> (Online)</span>
              ) : (
                <span style={{ color: 'gray', marginLeft: '10px' }}> (Offline)</span>
              )}
              <button
                style={{ marginLeft: '15px' }}
                onClick={() => handleDeleteFriend(friend.id)}
              >
                Remove friend
              </button>
            </li>
          ))}
        </ul>
      )}





      <h4>Notifications</h4>
      {!localNotifications || localNotifications.length === 0 ? (
        <p>No notifications yet</p>
      ) : (
        <ul>
          {localNotifications.map((notification) => {
            if (!notification) return null;

            return (
            <li key={notification.id}>
              {notification.notification_type === 'friend_request' && (
                <>
                  Friend request from user ID: {notification.sender__username}
                  <button onClick={() => handleAcceptFriendRequest(notification.id)}>
                    Accept
                  </button>
                  <button onClick={() => handleRejectFriendRequest(notification.id)}>
                    Reject
                  </button>
                </>
              )}
              {notification.notification_type === 'friend_request_accepted' && (
                <>
                  {notification.sender__username} has accepted your friend request
                  <button onClick={() => handleDeleteNotification(notification.id)}>
                    Delete notification
                  </button>
                </>
              )}
            </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default FriendsList;