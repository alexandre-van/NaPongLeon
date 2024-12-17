import { useState } from 'react';
import arrow from '../elements/arrow.png'
import vid from '../elements/gif-solo.gif'
import { Link } from 'react-router-dom';
import CreateGameButton from '../components/CreateGameButton.js';


export default function AIpong() {
    const [modifiers, setModifiers] = useState([]);

    const availableModifiers = ["so_long", "small_arena", "border", "elusive", "perfection"];

    // Gérer la sélection des modificateurs
    const handleModifierChange = (modifier) => {
        setModifiers((prevModifiers) =>
            prevModifiers.includes(modifier)
                ? prevModifiers.filter((mod) => mod !== modifier)
                : [...prevModifiers, modifier]
        );
    };

    return (
        <div>
            <div className="box">
                <h2 className="title-modes">AI PONG</h2>
                <img className="vid" src={vid}/>
                <ul>
                    {availableModifiers.map((modifier) => (
                        <li key={modifier}>
                            <div class="form-check form-switch">
                                <label class="form-check-label" for="flexSwitchCheckDefault">
                                    <input
                                        class="form-check-input" id="flexSwitchCheckDefault"
                                        type="checkbox"
                                        value={modifier}
                                        onChange={() => handleModifierChange(modifier)}
                                    />
                                    {modifier}
                                </label>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
            <div>

                <Link to="/ingame"><CreateGameButton gameMode="PONG_CLASSIC" modifiers={modifiers} /></Link>
            </div>
            <footer><Link to="/pong"><img className="arrow" src={arrow}/></Link></footer>
        </div>
    );
}