import { useState } from 'react';
import arrow from '../elements/arrow.png'
import vid from '../elements/gif-solo.gif'
import { Link } from 'react-router-dom';
import { useNavigate } from "react-router-dom";

export default function SoloMode() {
    const [modifiers, setModifiers] = useState([]);
    const navigate = useNavigate();

    const availableModifiers = ["so_long", "small_arena", "border", "elusive", "perfection"];

    const handleModifierChange = (modifier) => {
        setModifiers((prevModifiers) =>
            prevModifiers.includes(modifier)
                ? prevModifiers.filter((mod) => mod !== modifier)
                : [...prevModifiers, modifier]
        );
    };

    const startMatchmaking = () => {
        navigate("/matchmaking", { state: { gameMode: "PONG_CLASSIC", modifiers } });
    };

    return (
        <div>
            <div className="box">
                <h2 className="title-modes">1 VS 1</h2>
                <img className="vid" src={vid} />
                <ul>
                    {availableModifiers.map((modifier) => (
                        <li key={modifier}>
                            <div className="form-check form-switch">
                                <label className="form-check-label" htmlFor={`switch-${modifier}`}>
                                    <input
                                        className="form-check-input"
                                        id={`switch-${modifier}`}
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
                <button className="play-button-mode btn btn-outline-warning" 
                    style={{ marginTop: "10px" }}
                    onClick={startMatchmaking}>Play PONG CLASSIC</button>
            </div>
            <footer><Link to="/pong"><img className="arrow" src={arrow} /></Link></footer>
        </div>
    );
}
