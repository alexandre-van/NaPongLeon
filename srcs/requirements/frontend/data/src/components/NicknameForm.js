import { useState } from 'react';

const NicknameForm = ({ onSubmit, onError }) => {
  const [nickname, setNickname] = useState('');

  const handleNicknameChange = (e) => setNickname(e.target.value);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ value: nickname, error: null });
  };

  return (
    <div className="nickname-form">
      <form onSubmit={handleSubmit}>
        <label htmlFor="current-nickname">Current nickname:</label>
        <p>{nickname || 'No nickname yet'}</p>

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
