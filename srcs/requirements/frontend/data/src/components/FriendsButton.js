import { useState } from 'react';
import { useUser } from '../contexts/UserContext.js';
import { useWebSocket } from '../contexts/WebSocketContext.js';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import AddFriendButton from './AddFriendButton.js';
import api from '../services/api.js';

const FriendsButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, friends, setFriends, checkFriends } = useUser();
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [friendStatuses, setFriendStatuses] = useState({});
  const navigate = useNavigate()

  useEffect(() => {
    checkFriends();
  }, [checkFriends]);

  const fetchFriendStatuses = async () => {
    const onlineFriends = friends.filter(friend => friend.is_online);
    const statuses = {};
    for (const friend of onlineFriends) {
      try {
        const { data } = await api.get(`/game_manager/get_status/username=${friend.username}`);
        statuses[friend.id] = data.data;
      } catch (err) {
        console.error(`Error fetching status for ${friend.username}:`, err);
      }
    }
    setFriendStatuses(statuses);
  };

  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchFriendStatuses();
    }, 10000);
  
    return () => clearInterval(intervalId);
  }, [friends]);
  
  useEffect(() => {
    fetchFriendStatuses();
  }, [friends]);

  const getStatusColor = (status) => {
    switch (status) {
      case "inactive": return "green";
      case "pending": return "orange";
      case "in_queue":
      case "in_game": return "blue";
      case "waiting":
      case "loading_game": return "yellow";
      default: return "black";
    }
  };

  const getStatusTxt = (status) => {
    switch (status) {
      case "inactive": return "Online";
      case "pending": return "Expected in game";
      case "in_queue": return "In queue";
      case "in_game": return "In game";
      case "waiting": return "Waiting";
      case "loading_game": return "In game";
      default: return "";
    }
  };

  const handleNavigateToFriendGameHistory = async (username) => {
    navigate("/gamehistory", { state: { username } });
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

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '80px',
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
          zIndex: 1000
        }}
      >
        👥
      </button>

      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '80px',
          right: '80px',
          backgroundColor: '#333',
          borderRadius: '8px',
          padding: '20px',
          width: '400px',
          maxHeight: '80vh',
          overflowY: 'auto',
          zIndex: 1000
        }}>
          {!selectedFriend ? (
            <div>
              <h3 style={{ color: 'white', textAlign: "center", marginBottom: "15px" }}>Friends List</h3>
              <div style={{
                maxHeight: "600px",
                overflowY: "auto",
                borderRadius: "8px",
                padding: "10px",
                backgroundColor: '#444'
              }}>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  padding: "10px",
                  borderRadius: "5px",
                  cursor: "pointer",
                  marginBottom: "10px",
                  backgroundColor: "#555",
                  transition: "background-color 0.3s",
                }}>
                  <div style={{
                    width: "40px",
                    height: "40px",
                    borderRadius: "50%",
                    marginRight: "10px",
                    backgroundColor: "#666",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "24px",
                    color: 'white'
                  }}>
                    +
                  </div>
                  <AddFriendButton />
                </div>

                {friends.length === 0 ? (
                  <p style={{ textAlign: "center", color: 'white' }}>No friends yet.</p>
                ) : (
                  <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
                    {friends.map((friend) => (
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
                          backgroundColor: '#555',
                          color: 'white'
                        }}
                      >
                        <img
                          src={friend.avatar ? `media/${friend.avatar}` : "/static_files/images/default_avatar.png"}
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
            <div>
              <h3 style={{ color: 'white', textAlign: "center", marginBottom: "15px" }}>Friend Menu</h3>
              <div style={{
                padding: "20px",
                textAlign: "center",
                backgroundColor: '#444',
                borderRadius: '8px'
              }}>
                <img
                  src={selectedFriend.avatar ? `media/${selectedFriend.avatar}` : "/static_files/images/default_avatar.png"}
                  alt={`${selectedFriend.username}'s avatar`}
                  style={{
                    width: "100px",
                    height: "100px",
                    borderRadius: "50%",
                    marginBottom: "15px",
                  }}
                />
                <h1 style={{ fontSize: "36px", fontWeight: "bold", marginBottom: "5px", color: 'white' }}>
                  {selectedFriend.username}
                </h1>
                <span style={{
                  color: selectedFriend.is_online 
                    ? getStatusColor(friendStatuses[selectedFriend.id]?.status) || "green"
                    : "gray",
                  fontSize: "24px",
                }}>
                  {selectedFriend.is_online
                    ? `${getStatusTxt(friendStatuses[selectedFriend.id]?.status) || "Online"}${friendStatuses[selectedFriend.id]?.game_mode ? ` - ${friendStatuses[selectedFriend.id]?.game_mode}` : ""}`
                    : "Offline"}
                </span>

                <div style={{ marginBottom: "30px" }}></div>

                {selectedFriend.status === "in_game" && (
                  <button
                    onClick={() => {/* Logique de spectate */}}
                    style={{
                      display: "block",
                      margin: "10px auto",
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
                  onClick={() => handleNavigateToFriendGameHistory(selectedFriend.username)}
                  style={{
                    display: "block",
                    margin: "10px auto",
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
                    margin: "10px auto",
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
                    margin: "10px auto",
                    backgroundColor: "#666",
                    color: "white",
                    border: "none",
                    padding: "10px 20px",
                    borderRadius: "10px",
                    cursor: "pointer",
                  }}
                >
                  Return
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default FriendsButton;