import PlayButton from '../components/PlayButton.js';
import { useState } from 'react';
import arrow from '../elements/arrow.png';
import { Link } from 'react-router-dom';

export default function ClassicTournament() {
    const [modifiers, setModifiers] = useState([]);

    const availableModifiers = ["so_long", "small_arena", "border", "elusive", "perfection"];

    const [checkedBox, setCheckedBox] = useState("4"); // Par défaut, "4" est sélectionné

    const handleCheckboxChange = (box) => {
        setCheckedBox(box); // Force qu'une seule case soit cochée
    };

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
                <h2 className="title-modes">Solo Tournament</h2>
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
                <h3>Choisissez le nombre de compétiteurs :</h3>
                <label>
                    <input
                        type="radio"
                        name="competitors"
                        checked={checkedBox === "4"}
                        onChange={() => handleCheckboxChange("4")}
                    />
                    4
                </label>
                <label>
                    <input
                        type="radio"
                        name="competitors"
                        checked={checkedBox === "8"}
                        onChange={() => handleCheckboxChange("8")}
                    />
                    8
                </label>
            </div>
            <div>
                <Link to="/matchmaking">
                    <PlayButton gameMode="PONG_CLASSIC_TOURNAMENT" modifiers={modifiers} number={checkedBox} />
                </Link>
            </div>
            <footer>
                <Link to="/pong">
                    <img className="arrow" src={arrow} alt="Go back" />
                </Link>
            </footer>
        </div>
    );
}
