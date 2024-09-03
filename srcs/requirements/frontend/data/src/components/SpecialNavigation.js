export default function SpecialNavigation({ navigate }) {
    return (
        <div role='nav' className="nav-container">
            <div className="main-nav">
                <button onClick={() => navigate('home')}>SPICE PONG</button>
            </div>
        </div>
    );
}