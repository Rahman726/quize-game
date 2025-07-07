import pygame
import random
import sys

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

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Car Game")
clock = pygame.time.Clock()

class PlayerCar:
    def __init__(self):
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = 5
        self.color = BLUE
    
    def draw(self):
        # Draw car body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
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

class Obstacle:
    def __init__(self):
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.x = random.randint((SCREEN_WIDTH - ROAD_WIDTH) // 2, 
                               (SCREEN_WIDTH + ROAD_WIDTH) // 2 - self.width)
        self.y = -self.height
        self.speed = random.randint(3, 7)
        self.color = RED
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
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

def game_loop():
    player = PlayerCar()
    obstacles = []
    obstacle_frequency = 25  # lower is more frequent
    score = 0
    game_over = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return  # Restart game
        
        if not game_over:
            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")
            
            # Generate obstacles
            if random.randint(1, obstacle_frequency) == 1:
                obstacles.append(Obstacle())
            
            # Move obstacles and check collisions
            for obstacle in obstacles[:]:
                if obstacle.move():  # If obstacle moved off screen
                    obstacles.remove(obstacle)
                    score += 1
                elif obstacle.check_collision(player):
                    game_over = True
            
            # Increase difficulty
            if score > 0 and score % 10 == 0:
                obstacle_frequency = max(10, obstacle_frequency - 1)
        
        # Drawing
        screen.fill(BLACK)
        draw_road()
        player.draw()
        for obstacle in obstacles:
            obstacle.draw()
        
        # Display score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Game over message
        if game_over:
            font = pygame.font.SysFont(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                        SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.update()
        clock.tick(60)

# Main game loop
while True:
    game_loop()