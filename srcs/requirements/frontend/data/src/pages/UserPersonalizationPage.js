import { useState } from 'react';
import { Link } from 'react-router-dom';
import AvatarUpload from '../components/AvatarUpload';
import NicknameForm from '../components/NicknameForm';
import Setup2FA from '../components/Setup2FA';
import useAvatarUpload from '../hooks/useAvatarUpload';
import useNicknameUpdate from '../hooks/useNicknameUpdate';
import { useUser } from '../contexts/UserContext';

function UserPersonalizationPage() {
  const [error, setError] = useState(null);
  const [activeSection, setActiveSection] = useState(null);
  const { updateAvatar } = useAvatarUpload();
  const { updateNickname } = useNicknameUpdate();
  const { user, notFrom42 } = useUser();

  const handleSubmit = async (type, data) => {
    const { error, value } = data;
    if (error) {
      setError(error);
      return;
    }

    try {
      if (type === 'nickname') await updateNickname(value);
      if (type === 'avatar') await updateAvatar(value);
      setError(null);
    } catch (updateError) {
      setError(updateError.response.data.errors[0] || 'An error occurred');
    }
  };

  const getTitle = () => {
    switch (activeSection) {
      case 'nickname':
        return 'Update Nickname';
      case 'avatar':
        return 'Change Avatar';
      case '2fa':
        return '2FA Settings';
      default:
        return 'Personalize Profile';
    }
  };

  const renderContent = () => {
    if (!activeSection) {
      return (
        <>
          <div style={{
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "20px",
            textAlign: "center",
          }}>
            <img
              src={user.avatar_url}
              alt={user.username}
              style={{
                width: "100px",
                height: "100px",
                borderRadius: "50%",
                marginBottom: "15px",
              }}
            />
            <h1 style={{ fontSize: "36px", fontWeight: "bold", marginBottom: "5px" }}>
              {user.username}
            </h1>
            {user.nickname && (
              <p style={{ fontSize: "24px", marginTop: "6px" }}>
                {user.nickname}
              </p>
            )}
          </div>

          {/* Buttons section */}
          <div style={{ marginTop: "30px", textAlign: "center" }}>
            <button
              onClick={() => setActiveSection('nickname')}
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
              Update Nickname
            </button>
            <button
              onClick={() => setActiveSection('avatar')}
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
              Change Avatar
            </button>
            {notFrom42 && <button
              onClick={() => setActiveSection('2fa')}
              style={{
                display: "block",
                margin: "10px auto",
                backgroundColor: "#FFA500",
                color: "white",
                border: "none",
                padding: "10px 20px",
                borderRadius: "10px",
                cursor: "pointer",
              }}
            >
              2FA Settings
            </button>}
            <Link
              to="/profile"
              style={{
                display: "block",
                margin: "10px auto",
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
            </Link>
          </div>
        </>
      );
    }

    return (
      <div className="space-y-4">
        {activeSection === 'nickname' && (
          <NicknameForm onSubmit={(data) => handleSubmit('nickname', data)} onError={setError} />
        )}
        {activeSection === 'avatar' && (
          <AvatarUpload onSubmit={(data) => handleSubmit('avatar', data)} onError={setError} />
        )}
        {activeSection === '2fa' && (
          <Setup2FA onError={setError} />
        )}

        <button
          onClick={() => setActiveSection(null)}
          style={{
            display: "block",
            margin: "10px auto",
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
    );
  };

  return (
    <div className="profile" style={{ paddingTop: '50px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '20px' }}>{getTitle()}</h1>
      
      <div style={{
        border: '2px solid #fff',
        padding: '20px',
        borderRadius: '10px',
        backgroundColor: 'transparent',
        maxWidth: '600px',
        margin: '0 auto',
      }}>
        {renderContent()}

        {error && (
          <div className="mt-4 p-3 bg-red-50 text-red-600 rounded">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default UserPersonalizationPage;
