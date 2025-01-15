import { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext.js';

const NicknameForm = ({ onSubmit, onError }) => {
  const [nickname, setNickname] = useState('');
  const { user } = useUser();
  const [currentNickname, setCurrentNickname] = useState('');

  const handleNicknameChange = (e) => setNickname(e.target.value);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ value: nickname, error: null });
  };

  useEffect(() => {
    setCurrentNickname(user.nickname);
  }, [handleSubmit]);

  return (
    <div className="nickname-form">
      <form onSubmit={handleSubmit}>
        <label htmlFor="current-nickname">Current nickname:</label>
        <p>{currentNickname || 'No nickname yet'}</p>

        <label htmlFor="nickname">New Nickname</label>
        <input
          type="text"
          id="nickname"
          name="nickname"
          value={nickname}
          onChange={handleNicknameChange}
          placeholder="Enter your new nickname"
        />
        <button type="submit">Update nickname</button>
      </form>
    </div>
  );
};

export default NicknameForm;
