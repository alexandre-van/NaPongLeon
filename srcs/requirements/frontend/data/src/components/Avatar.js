const Avatar = ({ user }) => {
  return (
    <div className="avatar-container">
      <img
        src={user.avatar_url}
        alt={user.username}
        className="avatar-image"
        onError={(e) => {
          console.error('Error loading image:', e);
        }}
      />
    </div>
  );
};

export default Avatar;