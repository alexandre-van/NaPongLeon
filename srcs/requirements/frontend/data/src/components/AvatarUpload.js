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

