import PropTypes from "prop-types";

export default function PlayButton({ onClick }) {
  return (
    <button 
        className="play-button-mode btn btn-outline-warning" 
        onClick={handlePlayButton} 
        style={{ marginTop: "10px" }}
    >
        Play {gameMode}
    </button>
  );
}

PlayButton.propTypes = {
  onClick: PropTypes.func.isRequired,
};
