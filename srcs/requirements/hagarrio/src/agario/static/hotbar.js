export function createHotbar() {
    const hotbarDiv = document.createElement('div');
    hotbarDiv.id = 'hotbar';
    
    for (let i = 0; i < 3; i++) {
        const slot = document.createElement('div');
        slot.className = 'hotbar-slot';
        slot.dataset.slot = i;
        
        const hotkey = document.createElement('span');
        hotkey.className = 'hotkey';
        hotkey.textContent = i + 1;
        
        slot.appendChild(hotkey);
        hotbarDiv.appendChild(slot);
    }
    document.body.appendChild(hotbarDiv);
}

export function updateHotbar(inventory = []) {
    const slots = document.querySelectorAll('.hotbar-slot');
    slots.forEach((slot, index) => {
        const powerUp = inventory[index];
        const hotkey = slot.querySelector('.hotkey');
        
        // Nettoyer le slot sauf la touche
        Array.from(slot.children).forEach(child => {
            if (child !== hotkey) child.remove();
        });
        
        if (powerUp) {
            const icon = document.createElement('div');
            icon.className = 'power-up-icon';
            icon.innerHTML = getPowerUpIcon(powerUp.type);
            icon.style.color = powerUp.properties.color;
            slot.appendChild(icon);
        }
    });
}

function getPowerUpIcon(type) {
    const icons = {
        'speed_boost': '🚀',
        'slow_zone': '🐌',
        'shield': '🛡️',
        'point_multiplier': '✨'
    };
    return icons[type] || '🎮';
}