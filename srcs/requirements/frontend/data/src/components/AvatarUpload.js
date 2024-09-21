import { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext.js';
import Avatar from './Avatar.js';

const AvatarUpload = ({ onUpload, onError }) => {
  const { user, getAvatarUrl } = useUser();
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    console.log('User in AvatarUpload:', user);
  }, [user]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.substr(0, 5) === "image") {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
    } else {
      setSelectedFile(null);
      setPreview(null);
      onError("Please select an image file");
    }
  };

  const handleUpdate = async () => {
    if (!selectedFile) {
      onUpload({ file: null, error: "Please select an image file "});
      return;
    }
    onUpload({ file: selectedFile, error: null });
  };

  const avatarUrl = preview || getAvatarUrl();

  return (
    <div>
      <Avatar user={{ ...user, avatar_url: avatarUrl }} />
      <input type="file" onChange={handleFileSelect} accept="image/*" />
      <button onClick={handleUpdate} disabled={!selectedFile}>
        Upload Avatar
      </button>
    </div>
  );
};

export default AvatarUpload;



//      <input type="file" onChange={handleFileSelect} accept="image/*" disabled={avatarLoading} />
//      <button onClick={handleUpdate} disabled={!selectedFile || avatarLoading}>
        //{avatarLoading ? 'Uploading...' : 'Upload Avatar'}
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
