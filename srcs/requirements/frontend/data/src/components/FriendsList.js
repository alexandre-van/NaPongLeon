import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext.js';
import AddFriendButton from './AddFriendButton.js';
import { useUser } from '../contexts/UserContext.js';

const FriendsList = () => {
  const { friends, socket } = useWebSocket();
  const { user } = useUser();
  const [notifications, setNotifications] = useState([]);

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

  return (
    <div>
      <h3>Friends list</h3>
      <AddFriendButton />
      {friends.length === 0 ? (
        <p>No friends yet.</p>
      ) : (
        <ul>
          {friends.map((friend) => {
            <li key={friend.id}>
              {friend.username}
              {friend.status === 'online' && <span> (Online)</span>}
            </li>
          })}
        </ul>
      )}
      <h4>Notifications</h4>
      {notifications.length === 0 ? (
        <p>No notifications yet</p>
      ) : (
        <ul>
          {notifications.map((notification, index) => {
            <li key={index}>
              {notification.content}
              {notification.notification_type === 'friend_request_received' && (
                <button>
                  Accept Friendship
                </button>
              )}
            </li>
          })}
        </ul>
      )
      }
    </div>
  );
};

export default FriendsList;
