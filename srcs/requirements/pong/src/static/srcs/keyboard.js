import { setPad1Dir, setPad2Dir, getPad1Dir, getPad2Dir } from './pad.js';

const keyUp1 = 'z';
const keyDown1 = 's';
const keyUp2 = 'i';
const keyDown2 = 'k';

document.addEventListener('keydown', (event) => {
	switch(event.key) {
		case keyUp1:
			setPad1Dir(1);
			break;
		case keyDown1:
			setPad1Dir(-1);
			break;
		case keyUp2:
			setPad2Dir(1);
			break;
		case keyDown2:
			setPad2Dir(-1);
			break;
	}
});

document.addEventListener('keyup', (event) => {
	switch(event.key) {
		case keyUp1:
			if (getPad1Dir() === 1)
				setPad1Dir(0);
			break;
		case keyDown1:
			if (getPad1Dir() === -1)
				setPad1Dir(0);
			break;
		case keyUp2:
			if (getPad2Dir() === 1)
				setPad2Dir(0);
			break;
		case keyDown2:
			if (getPad2Dir() === -1)
				setPad2Dir(0);
			break;
	}
});
