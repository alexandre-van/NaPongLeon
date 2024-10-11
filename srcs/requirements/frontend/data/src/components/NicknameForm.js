import { useUser } from '../contexts/UserContext.js';
import { useState } from 'react';

const NicknameForm = ({ onUpload, onError }) => {
  const [nicknameForm, setNicknameForm] = useState(null);
  const { user } = useUser();

  const handleNicknameChange = (e) => {
    setNicknameForm(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!nicknameForm) {
      onUpload({ nickname: null, error: "Please submit a nickname"});
      return;
    }
    onUpload({ nickname: nicknameForm, error: null });
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="current nickname">Current nickname: {user.nickname ? user.nickname : 'No nickname yet'}</label>
        <label htmlFor="update nickname">Update Nickname</label>
        <input
          type="text"
          id="nickname"
          name="nickname"
          value={nicknameForm}
          onChange={handleNicknameChange}
          placeholder="Enter your new nickname"
        />
        <button type="submit">Update nickname</button>
      </form>
    </div>
  );
};

export default NicknameForm;
