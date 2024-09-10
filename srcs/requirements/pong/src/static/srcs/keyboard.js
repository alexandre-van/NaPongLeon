import { sendMove } from '../main.js';

<<<<<<< HEAD
let keyUp, keyDown = null;
let up, down, stop_up, stop_down = null;

function init_keyboard(key_data, input_data) {
	keyUp = key_data.up;
	keyDown = key_data.down;
	console.log(input_data);
	up = input_data.up;
	down = input_data.down;
	stop_up = input_data.stop_up;
	stop_down = input_data.stop_down;
}
=======
const keyUp = 'z';
const keyDown = 's';
>>>>>>> 701bd7645a59dfe00177594a5322371256e1259a

document.addEventListener('keydown', (event) => {
	switch(event.key) {
		case keyUp:
			sendMove(up);
			break;
		case keyDown:
			sendMove(down);
			break;
	}
});

document.addEventListener('keyup', (event) => {
	switch(event.key) {
		case keyUp:
			sendMove(stop_up);
			break;
		case keyDown:
			sendMove(stop_down);
			break;
	}
});

export { init_keyboard }