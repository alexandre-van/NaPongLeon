import { useState, useEffect } from 'react';
import useNicknameUpdate from '../hooks/useNicknameUpdate.js';

const NicknameForm = ({ onNicknameUpdate }) => {
  const [nicknameForm, setNicknameForm] = useState('');
  const { updateNickname, error } = useNicknameUpdate();
  const [actualNickname, setActualNickname] = use

  useEffect(() => {
    const fetchNickname = async () => {
    };
  }, []);

  const handleNicknameChange = (e) => {
    setNicknameForm(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = onNicknameUpdate(nicknameForm);
    if (success) {


    }
  };

  return (
    <div>
      <label htmlFor="actual-nickname">Actual nickname:</label>
      <p>{actualNickname}</p>
      <form onSubmit={handleSubmit}>
        <label htmlFor="nickname">Update Nickname</label>
        <input
          type="text"
          id="nickname"
          name="nickname"
          value={nicknameForm}
          onChange={handleNicknameChange}
          placeholder="Enter your new nickname"
        />
        <button type="submit">Update nickname</button>
        {error && <p>{error}</p>}
      </form>
    </div>
  );
};

export default NicknameForm;
