import { init_keyboard } from './keyboard.js';
import { ball_init } from './ball.js';
import { padels_init } from './pad.js';
import { createBorders, createDashedLine } from './border.js';
import { createPlateau } from './plateau.js';
import { createSunlight } from './lights.js';

function init(data){
    init_keyboard(data.key, data.input);
    ball_init(data.ball);
    padels_init(data.padel);
    createBorders(data.arena);
    createDashedLine(data.arena);
    createPlateau(data.arena);
    createSunlight();
}

export { init }