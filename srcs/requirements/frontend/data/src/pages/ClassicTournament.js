import PlayButton from '../components/PlayButton.js';
import { useState } from 'react';
import arrow from '../elements/arrow.png'
import vid from '../elements/gif-solo.gif'
import { Link } from 'react-router-dom';


export default function ClassicTournament() {
    const [modifiers, setModifiers] = useState([]);

    const availableModifiers = ["so_long", "small_arena", "border", "elusive", "perfection"];

    const [checkedBox, setCheckedBox] = useState(null);

    const handleCheckboxChange = (box) => {
        setCheckedBox(checkedBox === box ? null : box); // Décoche si on reclique sur la même box
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
                <h3>Choisissez le nombre de competiteurs :</h3>
                <label>
                    <input
                    type="checkbox"
                    checked={checkedBox === "4"}
                    onChange={() => handleCheckboxChange("4")}
                    />
                    4
                </label>
                <label>
                    <input
                    type="checkbox"
                    checked={checkedBox === "8"}
                    onChange={() => handleCheckboxChange("8")}
                    />
                    8
                </label>
            </div>
            <div>

                <Link to="/matchmaking"><PlayButton gameMode="PONG_CLASSIC_TOURNAMENT" modifiers={modifiers} number={checkedBox}/></Link>
            </div>
            <footer><Link to="/pong"><img className="arrow" src={arrow}/></Link></footer>
        </div>
    );
}