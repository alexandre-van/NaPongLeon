import { sendPlayerMove } from './network.js';
import { getMyPlayerId } from './player.js';

export function initInput() {
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
}

function handleKeyDown(event) {
    const playerId = getMyPlayerId();
    if (!playerId) return;

    let key = event.key.toLowerCase();
    if (['w', 'a', 's', 'd', 'arrowup', 'arrowleft', 'arrowdown', 'arrowright'].includes(key)) {
        // console.log('in handleKeyDown, key', key);
        event.preventDefault();
        sendPlayerMove(playerId, key, true);
    }
}

function handleKeyUp(event) {
    const playerId = getMyPlayerId();
    if (!playerId) return;

    let key = event.key.toLowerCase();
    if (['w', 'a', 's', 'd', 'arrowup', 'arrowleft', 'arrowdown', 'arrowright'].includes(key)) {
        // console.log('in handleKeyUp, key', key);
        event.preventDefault();
        sendPlayerMove(playerId, key, false);
    }
}
