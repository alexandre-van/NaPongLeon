import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useWebSocket } from '../contexts/WebSocketContext.js';
import AddFriendButton from './AddFriendButton.js';
import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

const FriendsList = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useUser();
  const { notifications, setNotifications, friends, setFriends } = useWebSocket();
  const [localNotifications, setLocalNotifications] = useState([]);
  const [localFriends, setLocalFriends] = useState([]);
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [friendStatuses, setFriendStatuses] = useState({});

  useEffect(() => {
    if (Array.isArray(notifications)) {
      setLocalNotifications(notifications);
    }
  }, [notifications]);

  useEffect(() => {
    if (Array.isArray(friends)) {
      setLocalFriends(friends);
    }
  }, [friends]);

  // Requête pour récupérer le statut des amis en ligne
  const fetchFriendStatuses = async () => {
    const onlineFriends = friends.filter(friend => friend.is_online);
    const statuses = {};
    for (const friend of onlineFriends) {
      try {
        const { data } = await api.get(`/game_manager/get_status/username=${friend.username}`);
        statuses[friend.id] = data.data; // Inclut le statut et le mode de jeu
      } catch (err) {
        console.error(`Error fetching status for ${friend.username}:`, err);
      }
    }
    setFriendStatuses(statuses);
  };

  useEffect(() => {
    if (isAuthenticated && friends.length > 0) {
      const intervalId = setInterval(() => {
        fetchFriendStatuses();
      }, 3000);
      return () => clearInterval(intervalId);
    }
  }, [isAuthenticated, friends]);
  
  useEffect(() => {
    fetchFriendStatuses();
  }, [isAuthenticated, friends]);

  if (!isAuthenticated) {
    return null;
  }

  const getStatusColor = (status) => {
    switch (status) {
      case "inactive": return "green";
      case "pending": return "orange";
      case "spectate": return "yellow";
      case "in_queue":
      case "loading_game":
      case "in_game": return "blue";
      case "waiting_for_players": 
      case "pending": return "orange";
      default: return "black";
    }
  };

  const getStatusTxt = (status) => {
    switch (status) {
        case "inactive": return "Online";
        case "spectate": return "Spectate";
        case "pending": return "Expected";
        case "in_queue": return "In queue";
        case "in_game":
        case "loading_game": return "In game";
        case "waiting_for_players": return "Waiting";
        default: return "";
    }
  };


  const handleNavigateToFriendGameHistory = async (username) => {
    navigate("/gamehistory", { state: { username } });
  };

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

  const handleDeleteFriend = async (friendId) => {
    try {
      const response = await api.delete('/authentication/friends/', {
        data: { friendId },
      });
      if (response.status === 200) {
        setFriends(prev => prev.filter(friend => friend.id !== friendId));
        setSelectedFriend(null);
      }
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

  function handleSpectateButton(friendStatuses, selectedFriend, navigate) {
    const friendStatus = friendStatuses[selectedFriend.id];
  
    if (
      friendStatus?.status === "in_game" &&
      friendStatus?.game_id &&
      (friendStatus?.game_service === "pong" || friendStatus?.game_service === "tournament")
    ) {
      // Récupérer les informations nécessaires
      const gameServiceUrl = `${window.location.protocol}/api/${friendStatus.game_service}`;
      const gameId = friendStatus.game_id;
  
      // Naviguer vers la page de spectateur
      navigate("/pong/ingame", { state: { gameService: gameServiceUrl, gameId: gameId } });
    } else {
      console.error("Impossible de spectate : aucune partie valide trouvée.");
    }
  }

  return (
    <div style={{ display: "flex", justifyContent: "center", gap: "20px", padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Liste des amis */}
      {!selectedFriend ? (
        <div style={{ flex: 1, maxWidth: "500px" }}>
          <h3 style={{ textAlign: "center", marginBottom: "15px" }}>Friends List</h3>
          <div style={{
            maxHeight: "600px",
            overflowY: "auto",
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "10px",
          }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              padding: "10px",
              borderRadius: "5px",
              cursor: "pointer",
              marginBottom: "10px",
              backgroundColor: "#f8f8f8",
              transition: "background-color 0.3s",
            }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f0f0f0"}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#f8f8f8"}
            >
              <div style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                marginRight: "10px",
                backgroundColor: "#e0e0e0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "24px"
              }}>
                +
              </div>
              <AddFriendButton />
            </div>



            {friends.length === 0 ? (
              <p style={{ textAlign: "center" }}>No friends yet.</p>
            ) : (
              <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
                {localFriends.map((friend) => (
                  <li
                    key={friend.id}
                    onClick={() => setSelectedFriend(friend)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      padding: "10px",
                      borderRadius: "5px",
                      cursor: "pointer",
                      transition: "background-color 0.3s",
                      marginBottom: "5px",
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f0f0f0"}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                  >
                    <img
                      src={friend.avatar ? `/media/${friend.avatar}` : "/static_files/images/default_avatar.png"}
                      alt={`${friend.username}'s avatar`}
                      style={{
                        width: "40px",
                        height: "40px",
                        borderRadius: "50%",
                        marginRight: "10px",
                      }}
                    />
                    <span style={{ flexGrow: 1 }}>{friend.username}</span>
                    <span style={{
                      color: friend.is_online ? getStatusColor(friendStatuses[friend.id]?.status) || "green" : "gray",
                      marginLeft: "10px"
                    }}>
                      {friend.is_online ? (getStatusTxt(friendStatuses[friend.id]?.status) || "Online") : "Offline"}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      ) : (
        <div style={{ flex: 1, maxWidth: "40%", overflow: "hidden" }}>
          <h3 style={{ textAlign: "center", marginBottom: "15px" }}>Friend Menu</h3>
          <div style={{
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "20px",
            textAlign: "center",
          }}>
            <img
              src={selectedFriend.avatar ? `/media/${selectedFriend.avatar}` : "/static_files/images/default_avatar.png"}
              alt={`${selectedFriend.username}'s avatar`}
              style={{
                width: "100px",
                height: "100px",
                borderRadius: "50%",
                marginBottom: "15px",
              }}
            />
            <h1 style={{ fontSize: "36px", fontWeight: "bold", marginBottom: "5px" }}>
              {selectedFriend.username}
            </h1>
            <h2>{selectedFriend.nickname && (
                <p style={{ fontSize: '24px', marginTop: '6px' }}>
                    {selectedFriend.nickname}
                </p>
            )}
            </h2>
            <span
              style={{
                color: selectedFriend.is_online 
                  ? getStatusColor(friendStatuses[selectedFriend.id]?.status) || "green"
                  : "gray",
                fontSize: "24px",
              }}
            >
            {selectedFriend.is_online
              ? `${getStatusTxt(friendStatuses[selectedFriend.id]?.status) || "Online"}${friendStatuses[selectedFriend.id]?.game_mode ? ` - ${friendStatuses[selectedFriend.id]?.game_mode}` : ""}`
              : "Offline"}
            
            </span>
    
    {/* Espacement entre le statut et les boutons */}
    <div style={{ marginBottom: "30px" }}></div>

    {friendStatuses[selectedFriend.id]?.status === "in_game" && friendStatuses[selectedFriend.id]?.game_id && (friendStatuses[selectedFriend.id]?.game_service === "pong" || friendStatuses[selectedFriend.id]?.game_service === "tournament") &&
                (
                  <button
                    onClick={() => handleSpectateButton(friendStatuses, selectedFriend, navigate)}
        style={{
          display: "block",
          margin: "10px auto", // Centrer horizontalement
          backgroundColor: "#4CAF50",
          color: "white",
          border: "none",
          padding: "10px 20px",
          borderRadius: "10px",
          cursor: "pointer",
        }}
      >
        Spectate
      </button>
    )}
    
    <button
      onClick={() => {
        handleNavigateToFriendGameHistory(selectedFriend.username)
      }}
      style={{
        display: "block",
        margin: "10px auto", // Centrer horizontalement
        backgroundColor: "#008CBA",
        color: "white",
        border: "none",
        padding: "10px 20px",
        borderRadius: "10px",
        cursor: "pointer",
      }}
    >
      Game History
    </button>
    
    <button
      onClick={() => handleDeleteFriend(selectedFriend.id)}
      style={{
        display: "block",
        margin: "10px auto", // Centrer horizontalement
        backgroundColor: "red",
        color: "white",
        border: "none",
        padding: "10px 20px",
        borderRadius: "10px",
        cursor: "pointer",
      }}
    >
      Remove Friend
    </button>

    <button
      onClick={() => setSelectedFriend(null)}
      style={{
        display: "block",
        margin: "10px auto", // Centrer horizontalement
        backgroundColor: "#f1f1f1",
        color: "#333",
        border: "none",
        padding: "10px 20px",
        borderRadius: "10px",
        cursor: "pointer",
        fontWeight: "bold",
      }}
    >
      Return
    </button>
  </div>
</div>

      
      )}
      {/* Notifications */}
      <div style={{ flex: 1, maxWidth: "40%", overflow: "hidden" }}>
      <h3 style={{ textAlign: "center", marginBottom: "15px" }}>Notifications</h3>
        <div style={{
          maxHeight: "400px",
          overflowY: "auto",
          border: "1px solid #ddd",
          borderRadius: "8px",
          padding: "10px",
        }}>
          {!localNotifications || localNotifications.length === 0 ? (
            <p>No notifications yet.</p>
          ) : (
            <ul>
              {localNotifications.map((notification) => {
                if (!notification) return null;

                return (
                  <li key={notification.id} style={{ marginBottom: "10px" }}>
                    {notification.notification_type === "friend_request" && (
                      <>
                        Friend request from {notification.sender__username}
                        <button
                          onClick={() => handleAcceptFriendRequest(notification.id)}
                          style={{ marginLeft: "10px" }}
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleRejectFriendRequest(notification.id)}
                          style={{ marginLeft: "10px" }}
                        >
                          Reject
                        </button>
                      </>
                    )}
                    {notification.notification_type === "friend_request_accepted" && (
                      <>
                        {notification.sender__username} has accepted your friend request
                        <button
                          onClick={() => handleDeleteNotification(notification.id)}
                          style={{ marginLeft: "10px" }}
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </li>
                )}
              )}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default FriendsList;