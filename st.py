import pygame
import random
import sys
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Screen setup
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Epic Team Fighter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)

# Fonts
font_small = pygame.font.SysFont('Arial', 24)
font_medium = pygame.font.SysFont('Arial', 36)
font_large = pygame.font.SysFont('Arial', 72)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Load sounds
try:
    punch_sound = mixer.Sound('punch.wav')  # Create this file or remove
    heal_sound = mixer.Sound('heal.wav')    # Create this file or remove
    victory_sound = mixer.Sound('victory.wav')  # Create this file or remove
    game_over_sound = mixer.Sound('game_over.wav')  # Create this file or remove
    has_sound = True
except:
    has_sound = False
    print("Sound files not found. Continuing without sound.")

class Character:
    def __init__(self, x, y, name, max_health, attack_power, speed, is_player=False, special_ability=None):
        self.x = x
        self.y = y
        self.name = name
        self.max_health = max_health
        self.current_health = max_health
        self.attack_power = attack_power
        self.speed = speed
        self.is_player = is_player
        self.width = 60
        self.height = 100
        self.attacking = False
        self.attack_cooldown = 0
        self.attack_range = 80
        self.direction = 1  # 1 for right, -1 for left
        self.first_aid_kits = 3 if is_player else 0
        self.special_ability = special_ability
        self.special_cooldown = 0
        self.animation_frame = 0
        self.hit_flash = 0
        
        # Character appearance
        self.color = BLUE if is_player else RED
        if "Boss" in name:
            self.color = PURPLE
            self.width = 80
            self.height = 120
    
    def draw(self, screen):
        # Draw character body
        if self.hit_flash > 0:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
            self.hit_flash -= 1
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw health bar
        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y - 25, self.width, 10))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 25, self.width * health_ratio, 10))
        
        # Draw name
        name_text = font_small.render(self.name, True, BLACK)
        screen.blit(name_text, (self.x, self.y - 50))
        
        # Draw attack indicator if attacking
        if self.attacking:
            attack_x = self.x + self.width if self.direction == 1 else self.x - self.attack_range
            pygame.draw.rect(screen, ORANGE, (attack_x, self.y, self.attack_range, self.height))
        
        # Draw special ability indicator
        if self.is_player and self.special_ability:
            ability_text = font_small.render(f"Special: {self.special_ability} ({'Ready' if self.special_cooldown == 0 else str(self.special_cooldown//FPS)})", True, BLACK)
            screen.blit(ability_text, (self.x, self.y + self.height + 5))
    
    def move(self, dx):
        self.x += dx * self.speed
        if dx > 0:
            self.direction = 1
        elif dx < 0:
            self.direction = -1
        
        # Boundary checking
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
    
    def attack(self):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_cooldown = 30  # Cooldown in frames
            if has_sound:
                punch_sound.play()
            return True
        return False
    
    def special_attack(self):
        if self.special_cooldown == 0 and self.special_ability:
            if self.special_ability == "Heal Team":
                # Heal all team members by 20%
                for member in self.team.members:
                    heal_amount = member.max_health * 0.2
                    member.current_health = min(member.max_health, member.current_health + heal_amount)
                if has_sound:
                    heal_sound.play()
            elif self.special_ability == "Power Strike":
                # Deal double damage on next attack
                self.attack_power *= 2
                self.attacking = True
                self.attack_cooldown = 30
                if has_sound:
                    punch_sound.play()
            elif self.special_ability == "Quick Attack":
                # Attack three times quickly
                self.attack_cooldown = 10
                self.attacking = True
                if has_sound:
                    punch_sound.play()
            
            self.special_cooldown = 10 * FPS  # 10 second cooldown
            return True
        return False
    
    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        else:
            self.attacking = False
            if self.special_ability == "Power Strike":
                self.attack_power = self.max_health // 7  # Reset to base attack power
        
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
        
        self.animation_frame = (self.animation_frame + 1) % 60
    
    def take_damage(self, damage):
        self.current_health -= damage
        self.hit_flash = 5  # Flash white when hit
        if self.current_health < 0:
            self.current_health = 0
    
    def use_first_aid(self):
        if self.first_aid_kits > 0:
            heal_amount = self.max_health * 0.3  # Heal 30% of max health
            self.current_health = min(self.max_health, self.current_health + heal_amount)
            self.first_aid_kits -= 1
            if has_sound:
                heal_sound.play()
            return True
        return False
    
    def is_colliding_with(self, other):
        if not self.attacking:
            return False
            
        if self.direction == 1:  # Facing right
            attack_rect = pygame.Rect(self.x + self.width, self.y, self.attack_range, self.height)
        else:  # Facing left
            attack_rect = pygame.Rect(self.x - self.attack_range, self.y, self.attack_range, self.height)
            
        other_rect = pygame.Rect(other.x, other.y, other.width, other.height)
        return attack_rect.colliderect(other_rect)

class Team:
    def __init__(self, name, is_player=False):
        self.name = name
        self.members = []
        self.is_player = is_player
        self.current_member_index = 0
        self.score = 0
        
    def add_member(self, character):
        character.team = self
        self.members.append(character)
    
    def get_current_member(self):
        if len(self.members) > 0:
            return self.members[self.current_member_index]
        return None
    
    def switch_member(self):
        if len(self.members) > 1:
            self.current_member_index = (self.current_member_index + 1) % len(self.members)
            return True
        return False
    
    def is_team_defeated(self):
        return all(member.current_health <= 0 for member in self.members)
    
    def draw(self, screen):
        # Draw team status panel
        panel_color = (200, 230, 255) if self.is_player else (255, 200, 200)
        pygame.draw.rect(screen, panel_color, (10 if self.is_player else SCREEN_WIDTH - 210, 10, 200, 200))
        
        # Draw team name
        team_text = font_medium.render(f"{self.name}", True, BLACK)
        screen.blit(team_text, (20 if self.is_player else SCREEN_WIDTH - 190, 20))
        
        # Draw team members status
        for i, member in enumerate(self.members):
            status = f"{member.name}: {member.current_health}/{member.max_health}"
            if i == self.current_member_index:
                status = "▶ " + status
            status_color = BLACK if member.current_health > 0 else RED
            status_text = font_small.render(status, True, status_color)
            screen.blit(status_text, (20 if self.is_player else SCREEN_WIDTH - 190, 60 + i * 30))
            
            # Draw first aid kits for player team
            if self.is_player and member.current_health > 0:
                aid_text = font_small.render(f"First Aid: {member.first_aid_kits}", True, GREEN)
                screen.blit(aid_text, (20, 60 + len(self.members) * 30 + i * 25))

class GameLevel:
    def __init__(self, level_num):
        self.level_num = level_num
        self.enemy_team = None
        self.is_boss_level = level_num % 3 == 0  # Every 3rd level is a boss level
        self.level_time = (180 - level_num * 5) * FPS  # Less time at higher levels (minimum 60 seconds)
        self.time_left = self.level_time
        self.completed = False
        self.background = random.choice([BLACK, (50, 50, 70), (70, 50, 50)])
        
    def create_enemy_team(self):
        team_name = f"Enemy Team {self.level_num}"
        self.enemy_team = Team(team_name)
        
        if self.is_boss_level:
            # Create boss character
            boss = Character(
                SCREEN_WIDTH - 150, 
                SCREEN_HEIGHT - 180, 
                f"Boss {self.level_num//3}", 
                400 + self.level_num * 60, 
                25 + self.level_num * 6, 
                2 + self.level_num // 5
            )
            boss.color = PURPLE
            self.enemy_team.add_member(boss)
        else:
            # Create regular enemies
            num_enemies = min(2 + self.level_num // 2, 5)  # Max 5 enemies
            for i in range(num_enemies):
                enemy_type = random.choice(["Grunt", "Fighter", "Assassin"])
                if enemy_type == "Grunt":
                    health = 120 + self.level_num * 25
                    attack = 12 + self.level_num * 2
                    speed = 3
                elif enemy_type == "Fighter":
                    health = 150 + self.level_num * 30
                    attack = 15 + self.level_num * 3
                    speed = 2
                else:  # Assassin
                    health = 90 + self.level_num * 15
                    attack = 18 + self.level_num * 4
                    speed = 5
                
                enemy = Character(
                    SCREEN_WIDTH - 150 - i * 70, 
                    SCREEN_HEIGHT - 180, 
                    f"{enemy_type} {i+1}", 
                    health, 
                    attack, 
                    speed
                )
                self.enemy_team.add_member(enemy)
    
    def update(self):
        self.time_left -= 1
        if self.time_left <= 0:
            return "time_up"
        return None
    
    def draw_timer(self, screen):
        # Draw timer panel
        pygame.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH // 2 - 100, 10, 200, 80))
        
        minutes = self.time_left // (60 * FPS)
        seconds = (self.time_left % (60 * FPS)) // FPS
        timer_text = font_medium.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - 50, 20))
        
        level_text = font_medium.render(f"Level: {self.level_num}{' (BOSS)' if self.is_boss_level else ''}", True, PURPLE if self.is_boss_level else BLACK)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 60))

class EnemyAI:
    def __init__(self, enemy_team, player_team):
        self.enemy_team = enemy_team
        self.player_team = player_team
        self.decision_cooldown = 0
        
    def update(self):
        if self.decision_cooldown > 0:
            self.decision_cooldown -= 1
            return
            
        current_enemy = self.enemy_team.get_current_member()
        if not current_enemy or current_enemy.current_health <= 0:
            self.enemy_team.switch_member()
            current_enemy = self.enemy_team.get_current_member()
            if not current_enemy:
                return
                
        player = self.player_team.get_current_member()
        if not player or player.current_health <= 0:
            if not self.player_team.switch_member():
                return
            player = self.player_team.get_current_member()
            if not player:
                return
                
        # Calculate distance to player
        distance = abs(current_enemy.x - player.x)
        
        # More sophisticated AI for bosses
        if "Boss" in current_enemy.name:
            # Boss AI - more aggressive and strategic
            if distance < current_enemy.attack_range + player.width:
                if random.random() < 0.8:  # 80% chance to attack
                    current_enemy.attack()
                elif random.random() < 0.7 and len(self.enemy_team.members) > 1:  # 70% chance to switch if multiple members
                    self.enemy_team.switch_member()
            else:
                # Move toward player but sometimes feint
                if player.x < current_enemy.x:
                    current_enemy.move(-1 if random.random() < 0.8 else 1)
                else:
                    current_enemy.move(1 if random.random() < 0.8 else -1)
        else:
            # Regular enemy AI
            if distance < current_enemy.attack_range + player.width:
                if random.random() < 0.6:  # 60% chance to attack
                    current_enemy.attack()
                elif random.random() < 0.3 and len(self.enemy_team.members) > 1:  # 30% chance to switch
                    self.enemy_team.switch_member()
                else:  # Move away sometimes
                    if player.x < current_enemy.x:
                        current_enemy.move(1)
                    else:
                        current_enemy.move(-1)
            else:
                # Move toward player
                if player.x < current_enemy.x:
                    current_enemy.move(-1)
                else:
                    current_enemy.move(1)
        
        self.decision_cooldown = random.randint(10, 30)

class FightingGame:
    def __init__(self):
        self.player_team = Team("Heroes", True)
        self.current_level = None
        self.game_state = "menu"  # menu, playing, level_complete, game_over, victory
        self.ai = None
        self.level_score = 0
        self.max_levels = 9  # 9 levels (3 boss fights)
        self.create_player_team()
    
    def create_player_team(self):
        # Create 3 team members with different attributes and special abilities
        warrior = Character(
            100, SCREEN_HEIGHT - 180, 
            "Warrior", 200, 25, 4, 
            True, "Power Strike"
        )
        mage = Character(
            100, SCREEN_HEIGHT - 180, 
            "Mage", 150, 20, 3, 
            True, "Heal Team"
        )
        rogue = Character(
            100, SCREEN_HEIGHT - 180, 
            "Rogue", 170, 18, 6, 
            True, "Quick Attack"
        )
        
        self.player_team.add_member(warrior)
        self.player_team.add_member(mage)
        self.player_team.add_member(rogue)
    
    def start_level(self, level_num):
        self.current_level = GameLevel(level_num)
        self.current_level.create_enemy_team()
        self.ai = EnemyAI(self.current_level.enemy_team, self.player_team)
        self.game_state = "playing"
        self.level_score = 0
        
        # Reset player team positions and partially revive defeated members
        for member in self.player_team.members:
            member.x = 100
            member.y = SCREEN_HEIGHT - 180
            if member.current_health <= 0:
                member.current_health = member.max_health * 0.4  # Revive with 40% health
            
            # Reset special ability cooldowns
            member.special_cooldown = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_RETURN:
                        self.start_level(1)
                    elif event.key == pygame.K_i:
                        self.game_state = "instructions"
                        
                elif self.game_state == "instructions":
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        self.game_state = "menu"
                        
                elif self.game_state == "playing":
                    current_player = self.player_team.get_current_member()
                    if not current_player:
                        break
                        
                    if event.key == pygame.K_SPACE:
                        current_player.attack()
                    elif event.key == pygame.K_TAB:
                        self.player_team.switch_member()
                    elif event.key == pygame.K_h:
                        current_player.use_first_aid()
                    elif event.key == pygame.K_e:
                        current_player.special_attack()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"
                
                elif self.game_state in ("level_complete", "game_over", "victory"):
                    if event.key == pygame.K_RETURN:
                        if self.game_state == "level_complete" and self.current_level.level_num < self.max_levels:
                            self.start_level(self.current_level.level_num + 1)
                        else:
                            self.__init__()  # Reset game
        return True
    
    def update(self):
        if self.game_state != "playing":
            return
            
        # Update level timer
        time_result = self.current_level.update()
        if time_result == "time_up":
            self.game_state = "game_over"
            if has_sound:
                game_over_sound.play()
            return
            
        # Update player team
        current_player = self.player_team.get_current_member()
        if current_player:
            current_player.update()
            
            # Handle keyboard input for movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                current_player.move(-1)
            if keys[pygame.K_RIGHT]:
                current_player.move(1)
        
        # Update enemy team and AI
        if self.ai:
            self.ai.update()
            current_enemy = self.current_level.enemy_team.get_current_member()
            if current_enemy:
                current_enemy.update()
                
                # Check if enemy attack hits player
                if current_player and current_enemy.is_colliding_with(current_player):
                    current_player.take_damage(current_enemy.attack_power)
        
        # Check if player attack hits enemy
        if current_player and current_player.attacking:
            current_enemy = self.current_level.enemy_team.get_current_member()
            if current_enemy and current_player.is_colliding_with(current_enemy):
                current_enemy.take_damage(current_player.attack_power)
                self.level_score += current_player.attack_power
        
        # Check win/lose conditions
        if self.current_level.enemy_team.is_team_defeated():
            if self.current_level.level_num == self.max_levels:
                self.game_state = "victory"
                if has_sound:
                    victory_sound.play()
            else:
                self.game_state = "level_complete"
                if has_sound:
                    victory_sound.play()
            self.player_team.score += self.level_score
            self.current_level.completed = True
        elif self.player_team.is_team_defeated():
            self.game_state = "game_over"
            if has_sound:
                game_over_sound.play()
    
    def draw(self):
        # Draw background based on level
        if self.game_state == "playing":
            screen.fill(self.current_level.background)
            
            # Draw arena floor
            pygame.draw.rect(screen, (100, 100, 100), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        else:
            screen.fill(BLACK)
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "instructions":
            self.draw_instructions()
        elif self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "level_complete":
            self.draw_level_complete()
        elif self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "victory":
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_menu(self):
        # Title
        title = font_large.render("EPIC TEAM FIGHTER", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 150))
        
        # Menu options
        start_text = font_medium.render("Press ENTER to Start", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2))
        
        instructions_text = font_medium.render("Press I for Instructions", True, WHITE)
        screen.blit(instructions_text, (SCREEN_WIDTH//2 - instructions_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        # Draw team preview
        for i, member in enumerate(self.player_team.members):
            pygame.draw.rect(screen, member.color, (SCREEN_WIDTH//2 - 100 + i*70, SCREEN_HEIGHT//2 + 100, 50, 80))
            name_text = font_small.render(member.name, True, WHITE)
            screen.blit(name_text, (SCREEN_WIDTH//2 - 100 + i*70, SCREEN_HEIGHT//2 + 190))
    
    def draw_instructions(self):
        title = font_large.render("INSTRUCTIONS", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        instructions = [
            "Team-based fighting game with 3 player characters",
            "Defeat enemy teams across 9 challenging levels",
            "Every 3rd level is a boss fight!",
            "",
            "CONTROLS:",
            "LEFT/RIGHT arrows - Move",
            "SPACE - Basic Attack",
            "TAB - Switch Characters",
            "H - Use First Aid Kit (Heal 30%)",
            "E - Use Special Ability",
            "",
            "SPECIAL ABILITIES:",
            "Warrior: Power Strike (2x damage next attack)",
            "Mage: Heal Team (20% heal to all members)",
            "Rogue: Quick Attack (Fast consecutive attacks)",
            "",
            "Press ENTER or ESC to return to menu"
        ]
        
        for i, line in enumerate(instructions):
            text = font_small.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 150 + i * 30))
    
    def draw_game(self):
        # Draw level info
        self.current_level.draw_timer(screen)
        
        # Draw teams
        self.player_team.draw(screen)
        self.current_level.enemy_team.draw(screen)
        
        # Draw characters
        current_player = self.player_team.get_current_member()
        if current_player:
            current_player.draw(screen)
        
        current_enemy = self.current_level.enemy_team.get_current_member()
        if current_enemy:
            current_enemy.draw(screen)
        
        # Draw score and controls reminder
        score_text = font_medium.render(f"Score: {self.player_team.score + self.level_score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT - 40))
        
        controls_text = font_small.render("TAB:Switch  H:Heal  E:Special  ESC:Menu", True, WHITE)
        screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 80))
    
    def draw_level_complete(self):
        title = font_large.render("LEVEL COMPLETE!", True, GREEN)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 150))
        
        score_text = font_medium.render(f"Level Score: {self.level_score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        total_text = font_medium.render(f"Total Score: {self.player_team.score}", True, WHITE)
        screen.blit(total_text, (SCREEN_WIDTH//2 - total_text.get_width()//2, SCREEN_HEIGHT//2))
        
        next_text = font_medium.render("Press ENTER to continue to next level", True, WHITE)
        screen.blit(next_text, (SCREEN_WIDTH//2 - next_text.get_width()//2, SCREEN_HEIGHT//2 + 100))
    
    def draw_game_over(self):
        title = font_large.render("GAME OVER", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 150))
        
        score_text = font_medium.render(f"Final Score: {self.player_team.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        level_text = font_medium.render(f"Reached Level: {self.current_level.level_num}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, SCREEN_HEIGHT//2))
        
        restart_text = font_medium.render("Press ENTER to return to menu", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 100))
    
    def draw_victory(self):
        title = font_large.render("VICTORY!", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 150))
        
        congrats_text = font_medium.render("You defeated all enemies!", True, WHITE)
        screen.blit(congrats_text, (SCREEN_WIDTH//2 - congrats_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        score_text = font_medium.render(f"Final Score: {self.player_team.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        
        restart_text = font_medium.render("Press ENTER to return to menu", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 100))
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# Create and run the game
if __name__ == "__main__":
    game = FightingGame()
    game.run()
    pygame.quit()
    sys.exit()