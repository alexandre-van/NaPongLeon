import { useState, useEffect, useRef } from 'react';
import { useUser } from '../contexts/UserContext.js';
import { useNavigate } from 'react-router-dom';
import AddFriendButton from './AddFriendButton.js';
import api from '../services/api.js';
import { useWebSocket } from '../contexts/WebSocketContext.js';

const FriendsButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated } = useUser(); 
  const { friends, setFriends } = useWebSocket();
  const [localFriends, setLocalFriends] = useState([]);
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [friendStatuses, setFriendStatuses] = useState({});
  const navigate = useNavigate();

  // Référence pour le bouton et le menu
  const containerRef = useRef(null);

  useEffect(() => {
    if (isAuthenticated && Array.isArray(friends)) {
      setLocalFriends(friends);
    }
  }, [friends]);

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

  useEffect(() => {
    // Gestionnaire pour fermer le menu si clic à l'extérieur
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  if (!isAuthenticated) {
    return null;
  }

  const onlineFriendsCount = localFriends.filter(friend => friend.is_online).length;

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

  const sortedFriends = localFriends.sort((a, b) => b.is_online - a.is_online);

  return (
    <div ref={containerRef}>
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
        {onlineFriendsCount > 0 && (
          <div
            style={{
              position: 'absolute',
              top: '5px',
              right: '5px',
              backgroundColor: '#4CAF50',
              color: 'white',
              fontSize: '14px',
              fontWeight: 'bold',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: 0.75,
            }}
          >
            {onlineFriendsCount}
          </div>
        )}
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
                maxHeight: "450px",
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
                    {sortedFriends.map((friend) => (
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
            <div>
              <h3 style={{ color: 'white', textAlign: "center", marginBottom: "15px" }}>Friend Menu</h3>
              <div style={{
                padding: "20px",
                textAlign: "center",
                backgroundColor: '#444',
                borderRadius: '8px'
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
                <h1 style={{ fontSize: "36px", fontWeight: "bold", marginBottom: "5px", color: 'white' }}>
                  {selectedFriend.username}
                </h1>
                <h2>{selectedFriend.nickname && (
                  <p style={{ fontSize: '24px', marginTop: '6px' }}>
                      {selectedFriend.nickname}
                  </p>
                )}
                </h2>
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

                {friendStatuses[selectedFriend.id]?.status === "in_game" && friendStatuses[selectedFriend.id]?.game_id && (friendStatuses[selectedFriend.id]?.game_service === "pong" || friendStatuses[selectedFriend.id]?.game_service === "tournament") &&
                (
                  <button
                    onClick={() => handleSpectateButton(friendStatuses, selectedFriend, navigate)}
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
    </div>
  );
};

export default FriendsButton;
