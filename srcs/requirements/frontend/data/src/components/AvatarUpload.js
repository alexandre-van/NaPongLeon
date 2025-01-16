import { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';
import Avatar from './Avatar';

const AvatarUpload = ({ onSubmit, onError }) => {
  const { user, getAvatarUrl } = useUser();
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
  }, [user]);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image')) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
    } else {
      setSelectedFile(null);
      setPreview(null);
      onError('Please select a valid image file');
    }
  };

  const handleUpdate = () => {
    if (!selectedFile) {
      onSubmit({ value: null, error: 'Please select an image file' });
      return;
    }
    onSubmit({ value: selectedFile, error: null });
  };

  const avatarUrl = preview || getAvatarUrl();

  return (
    <div>
      <Avatar user={{ ...user, avatar_url: avatarUrl }} />
      <input type="file" onChange={handleFileSelect} accept="image/*" />
      <button onClick={handleUpdate} disabled={!selectedFile}>Upload Avatar</button>
    </div>
  );
};

export default AvatarUpload;
