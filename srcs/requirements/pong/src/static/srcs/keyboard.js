import { sendMove } from '../main.js';

const keyUp = 'w';
const keyDown = 's';

document.addEventListener('keydown', (event) => {
	switch(event.key) {
		case keyUp:
			sendMove("keydown_up");
			break;
		case keyDown:
			sendMove("keydown_down");
			break;
	}
});

document.addEventListener('keyup', (event) => {
	switch(event.key) {
		case keyUp:
			sendMove("keyup_up");
			break;
		case keyDown:
			sendMove("keyup_down");
			break;
	}
});
