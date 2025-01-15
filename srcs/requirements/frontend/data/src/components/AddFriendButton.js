import { useWebSocket } from '../contexts/WebSocketContext.js';
import { useUser } from '../contexts/UserContext.js';
import { useState } from 'react';

const AddFriendButton = () => {
  const [targetUsername, setTargetUsername] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const { sendFriendRequest } = useUser();

  const handleAddFriend = async () => {
    try {
      await sendFriendRequest(targetUsername);
    } catch (error) {
      console.error(error.message);
    }
  };

  if (isAdding) {
    return (
      <div>
        <input 
          type="text"
          value={targetUsername}
          onChange={(e) => setTargetUsername(e.target.value)}
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
