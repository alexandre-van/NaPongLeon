import { useUser } from '../contexts/UserContext.js';

const FriendsList = () => {
  const { user } = useUser();

  return (
    <div>
      <h3>Friends list</h3>
    </div>
  );
};

export default FriendsList;
