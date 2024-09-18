
const Avatar = ({ user, size = 100}) => {

  return (
    <div>
      <img
        src={user.avatar_url}
        alt={user.username}
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          objectFit: 'cover'
        }}
        onError={(e) => {
          console.error('Error loading image:', e);
        }}
      />
    </div>
  );
};

export default Avatar;
