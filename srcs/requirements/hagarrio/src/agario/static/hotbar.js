export function createHotbar() {
    // Supprimer l'ancien hotbar s'il existe
    const existingHotbar = document.getElementById('hotbar');
    if (existingHotbar) {
        existingHotbar.remove();
    }

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
    // console.log('Updating hotbar with inventory:', inventory);
    const slots = document.querySelectorAll('.hotbar-slot');
    
    if (!slots.length) {
        console.error('No hotbar slots found');
        return;
    }

    slots.forEach((slot, index) => {
        const powerUp = inventory[index];
        const hotkey = slot.querySelector('.hotkey');
        
        // Nettoyer le slot sauf la touche
        Array.from(slot.children).forEach(child => {
            if (child !== hotkey) {
                child.remove();
            }
        });
        
        // Ajouter l'icône uniquement si le powerUp existe
        if (powerUp !== null) {
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
        'slow_zone': '🐢',
        'shield': '🛡️',
        'point_multiplier': '✨'
    };
    return icons[type] || '🎮';
}