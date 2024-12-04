import uuid
import random
import asyncio
from .logger import setup_logger

logger = setup_logger()

FOOD_TYPES = {
    'common': {'value': 1, 'probability': 0.75, 'color': '#FFFF00'},
    'rare': {'value': 3, 'probability': 0.20, 'color': '#00FF00'},
    'epic': {'value': 10, 'probability': 0.05, 'color': '#FF00FF'}
}

POWER_UPS = {
    'speed_boost': {
        'duration': 10,
        'probability': 0.1,
        'color': '#FFD700',
        'effect': 'speed_multiplier',
        'value': 1.25
    },
    'slow_zone': {
        'duration': 10,
        'probability': 0.1,
        'color': '#800080',
        'effect': 'speed_multiplier',
        'value': 0.7
    },
    'shield': {
        'duration': 8,
        'probability': 0.05,
        'color': '#0000FF',
        'effect': 'invulnerable',
        'value': True
    },
    'point_multiplier': {
        'duration': 10,
        'probability': 0.08,
        'color': '#FFA500',
        'effect': 'score_multiplier',
        'value': 2
    }
}

class Game:
    def __init__(self, game_id):
        self.game_id = game_id
        self.players = {}
        self.food = []
        self.map_width = 35000
        self.map_height = 35000
        self.max_food = 2500
        self.player_inputs = {}
        self.player_movements = {}
        self.PLAYER_SPEED = 600
        self.status = "custom"
        self.game_loop_task = None
        self.initialize_food()
        self.power_ups = []
        self.power_up_spawn_timer = 0
        self.power_up_spawn_interval = 10  # secondes

    def initialize_food(self):
        """Initialise la nourriture sur la carte"""
        for _ in range(self.max_food):
            self.add_food()

    def get_random_food_type(self):
        """Détermine aléatoirement le type de nourriture"""
        rand = random.random()
        cumulative_prob = 0
        for food_type, props in FOOD_TYPES.items():
            cumulative_prob += props['probability']
            if rand <= cumulative_prob:
                return food_type
        return 'common'

    def add_food(self, food_id=None):
        """Ajoute de la nourriture sur la carte"""
        if len(self.food) >= self.max_food:
            return None
        
        food_type = self.get_random_food_type()
        new_food = {
            'id': str(uuid.uuid4()) if not food_id else food_id,
            'x': random.randint(0, self.map_width),
            'y': random.randint(0, self.map_height),
            'type': food_type,
            'value': FOOD_TYPES[food_type]['value'],
            'color': FOOD_TYPES[food_type]['color']
        }
        self.food.append(new_food)
        return new_food

    def check_food_collision(self, player_id):
        """Vérifie les collisions entre un joueur et la nourriture"""
        player = self.players.get(player_id)
        if not player:
            return False
        
        changed_foods = []
        collision_occurred = False
        
        for food in self.food[:]:
            if self.distance(player, food) < player['size'] * 0.9:
                player['size'] += food['value'] * player['score_multiplier']
                player['score'] += food['value'] * player['score_multiplier']
                self.food.remove(food)
                new_food = self.add_food()
                if new_food:
                    changed_foods.append(new_food)
                collision_occurred = True

        return changed_foods if collision_occurred else None

    def distance(self, obj1, obj2):
        """Calcule la distance entre deux objets"""
        return ((obj1['x'] - obj2['x']) ** 2 + (obj1['y'] - obj2['y']) ** 2) ** 0.5

    def check_all_food_collisions(self):
        """Vérifie les collisions pour tous les joueurs"""
        food_changes = []
        for player_id in self.players:
            changes = self.check_food_collision(player_id)
            if changes:
                food_changes.extend(changes)
        return len(food_changes) > 0

    # def is_game_active(self):
    #     """Vérifie si la partie est active"""
    #     return self.status == "in_progress"

    def add_player(self, player_id, player_name):
        """Ajoute un joueur à la partie"""
        self.players[player_id] = {
            'id': player_id,
            'name': player_name,
            'x': random.randint(0, self.map_width),
            'y': random.randint(0, self.map_height),
            'size': 30,
            'score': 0,
            'color': f'#{random.randint(0, 0xFFFFFF):06x}',
            'speed_multiplier': 1,
            'invulnerable': False,
            'score_multiplier': 1
        }
        if len(self.players) > 4:
            self.status = "in_progress"
            
    def remove_player(self, player_id):
        """Retire un joueur de la partie"""
        if player_id in self.players:
            del self.players[player_id]
            if player_id in self.player_inputs:
                del self.player_inputs[player_id]
            if player_id in self.player_movements:
                del self.player_movements[player_id]
        if len(self.players) == 0:
            self.status = "finished"

    def get_food_state(self):
        """Retourne l'état complet de la partie"""
        return {
            'type': 'food_update',
            'game_id': self.game_id,
            'players': self.players,
            'food': self.food,
        }

    def get_players_state(self):
        """Retourne l'état des joueurs"""
        return {
            'type': 'players_update',
            'game_id': self.game_id,
            'players': self.players,
        }

    def update_state(self, food_changes=None):
        """Retourne l'état mis à jour soit des joueurs soit de la nourriture"""
        game_state = self.get_food_state() if food_changes == True else self.get_players_state()
        return game_state

    def handle_player_input(self, player_id, key, is_key_down):
        """Gère les entrées des joueurs"""
        if player_id not in self.player_inputs:
            self.player_inputs[player_id] = {
                'w': False, 'a': False, 's': False, 'd': False,
                'arrowup': False, 'arrowleft': False, 'arrowdown': False, 'arrowright': False
            }
        self.player_inputs[player_id][key.lower()] = is_key_down

    async def start_game_loop(self, broadcast_callback):
        """Démarre la boucle de jeu"""
        self.game_loop_task = asyncio.create_task(self._game_loop(broadcast_callback))
        
    async def _game_loop(self, broadcast_callback):
        """Boucle de jeu principale"""
        try:
            last_update = asyncio.get_event_loop().time()
            await broadcast_callback(self.game_id, self.update_state(food_changes=True))
            while self.status != "finished":
                current_time = asyncio.get_event_loop().time()
                delta_time = current_time - last_update
                last_update = current_time

                positions_updated = self.update_positions(delta_time)
                if positions_updated:
                    await broadcast_callback(self.game_id, self.update_state(food_changes=False)) # Send only updated positions to all players

                player_food_changes = self.check_all_food_collisions()
                if player_food_changes:
                    await broadcast_callback(self.game_id, self.update_state(food_changes=True)) # Send food changes to all players
                # Vérifier les collisions avec les power-ups
                for player_id in self.players:
                    collected_power_up = self.check_power_up_collision(player_id)
                    if collected_power_up:
                        await broadcast_callback(self.game_id, {
                            'type': 'power_up_collected',
                            'game_id': self.game_id,
                            'players': self.players,
                            'player_id': player_id,
                            'power_up': collected_power_up,
                            'power_ups': self.power_ups
                        })
                # Gestion des power-ups
                self.power_up_spawn_timer += delta_time
                if self.power_up_spawn_timer >= self.power_up_spawn_interval:
                    self.power_up_spawn_timer = 0
                    new_power_up = self.spawn_power_up()
                    if new_power_up:
                        await broadcast_callback(self.game_id, {
                            'type': 'power_up_spawned',
                            'game_id': self.game_id,
                            'players': self.players,
                            'power_up': new_power_up,
                            'power_ups': self.power_ups
                        })
                await asyncio.sleep(1/60)

            if self.status == "finished":
                """TODO: Send final state to all players"""
        except Exception as e:
            logger.error(f"Error in game loop for game {self.game_id}: {e}")

    def update_positions(self, delta_time):
        """Met à jour les positions des joueurs"""
        positions_updated = False
        for player_id, inputs in self.player_inputs.items():
            if player_id not in self.players:
                continue

            dx = dy = 0
            if inputs['w'] or inputs['arrowup']: dy += 1
            if inputs['s'] or inputs['arrowdown']: dy -= 1
            if inputs['a'] or inputs['arrowleft']: dx -= 1
            if inputs['d'] or inputs['arrowright']: dx += 1

            if dx != 0 or dy != 0:
                player = self.players[player_id]
                base_speed = self.PLAYER_SPEED * player['speed_multiplier']
                if player['score'] <= 200:
                    speed_factor = max(0.9, 1 - (player['score'] / 2300))
                    speed = base_speed * speed_factor
                elif player['score'] <= 400:
                    speed_factor = max(0.8, 1 - (player['score'] / 2300))
                    speed = base_speed * speed_factor
                elif player['score'] <= 800:
                    speed_factor = max(0.6, 1 - (player['score'] / 2300))
                    speed = base_speed * speed_factor
                elif player['score'] <= 1000:
                    speed = base_speed * 0.6
                else:
                    speed = base_speed * 0.5
                
                new_x = player['x'] + dx * speed * delta_time
                new_y = player['y'] + dy * speed * delta_time
                
                new_x = max(0, min(new_x, self.map_width))
                new_y = max(0, min(new_y, self.map_height))
                
                if abs(new_x - player['x']) > 0.01 or abs(new_y - player['y']) > 0.01:
                    player['x'] = new_x
                    player['y'] = new_y
                    positions_updated = True
                player['current_speed'] = round(speed)
        return positions_updated

    def spawn_power_up(self):
        power_up_type = random.choice(list(POWER_UPS.keys()))
        power_up = {
            'id': str(uuid.uuid4()),
            'type': power_up_type,
            'x': random.randint(0, self.map_width),
            'y': random.randint(0, self.map_height),
            'properties': POWER_UPS[power_up_type]
        }
        self.power_ups.append(power_up)
        return power_up

    def check_power_up_collision(self, player_id):
        player = self.players.get(player_id)
        if not player:
            return False
        
        for power_up in self.power_ups[:]:
            if self.distance(player, power_up) < player['size']:
                self.apply_power_up(player_id, power_up)
                collected_power_up = power_up  # Sauvegarder le power-up avant de le supprimer
                self.power_ups.remove(power_up)
                return collected_power_up  # Retourner le power-up collecté
        return False

    def apply_power_up(self, player_id, power_up):
        player = self.players[player_id]
        effect = power_up['properties']['effect']
        value = power_up['properties']['value']
        duration = power_up['properties']['duration']
        
        if effect == 'speed_multiplier':
            player['speed_multiplier'] = value
        elif effect == 'invulnerable':
            player['invulnerable'] = value
        elif effect == 'score_multiplier':
            player['score_multiplier'] = value
        
        # Planifier la fin de l'effet
        asyncio.create_task(self.remove_power_up_effect(player_id, effect, duration))

    async def remove_power_up_effect(self, player_id, effect, duration):
        await asyncio.sleep(duration)
        if player_id in self.players:
            player = self.players[player_id]
            if effect == 'speed_multiplier':
                player['speed_multiplier'] = 1
            elif effect == 'invulnerable':
                player['invulnerable'] = False
            elif effect == 'score_multiplier':
                player['score_multiplier'] = 1

    async def cleanup(self):
        """Nettoie les ressources de la partie"""
        logger.info(f"Cleaning up game {self.game_id}")
        
        if self.game_loop_task:
            self.game_loop_task.cancel()
            try:
                await self.game_loop_task
            except asyncio.CancelledError:
                logger.debug(f"Game loop for game {self.game_id} cancelled successfully")
                pass
            except Exception as e:
                logger.error(f"Error while cancelling game loop for game {self.game_id}: {e}")
        self.status = "finished"
        self.players.clear()
        self.food.clear()
        self.player_inputs.clear()
        self.player_movements.clear()
        logger.info(f"Game {self.game_id} cleaned up successfully")
