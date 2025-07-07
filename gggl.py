import pygame
import random
import sys
import json
from enum import Enum

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
ROAD_WIDTH = 300
CAR_WIDTH = 50
CAR_HEIGHT = 80
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 50
SPEED = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Obstacle types
class ObstacleType(Enum):
    NORMAL = 1
    FAST = 2
    SLOW = 3
    DOUBLE_POINTS = 4
    INVINCIBLE = 5

class PowerUpType(Enum):
    EXTRA_LIFE = 1
    SLOW_TIME = 2
    CLEAR_ROAD = 3

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Car Game")
clock = pygame.time.Clock()

# High score file
HIGH_SCORE_FILE = "highscore.json"

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            return json.load(f).get('high_score', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({'high_score': score}, f)

class PlayerCar:
    def __init__(self):
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = 5
        self.color = BLUE
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0
        self.slow_time = False
        self.slow_time_timer = 0
    
    def draw(self):
        # Draw car body (change color if invincible)
        car_color = CYAN if self.invincible else self.color
        pygame.draw.rect(screen, car_color, (self.x, self.y, self.width, self.height))
        
        # Draw car windows
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 10, self.width - 10, 15))
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 35, self.width - 10, 15))
        
        # Draw wheels
        pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + self.height - 10), 8)
        pygame.draw.circle(screen, BLACK, (self.x + self.width - 10, self.y + self.height - 10), 8)
        pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 10), 8)
        pygame.draw.circle(screen, BLACK, (self.x + self.width - 10, self.y + 10), 8)
    
    def move(self, direction):
        if direction == "left" and self.x > (SCREEN_WIDTH - ROAD_WIDTH) // 2:
            self.x -= self.speed
        if direction == "right" and self.x < (SCREEN_WIDTH + ROAD_WIDTH) // 2 - self.width:
            self.x += self.speed
    
    def update(self):
        # Update power-up timers
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        if self.slow_time:
            self.slow_time_timer -= 1
            if self.slow_time_timer <= 0:
                self.slow_time = False
    
    def lose_life(self):
        if not self.invincible:
            self.lives -= 1
            # Brief invincibility after losing a life
            self.invincible = True
            self.invincible_timer = 60  # 1 second at 60 FPS
            return self.lives <= 0
        return False
    
    def add_life(self):
        if self.lives < 5:  # Max 5 lives
            self.lives += 1

class Obstacle:
    def __init__(self):
        self.type = random.choice(list(ObstacleType))
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.x = random.randint((SCREEN_WIDTH - ROAD_WIDTH) // 2, 
                               (SCREEN_WIDTH + ROAD_WIDTH) // 2 - self.width)
        self.y = -self.height
        
        # Set properties based on type
        if self.type == ObstacleType.NORMAL:
            self.speed = 5
            self.color = RED
            self.points = 1
        elif self.type == ObstacleType.FAST:
            self.speed = 8
            self.color = PURPLE
            self.points = 2
        elif self.type == ObstacleType.SLOW:
            self.speed = 3
            self.color = GREEN
            self.points = 1
        elif self.type == ObstacleType.DOUBLE_POINTS:
            self.speed = 5
            self.color = YELLOW
            self.points = 2
        elif self.type == ObstacleType.INVINCIBLE:
            self.speed = 5
            self.color = CYAN
            self.points = 3
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Add visual indicators for special obstacles
        if self.type == ObstacleType.FAST:
            pygame.draw.line(screen, WHITE, (self.x + 5, self.y + 5), 
                            (self.x + self.width - 5, self.y + self.height - 5), 2)
        elif self.type == ObstacleType.SLOW:
            pygame.draw.line(screen, WHITE, (self.x + 5, self.y + self.height - 5), 
                            (self.x + self.width - 5, self.y + 5), 2)
        elif self.type == ObstacleType.DOUBLE_POINTS:
            pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 10, 10, 10))
            pygame.draw.rect(screen, WHITE, (self.x + self.width - 20, self.y + 10, 10, 10))
        elif self.type == ObstacleType.INVINCIBLE:
            pygame.draw.polygon(screen, WHITE, [
                (self.x + self.width // 2, self.y + 10),
                (self.x + 10, self.y + self.height - 10),
                (self.x + self.width - 10, self.y + self.height - 10)
            ])
    
    def move(self, slow_time=False):
        speed = self.speed * 0.5 if slow_time else self.speed
        self.y += speed
        return self.y > SCREEN_HEIGHT
    
    def check_collision(self, player):
        if (player.x < self.x + self.width and
            player.x + player.width > self.x and
            player.y < self.y + self.height and
            player.y + player.height > self.y):
            return True
        return False

class PowerUp:
    def __init__(self):
        self.type = random.choice(list(PowerUpType))
        self.width = 30
        self.height = 30
        self.x = random.randint((SCREEN_WIDTH - ROAD_WIDTH) // 2, 
                              (SCREEN_WIDTH + ROAD_WIDTH) // 2 - self.width)
        self.y = -self.height
        self.speed = 4
        
        if self.type == PowerUpType.EXTRA_LIFE:
            self.color = GREEN
            self.shape = "heart"
        elif self.type == PowerUpType.SLOW_TIME:
            self.color = BLUE
            self.shape = "clock"
        elif self.type == PowerUpType.CLEAR_ROAD:
            self.color = YELLOW
            self.shape = "star"
    
    def draw(self):
        if self.shape == "heart":
            # Draw heart shape
            pygame.draw.circle(screen, self.color, (self.x + 10, self.y + 10), 8)
            pygame.draw.circle(screen, self.color, (self.x + 20, self.y + 10), 8)
            pygame.draw.polygon(screen, self.color, [
                (self.x + 5, self.y + 12),
                (self.x + 25, self.y + 12),
                (self.x + 15, self.y + 25)
            ])
        elif self.shape == "clock":
            # Draw clock shape
            pygame.draw.circle(screen, self.color, (self.x + 15, self.y + 15), 12)
            pygame.draw.line(screen, BLACK, (self.x + 15, self.y + 15), 
                           (self.x + 15, self.y + 8), 2)
            pygame.draw.line(screen, BLACK, (self.x + 15, self.y + 15), 
                           (self.x + 22, self.y + 15), 2)
        elif self.shape == "star":
            # Draw star shape
            points = []
            for i in range(5):
                angle = 2 * 3.14159 * i / 5 - 3.14159 / 2
                outer_x = self.x + 15 + 12 *(angle)
                outer_y = self.y + 15 + 12 *(angle)
                inner_x = self.x + 15 + 6 *(angle + 3.14159 / 5)
                inner_y = self.y + 15 + 6 *(angle + 3.14159 / 5)
                points.extend([(outer_x, outer_y), (inner_x, inner_y)])
            pygame.draw.polygon(screen, self.color, points)
    
    def move(self):
        self.y += self.speed
        return self.y > SCREEN_HEIGHT
    
    def check_collision(self, player):
        if (player.x < self.x + self.width and
            player.x + player.width > self.x and
            player.y < self.y + self.height and
            player.y + player.height > self.y):
            return True
        return False

def draw_road():
    # Road background
    pygame.draw.rect(screen, GRAY, ((SCREEN_WIDTH - ROAD_WIDTH) // 2, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    
    # Road markings
    for i in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH // 2 - 5, i, 10, 20))

def draw_lives(surface, x, y, lives, max_lives=5):
    for i in range(max_lives):
        pos_x = x + i * 30
        if i < lives:
            # Draw filled heart
            pygame.draw.circle(surface, RED, (pos_x + 8, y + 8), 8)
            pygame.draw.circle(surface, RED, (pos_x + 22, y + 8), 8)
            pygame.draw.polygon(surface, RED, [
                (pos_x + 4, y + 10),
                (pos_x + 26, y + 10),
                (pos_x + 15, y + 25)
            ])
        else:
            # Draw empty heart outline
            pygame.draw.circle(surface, WHITE, (pos_x + 8, y + 8), 8, 1)
            pygame.draw.circle(surface, WHITE, (pos_x + 22, y + 8), 8, 1)
            pygame.draw.polygon(surface, WHITE, [
                (pos_x + 4, y + 10),
                (pos_x + 26, y + 10),
                (pos_x + 15, y + 25)
            ], 1)

def draw_pause_screen():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.SysFont(None, 72)
    pause_text = font.render("PAUSED", True, WHITE)
    continue_text = font.render("Press P to continue", True, WHITE)
    
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 - 50))
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                              SCREEN_HEIGHT // 2 + 50))

def game_loop():
    player = PlayerCar()
    obstacles = []
    powerups = []
    obstacle_frequency = 25
    powerup_frequency = 100
    score = 0
    high_score = load_high_score()
    game_over = False
    paused = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not game_over:
                    paused = not paused
                
                if game_over and event.key == pygame.K_r:
                    return  # Restart game
        
        if paused:
            draw_pause_screen()
            pygame.display.update()
            clock.tick(60)
            continue
        
        if not game_over:
            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")
            
            player.update()
            
            # Generate obstacles and powerups
            if random.randint(1, obstacle_frequency) == 1:
                obstacles.append(Obstacle())
            
            if random.randint(1, powerup_frequency) == 1:
                powerups.append(PowerUp())
            
            # Move obstacles and check collisions
            for obstacle in obstacles[:]:
                if obstacle.move(player.slow_time):
                    obstacles.remove(obstacle)
                    score += obstacle.points
                elif obstacle.check_collision(player):
                    if player.lose_life():
                        game_over = True
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                    obstacles.remove(obstacle)
            
            # Move powerups and check collisions
            for powerup in powerups[:]:
                if powerup.move():
                    powerups.remove(powerup)
                elif powerup.check_collision(player):
                    if powerup.type == PowerUpType.EXTRA_LIFE:
                        player.add_life()
                    elif powerup.type == PowerUpType.SLOW_TIME:
                        player.slow_time = True
                        player.slow_time_timer = 180  # 3 seconds at 60 FPS
                    elif powerup.type == PowerUpType.CLEAR_ROAD:
                        obstacles.clear()
                    powerups.remove(powerup)
            
            # Increase difficulty
            if score > 0 and score % 10 == 0:
                obstacle_frequency = max(10, obstacle_frequency - 1)
        
        # Drawing
        screen.fill(BLACK)
        draw_road()
        
        # Draw all game objects
        for obstacle in obstacles:
            obstacle.draw()
        
        for powerup in powerups:
            powerup.draw()
        
        player.draw()
        
        # Display HUD
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = font.render(f"High: {high_score}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))
        
        # Draw lives
        draw_lives(screen, SCREEN_WIDTH - 160, 10, player.lives)
        
        # Draw power-up indicators
        if player.slow_time:
            time_left = max(0, player.slow_time_timer // 60)
            time_text = font.render(f"Slow: {time_left}s", True, BLUE)
            screen.blit(time_text, (SCREEN_WIDTH - 150, 50))
        
        if player.invincible:
            inv_text = font.render("INVINCIBLE!", True, CYAN)
            screen.blit(inv_text, (SCREEN_WIDTH - 150, 90))
        
        # Game over message
        if game_over:
            font = pygame.font.SysFont(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to restart", True, WHITE)
            final_score_text = font.render(f"Score: {score}", True, WHITE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                       SCREEN_HEIGHT // 2 - 100))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 
                                         SCREEN_HEIGHT // 2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 + 60))
        
        pygame.display.update()
        clock.tick(60)

# Main game loop
while True:
    game_loop()