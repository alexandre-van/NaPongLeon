import { sendMove } from '../main.js';

const keyUp = 'z';
const keyDown = 's';

document.addEventListener('keydown', (event) => {
	switch(event.key) {
		case keyUp:
			sendMove(1);
			break;
		case keyDown:
			sendMove(2);
			break;
	}
});

document.addEventListener('keyup', (event) => {
	switch(event.key) {
		case keyUp:
			sendMove(3);
			break;
		case keyDown:
			sendMove(4);
			break;
	}
});
