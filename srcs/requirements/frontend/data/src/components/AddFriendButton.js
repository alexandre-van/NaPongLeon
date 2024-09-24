import { useWebSocket } from '../contexts/WebSocketContext.js';
import { useState } from 'react';

const AddFriendButton = () => {
  const [friendId, setFriendId] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const { socket } = useWebSocket();

  const showInputAddButton = () => {
    return (
      <button onClick={handleAddFriend}>
        Add friend Final
      </button>
    );
  };

  const handleAddFriend = async () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const message = {
        action: 'send_request',
        target_user_id: friendId
      };
      socket.send(JSON.stringify(message));
      setFriendId('');
      setIsAdding(false);
    } else {
      console.error("WebSocket is not open. Unable to send friend request");
    }
  };

  if (isAdding) {
    return (
      <div>
        <input 
          type="text"
          value={friendId}
          onChange={(e) => setFriendId(e.target.value)}
          placeholder="Enter friend's ID"
        />
        <button onClick={handleAddFriend}>Add Friend</button>
        <button onClick={() => setIsAdding(false)}>Cancel</button>
      </div>
    );
  }

  return (
    <button onClick={() => setIsAdding(true)}>
      Add friend
    </button>
  );
};

export default AddFriendButton;
