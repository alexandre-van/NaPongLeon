import { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext.js';
import useAvatarUpload from '../hooks/useAvatarUpdate.js';
import Avatar from './Avatar.js';

const AvatarUpload = () => {
  const { user } = useUser();
  const { updateAvatar, loading: avatarLoading } = useAvatarUpload();

  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('User in AvatarUpload:', user);
  }, [user]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.substr(0, 5) === "image") {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setError(null);
    } else {
      setSelectedFile(null);
      setPreview(null);
      setError("Please select an image file");
    }
  };

  const handleUpdate = async () => {
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }
    try {
      await updateAvatar(selectedFile);
      setSelectedFile(null);
      setPreview(null);
      setError(null);
      console.log('Avatar uploaded successfully');
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div>
      <Avatar user={{ ...user, avatar_url: preview || user.avatar_url }} />
      <input type="file" onChange={handleFileSelect} accept="image/*" disabled={avatarLoading} />
      <button onClick={handleUpdate} disabled={!selectedFile || avatarLoading}>
        {avatarLoading ? 'Uploading...' : 'Upload Avatar'}
      </button>
      {error && <p>{error}</p>}
    </div>
  );
};

export default AvatarUpload;





/*const AvatarUpload = ({ user, onAvatarUpdate }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!selectedFile) {
      setPreview(null);
      return;
    }

    const objectUrl = URL.createObjectURL(selectedFile);
    setPreview(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [selectedFile]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.substr(0, 5) === "image") {
      setSelectedFile(file);
      setError(null);
    } else {
      setSelectedFile(null);
      setError("Please select an image file");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append('avatar', selectedFile);

    try {
      const uploadResponse = api.post('/authentication/upload-avatar/', formData, {
        headers: {
          'Content-Type': "multipart/form-data",
        }
      });

      if (uploadResponse.data.message === 'Avatar uploaded successfully') {
        const avatarResponse = await api.get('/authentication/get-avatar/');
        if (avatarResponse.data.avatar_url) {
          onAvatarUpdate(avatarResponse.data.avatar_url);
          setError(null);
          console.log('Avatar uploaded successfully');
        }
      } 
    } catch (error) {
      setError(error.response?.data?.error || "An error occured during upload");
    }
  };

  return (
    <div className="avatar-upload">
      <img
        src={preview}
        alt="Avatar preview"
        className="avatar-preview"
      />
      <input type="file" onChange={handleFileSelect} accept="image/*" />
      <button onClick={handleUpload} disabled={!selectedFile}>
        Upload Avatar
      </button>
    </div>
  );
};

export default AvatarUpload;*/
