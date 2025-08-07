import pygame
import random
import time
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5
AI_SPEED = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

class Player:
    def __init__(self, x, y, color, is_ai=False):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = color
        self.speed = AI_SPEED if is_ai else PLAYER_SPEED
        self.score = 0
        self.is_ai = is_ai
        self.target = None
    
    def move(self, dx, dy, team_members):
        if self.is_ai:
            self.ai_move(team_members)
        else:
            self.x += dx * self.speed
            self.y += dy * self.speed
            # Boundary checking
            self.x = max(self.radius, min(self.x, SCREEN_WIDTH - self.radius))
            self.y = max(self.radius, min(self.y, SCREEN_HEIGHT - self.radius))
    
    def ai_move(self, team_members):
        if not team_members:
            return
            
        # Find nearest team member
        if not self.target or not self.target.active:
            closest = None
            min_dist = float('inf')
            for member in team_members:
                if member.active:
                    dist = math.hypot(self.x - member.x, self.y - member.y)
                    if dist < min_dist:
                        min_dist = dist
                        closest = member
            self.target = closest
        
        if self.target and self.target.active:
            # Move toward target
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx = dx / dist * self.speed
                dy = dy / dist * self.speed
                self.x += dx
                self.y += dy
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw score above player
        font = pygame.font.SysFont(None, 24)
        score_text = font.render(str(self.score), True, WHITE)
        screen.blit(score_text, (self.x - 10, self.y - 40))

class TeamMember:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.active = True
    
    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

class TeamGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Team Collection Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.level = 1
        self.max_levels = 3
        self.game_over = False
        self.level_complete = False
        self.font = pygame.font.SysFont(None, 36)
        
        # Create players
        self.player = Player(100, 100, BLUE)
        self.ai_player = Player(700, 500, RED, is_ai=True)
        
        self.reset_level()
    
    def reset_level(self):
        # Create team members
        self.team_members = []
        for _ in range(10):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.team_members.append(TeamMember(x, y))
        
        # Set timer based on level
        self.time_limit = 60 - (self.level * 10)  # Level 1: 50s, Level 2: 40s, Level 3: 30s
        self.start_time = time.time()
        self.level_complete = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_r and (self.game_over or self.level_complete):
                    self.__init__()  # Restart game
    
    def update(self):
        if self.game_over or self.level_complete:
            return
        
        # Player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[K_LEFT] or keys[K_a]:
            dx -= 1
        if keys[K_RIGHT] or keys[K_d]:
            dx += 1
        if keys[K_UP] or keys[K_w]:
            dy -= 1
        if keys[K_DOWN] or keys[K_s]:
            dy += 1
        
        self.player.move(dx, dy, self.team_members)
        self.ai_player.move(0, 0, self.team_members)  # AI moves automatically
        
        # Check collisions with team members
        for member in self.team_members:
            if member.active:
                # Check player collision
                player_dist = math.hypot(self.player.x - member.x, self.player.y - member.y)
                if player_dist < self.player.radius + member.radius:
                    member.active = False
                    self.player.score += 10
                
                # Check AI collision
                ai_dist = math.hypot(self.ai_player.x - member.x, self.ai_player.y - member.y)
                if ai_dist < self.ai_player.radius + member.radius:
                    member.active = False
                    self.ai_player.score += 10
        
        # Check if all team members are collected
        if all(not member.active for member in self.team_members):
            if self.level < self.max_levels:
                self.level += 1
                self.reset_level()
            else:
                self.level_complete = True
        
        # Check time limit
        elapsed = time.time() - self.start_time
        if elapsed > self.time_limit:
            self.game_over = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw team members
        for member in self.team_members:
            member.draw(self.screen)
        
        # Draw players
        self.player.draw(self.screen)
        self.ai_player.draw(self.screen)
        
        # Draw UI
        time_left = max(0, self.time_limit - (time.time() - self.start_time))
        time_text = self.font.render(f"Time: {int(time_left)}s", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}/{self.max_levels}", True, WHITE)
        
        self.screen.blit(time_text, (10, 10))
        self.screen.blit(level_text, (10, 50))
        
        # Game over or level complete message
        if self.game_over:
            result_text = self.font.render("GAME OVER! Press R to restart", True, RED)
            score_text = self.font.render(f"Final Score: {self.player.score} (AI: {self.ai_player.score})", True, WHITE)
            self.screen.blit(result_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20))
        elif self.level_complete:
            result_text = self.font.render("YOU WIN! Press R to play again", True, GREEN)
            score_text = self.font.render(f"Final Score: {self.player.score} (AI: {self.ai_player.score})", True, WHITE)
            self.screen.blit(result_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = TeamGame()
    game.run()
    pygame.quit()