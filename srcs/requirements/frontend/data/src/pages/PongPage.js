import PlayButton from '../components/PlayButton.js';
import { useState } from 'react';

export default function PongPage() {
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
        <div style={{ textAlign: "center" }}>
            <h2>Choose Modifiers:</h2>
            <ul style={{ listStyleType: "none", padding: 0 }}>
                {availableModifiers.map((modifier) => (
                    <li key={modifier}>
                        <label>
                            <input
                                type="checkbox"
                                value={modifier}
                                onChange={() => handleModifierChange(modifier)}
                            />
                            {modifier}
                        </label>
                    </li>
                ))}
            </ul>

            <h2>Join a matchmaking queue</h2>
            <PlayButton gameMode="PONG_CLASSIC" modifiers={modifiers} />
            <PlayButton gameMode="PONG_DUO" modifiers={modifiers} />
            <h2>TOURNAMENT</h2>
            <h2>Join a matchmaking queue</h2>
            <PlayButton gameMode="PONG_CLASSIC_TOURNAMENT" modifiers={modifiers} />
            <PlayButton gameMode="PONG_DUO_TOURNAMENT" modifiers={modifiers} />
        </div>
    );
}