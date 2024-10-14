import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext.js';
import AddFriendButton from './AddFriendButton.js';
import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

const FriendsList = () => {
//  const { friends, socket } = useWebSocket();
  const { user } = useUser();
  const [notifications, setNotifications] = useState([]);
  const [friends, setFriends] = useState([]);

  const checkFriends = useCallback(async () => {
    try {
      console.log('checkFriends');
      const response = await api.get('/authentication/friends/');
      console.log(response);
      setFriends(response.data.data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const checkNotifications = useCallback(async () => {
    try {
      console.log('checkNotifications');
      const response = await api.get('/authentication/notifications/');
      console.log(response);
      setNotifications(response.data.data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    checkNotifications();
  }, [checkNotifications]);

  useEffect(() => {
    checkFriends();
  }, [checkFriends]);

  const handleAcceptFriendRequest = async (notificationId) => {
    try {
      console.log('handleAcceptFriendRequest');
      const data = {
        notificationId: notificationId,
      };
      const response = await api.patch('/authentication/friends/requests/', data);
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
          default:
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
              {friend.username}
              {friend.status === 'online' && <span> (Online)</span>}
              <button onClick={() => handleDeleteFriend(friend.id)}>
                Remove friend
              </button>
            </li>
          ))}
        </ul>
      )}
      <h4>Notifications</h4>
      {notifications.length === 0 ? (
        <p>No notifications yet</p>
      ) : (
        <ul>
          {notifications.map((notification) => (
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
          ))}
        </ul>
      )}
    </div>
  );
};

export default FriendsList;
