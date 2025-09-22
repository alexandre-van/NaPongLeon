import { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext.js';
import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

const NotifButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null); // Ref pour le conteneur du menu
  const { isAuthenticated } = useUser(); 
  const { notifications, setNotifications } = useWebSocket();
  const [localNotifications, setLocalNotifications] = useState([]);

  useEffect(() => {
    if (!isAuthenticated) {
      if (localNotifications.length > 0 || notifications.length > 0) {
        setLocalNotifications([]);
        setNotifications([]);
      }
    } else if (Array.isArray(notifications) && notifications !== localNotifications) {
      setLocalNotifications(notifications);
    }
  }, [isAuthenticated, notifications]);

  const unreadNotificationsCount = localNotifications.filter(notification => !notification.is_read).length;

  const handleAcceptFriendRequest = async (notificationId) => {
    try {
      await api.patch('/authentication/friends/requests/', { notificationId });
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleRejectFriendRequest = async (notificationId) => {
    try {
      await api.delete('/authentication/friends/requests/', {
        data: { id: notificationId },
      });
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteNotification = async (notificationId) => {
    try {
      await api.delete('/authentication/notifications/', {
        data: { id: notificationId },
      });
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
    } catch (err) {
      console.error(err);
    }
  };

  // Fermer le menu si on clique en dehors
  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('click', handleOutsideClick);
    }

    return () => {
      document.removeEventListener('click', handleOutsideClick);
    };
  }, [isOpen]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <button
        onClick={(e) => {
          e.stopPropagation(); // Empêche la propagation de l'événement
          setIsOpen(!isOpen);
        }}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          backgroundColor: '#333',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          zIndex: 1000,
          boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
        }}
      >
        🔔
        {unreadNotificationsCount > 0 && (
          <div
            style={{
              position: 'absolute',
              top: '5px',
              right: '5px',
              backgroundColor: '#f44336',
              color: 'white',
              fontSize: '14px',
              fontWeight: 'bold',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {unreadNotificationsCount}
          </div>
        )}
      </button>

      {isOpen && (
        <div
          ref={menuRef} // Ref pour le conteneur
          style={{
            position: 'fixed',
            bottom: '80px',
            right: '20px',
            backgroundColor: '#333',
            borderRadius: '8px',
            padding: '20px',
            width: '400px',
            maxHeight: '80vh',
            overflowY: 'auto',
            zIndex: 1000,
            boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
          }}
        >
          <h3 style={{ color: 'white', textAlign: "center", marginBottom: "15px" }}>Notifications</h3>
          <div
            style={{
              maxHeight: "400px",
              overflowY: "auto",
              borderRadius: "8px",
              padding: "10px",
              backgroundColor: '#444',
            }}
          >
            {!localNotifications || localNotifications.length === 0 ? (
              <p style={{ color: 'white', textAlign: 'center' }}>No notifications yet.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {localNotifications.map((notification) => {
                  if (!notification) return null;

                  return (
                    <li
                      key={notification.id}
                      style={{
                        marginBottom: "10px",
                        backgroundColor: '#555',
                        padding: '10px',
                        borderRadius: '5px',
                        color: 'white',
                      }}
                    >
                      {notification.notification_type === "friend_request" && (
                        <div
                          style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                        >
                          <span>Friend request from {notification.sender__username}</span>
                          <div>
                            <button
                              onClick={() => handleAcceptFriendRequest(notification.id)}
                              style={{
                                backgroundColor: "#4CAF50",
                                color: "white",
                                border: "none",
                                padding: "5px 10px",
                                borderRadius: "5px",
                                cursor: "pointer",
                                marginRight: "5px",
                              }}
                            >
                              Accept
                            </button>
                            <button
                              onClick={() => handleRejectFriendRequest(notification.id)}
                              style={{
                                backgroundColor: "#ff4444",
                                color: "white",
                                border: "none",
                                padding: "5px 10px",
                                borderRadius: "5px",
                                cursor: "pointer",
                              }}
                            >
                              Reject
                            </button>
                          </div>
                        </div>
                      )}
                      {notification.notification_type === "friend_request_accepted" && (
                        <div
                          style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                        >
                          <span>{notification.sender__username} has accepted your friend request</span>
                          <button
                            onClick={() => handleDeleteNotification(notification.id)}
                            style={{
                              backgroundColor: "#666",
                              color: "white",
                              border: "none",
                              padding: "5px 10px",
                              borderRadius: "5px",
                              cursor: "pointer",
                            }}
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default NotifButton;
