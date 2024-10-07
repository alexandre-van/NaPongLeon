import time

class PongAI:
    def __init__(self, paddle_height, court_height):
        self.paddle_height = paddle_height
        self.court_height = court_height
        self.paddle_y = court_height // 2  # Position initiale au milieu
        self.last_update = time.time()

    def update(self, ball_x, ball_y, ball_dx, ball_dy):
        current_time = time.time()
        if current_time - self.last_update >= 1:  # Mise à jour une fois par seconde
            self.last_update = current_time
            
            # Calculer où la balle va atterrir
            if ball_dy != 0:
                time_to_reach = (self.court_height - ball_y) / ball_dy
                predicted_y = ball_y + ball_dy * time_to_reach
                
                # Ajuster la position de la raquette
                target_y = predicted_y - self.paddle_height / 2
                if target_y < 0:
                    target_y = 0
                elif target_y > self.court_height - self.paddle_height:
                    target_y = self.court_height - self.paddle_height
                
                # Déplacer la raquette
                if self.paddle_y < target_y:
                    self.paddle_y += min(10, target_y - self.paddle_y)  # Vitesse limitée
                elif self.paddle_y > target_y:
                    self.paddle_y -= min(10, self.paddle_y - target_y)  # Vitesse limitée

    def get_move(self):
        # Simuler une entrée clavier
        if self.paddle_y < self.court_height / 2:
            return "DOWN"
        elif self.paddle_y > self.court_height / 2:
            return "UP"
        else:
            return None