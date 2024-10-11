document.addEventListener('DOMContentLoaded', (event) => {
    if (typeof THREE === 'undefined') {
        console.error('Three.js is not loaded');
        return;
    }
    
    console.log('Three.js is available:', THREE.REVISION);

    const scene = new THREE.Scene();
    const mapWidth = 2000;
    const mapHeight = 2000;
    const camera = new THREE.OrthographicCamera(0, mapWidth, mapHeight, 0, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const socket = new WebSocket('ws://' + window.location.host + '/ws/game/');

    let players = {};
    let food = [];
    let myPlayerId = null;
    let keys = { w: false, a: false, s: false, d: false };

    function getRandomColor() {
        const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    socket.onmessage = function(e) {
        const gameState = JSON.parse(e.data);
        updateGameState(gameState);
    };

    function updateGameState(gameState) {
        players = gameState.players;
        food = gameState.food;
        if (gameState.yourPlayerId && !myPlayerId) {
            myPlayerId = gameState.yourPlayerId;
            if (players[myPlayerId]) {
                camera.position.set(players[myPlayerId].x, players[myPlayerId].y, 100);
                camera.lookAt(players[myPlayerId].x, players[myPlayerId].y, 0);
            }
        }
        updateSceneObjects();
    }

    function updateSceneObjects() {
        while(scene.children.length > 0){ 
            scene.remove(scene.children[0]); 
        }

        Object.values(players).forEach(p => {
            // Créer le sprite du joueur (boule)
            const playerCanvas = document.createElement('canvas');
            const playerContext = playerCanvas.getContext('2d');
            const size = p.size * 2;
            playerCanvas.width = size;
            playerCanvas.height = size;

            playerContext.beginPath();
            playerContext.arc(size/2, size/2, size/2, 0, 2 * Math.PI);
            playerContext.fillStyle = p.color;
            playerContext.fill();

            const playerTexture = new THREE.CanvasTexture(playerCanvas);
            playerTexture.minFilter = THREE.LinearFilter;
            playerTexture.magFilter = THREE.LinearFilter;
            const playerMaterial = new THREE.SpriteMaterial({ map: playerTexture });
            const playerSprite = new THREE.Sprite(playerMaterial);
            playerSprite.scale.set(p.size * 2, p.size * 2, 1);
            playerSprite.position.set(p.x, p.y, 0);
            scene.add(playerSprite);

            // Créer le sprite du texte
            const textCanvas = document.createElement('canvas');
            const textContext = textCanvas.getContext('2d');
            const fixedTextSize = 70;
            textCanvas.width = fixedTextSize * 8;
            textCanvas.height = fixedTextSize * 2;

            textContext.font = `bold ${fixedTextSize}px Arial`;
            textContext.fillStyle = 'white';
            textContext.strokeStyle = 'black';
            textContext.lineWidth = fixedTextSize / 25; // Augmentation de l'épaisseur du contour
            textContext.textAlign = 'center';
            textContext.textBaseline = 'middle';

            const maxWidth = 18;
            let text = p.name;
            if (textContext.measureText(text).width > maxWidth) {
                text = text.substring(0, maxWidth - 3) + '...';
            }

            textContext.strokeText(text, textCanvas.width / 2, textCanvas.height / 2);
            textContext.fillText(text, textCanvas.width / 2, textCanvas.height / 2);

            const textTexture = new THREE.CanvasTexture(textCanvas);
            textTexture.minFilter = THREE.LinearFilter;
            textTexture.magFilter = THREE.LinearFilter;
            const textMaterial = new THREE.SpriteMaterial({ map: textTexture });
            const textSprite = new THREE.Sprite(textMaterial);
            textSprite.scale.set(120, 30, 1);
            textSprite.position.set(p.x, p.y, 0.1);
            scene.add(textSprite);
        });

        // Ajout du rendu de la nourriture
        food.forEach(f => {
            const foodCanvas = document.createElement('canvas');
            const foodContext = foodCanvas.getContext('2d');
            const foodSize = 10;
            foodCanvas.width = foodSize;
            foodCanvas.height = foodSize;

            foodContext.beginPath();
            foodContext.arc(foodSize/2, foodSize/2, foodSize/2, 0, 2 * Math.PI);
            foodContext.fillStyle = getRandomColor(); // Utilisation de la fonction pour obtenir une couleur aléatoire
            foodContext.fill();

            const foodTexture = new THREE.CanvasTexture(foodCanvas);
            foodTexture.minFilter = THREE.LinearFilter;
            foodTexture.magFilter = THREE.LinearFilter;
            const foodMaterial = new THREE.SpriteMaterial({ map: foodTexture });
            const foodSprite = new THREE.Sprite(foodMaterial);
            foodSprite.scale.set(foodSize, foodSize, 1);
            foodSprite.position.set(f.x, f.y, 0);
            scene.add(foodSprite);
        });
    }

    function updateGame() {
        if (myPlayerId && players[myPlayerId]) {
            let dx = 0, dy = 0;
            const speed = Math.max(1, 10 - players[myPlayerId].size / 10); // Vitesse diminue avec la taille
            if (keys.w) dy += speed;
            if (keys.s) dy -= speed;
            if (keys.a) dx -= speed;
            if (keys.d) dx += speed;

            if (dx !== 0 || dy !== 0) {
                const newX = Math.max(0, Math.min(mapWidth, players[myPlayerId].x + dx));
                const newY = Math.max(0, Math.min(mapHeight, players[myPlayerId].y + dy));

                socket.send(JSON.stringify({
                    'type': 'move',
                    'x': newX,
                    'y': newY
                }));

                // Mise à jour de la position de la caméra
                camera.position.set(newX, newY, 100);
                camera.lookAt(newX, newY, 0);
            }
        }
    }

    function animate() {
        requestAnimationFrame(animate);
        updateGame();
        renderer.render(scene, camera);
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'w' || event.key === 'W') keys.w = true;
        if (event.key === 'a' || event.key === 'A') keys.a = true;
        if (event.key === 's' || event.key === 'S') keys.s = true;
        if (event.key === 'd' || event.key === 'D') keys.d = true;
    });

    document.addEventListener('keyup', (event) => {
        if (event.key === 'w' || event.key === 'W') keys.w = false;
        if (event.key === 'a' || event.key === 'A') keys.a = false;
        if (event.key === 's' || event.key === 'S') keys.s = false;
        if (event.key === 'd' || event.key === 'D') keys.d = false;
    });

    animate();

    window.addEventListener('resize', () => {
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.right = mapWidth;
        camera.top = mapHeight;
        camera.updateProjectionMatrix();
    });
});