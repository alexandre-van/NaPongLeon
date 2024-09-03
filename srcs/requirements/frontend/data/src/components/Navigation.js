export default function Navigation({ navigate }) {
    return (
        <div role='nav' className="nav-container">
            <div className="home-nav">
                <button onClick={() => navigate('home')}>SPICE PONG</button>
            </div>
            <div className="main-nav">
                <button onClick={() => navigate('about')}>ABOUT</button>
                <button onClick={() => navigate('news')}>NEWS</button>
                <button onClick={() => navigate('game-modes')}>GAME MODES</button>
                <button onClick={() => navigate('leaderboard')}>LEADERBOARD</button>
            </div>
            <div className="right-nav">
                <button onClick={() => navigate('login')}>LOG IN</button>
            </div>
        </div>
    );
}