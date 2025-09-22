import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import arrow from '../elements/arrow.png'

export default function GameModeSelector() {
    const location = useLocation();
    const { gameMode, title, hasCompetitors } = location.state || {}; // S'assure que l'état existe

    const [modifiers, setModifiers] = useState([]);
    const [checkedBox, setCheckedBox] = useState(`${hasCompetitors ? "4" : ""}`);
    const navigate = useNavigate();

    const availableModifiers = ["so_long", "small_arena", "border", "elusive", "perfection"];

    const handleModifierChange = (modifier) => {
        setModifiers((prevModifiers) =>
            prevModifiers.includes(modifier)
                ? prevModifiers.filter((mod) => mod !== modifier)
                : [...prevModifiers, modifier]
        );
    };

    const handleCheckboxChange = (box) => {
        setCheckedBox(box); // Pour ne permettre qu'une seule case cochée
    };

    const startMatchmaking = () => {
        const state = { gameMode, modifiers, hasCompetitors, checkedBox };
        if (hasCompetitors) state.number = checkedBox; // Ajouter le nombre de compétiteurs si nécessaire
        navigate("/pong/matchmaking", { state });
    };

    return (
        <div>
            <div className="box">
                <h2 className="title-modes">{title}</h2>
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
            {hasCompetitors && (
                <div>
                    <h3>Choose the number of competitors:</h3>
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
            )}
            <div>
                <button
                    className="play-button-mode btn btn-outline-warning"
                    style={{ marginTop: "10px" }}
                    onClick={startMatchmaking}
                >
                    Play {gameMode ? gameMode.replace("_", " ") : "Game Mode"}
                </button>
            </div>
            <footer>
                <Link to="/pong">
                    <img className="arrow" src={arrow} alt="Go back" />
                </Link>
            </footer>
        </div>
    );
}
