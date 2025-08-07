import pygame
import random
from threading import Thread, Event

# Initialize Pygame
pygame.init()

class MazeGame:
    def __init__(self):
        self.cell_size = 40  # Pixels per cell
        self.base_grid_size = 5  # Starting maze size (5x5)
        self.level = 1
        self.grid_size = self.base_grid_size
        self.screen_width = self.grid_size * self.cell_size
        self.screen_height = self.grid_size * self.cell_size + 60  # Space for status
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Maze Game")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        
        # Font
        self.font = pygame.font.SysFont("arial", 24)
        
        # Game state
        self.player_pos = [0, 0]
        self.exit_pos = [0, 0]
        self.maze = []
        self.time_limit = 30  # Base time limit in seconds
        self.time_remaining = self.time_limit
        self.game_over = False
        self.stop_timer = Event()
        self.message = ""
        self.message_timer = 0
        
        self.setup_level()

    def generate_maze(self):
        # Initialize grid with walls
        self.maze = [[1 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Recursive backtracking to generate maze
        def carve_path(x, y):
            self.maze[x][y] = 0  # Mark as path
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # Right, Down, Left, Up
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and self.maze[nx][ny] == 1:
                    self.maze[x + dx//2][y + dy//2] = 0  # Carve passage
                    carve_path(nx, ny)
        
        # Start carving from (0,0)
        carve_path(0, 0)
        
        # Set exit at a distant position
        self.exit_pos = [self.grid_size-1, self.grid_size-1]
        self.maze[self.exit_pos[0]][self.exit_pos[1]] = 0

    def setup_level(self):
        # Increase maze size every other level
        self.grid_size = self.base_grid_size + (self.level // 2) * 2
        self.screen_width = self.grid_size * self.cell_size
        self.screen_height = self.grid_size * self.cell_size + 60
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Reset positions
        self.player_pos = [0, 0]
        self.generate_maze()
        self.time_remaining = self.time_limit + (self.level * 5)  # Increase time with level
        self.stop_timer.clear()
        self.message = f"Level {self.level} Start!"
        self.message_timer = pygame.time.get_ticks() + 2000

    def draw_maze(self):
        self.screen.fill(self.BLACK)
        # Draw maze
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rect = pygame.Rect(j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size)
                if self.maze[i][j] == 1:
                    pygame.draw.rect(self.screen, self.WHITE, rect)  # Wall
                else:
                    pygame.draw.rect(self.screen, self.BLACK, rect)  # Path
                    pygame.draw.rect(self.screen, self.WHITE, rect, 1)  # Grid lines

                # Draw player and exit
                if [i, j] == self.player_pos:
                    pygame.draw.circle(self.screen, self.BLUE, 
                                     (j * self.cell_size + self.cell_size // 2, i * self.cell_size + self.cell_size // 2), 
                                     self.cell_size // 3)
                elif [i, j] == self.exit_pos:
                    pygame.draw.rect(self.screen, self.GREEN, 
                                   (j * self.cell_size + self.cell_size // 4, i * self.cell_size + self.cell_size // 4, 
                                    self.cell_size // 2, self.cell_size // 2))

        # Draw status
        status_text = f"Level: {self.level} | Time: {self.time_remaining:.1f}s"
        status_surface = self.font.render(status_text, True, self.WHITE)
        self.screen.blit(status_surface, (10, self.screen_height - 50))

        # Draw message if active
        if self.message and pygame.time.get_ticks() < self.message_timer:
            message_surface = self.font.render(self.message, True, self.WHITE)
            self.screen.blit(message_surface, (self.screen_width // 2 - message_surface.get_width() // 2, self.screen_height - 30))

        pygame.display.flip()

    def move_player(self, direction):
        new_pos = self.player_pos.copy()
        if direction == 'w' and self.player_pos[0] > 0:
            new_pos[0] -= 1
        elif direction == 's' and self.player_pos[0] < self.grid_size - 1:
            new_pos[0] += 1
        elif direction == 'a' and self.player_pos[1] > 0:
            new_pos[1] -= 1
        elif direction == 'd' and self.player_pos[1] < self.grid_size - 1:
            new_pos[1] += 1
        else:
            self.message = "Cannot move there!"
            self.message_timer = pygame.time.get_ticks() + 1000
            return

        # Check if move is valid (not a wall)
        if self.maze[new_pos[0]][new_pos[1]] == 0:
            self.player_pos = new_pos
        else:
            self.message = "Wall in the way!"
            self.message_timer = pygame.time.get_ticks() + 1000

        # Check if reached exit
        if self.player_pos == self.exit_pos:
            self.level += 1
            self.message = f"Level {self.level-1} completed!"
            self.message_timer = pygame.time.get_ticks() + 2000
            self.stop_timer.set()

    def timer(self):
        while not self.stop_timer.is_set() and self.time_remaining > 0:
            
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.message = "Time's up! Game Over."
                self.message_timer = pygame.time.get_ticks() + 2000
                self.game_over = True
                break

    def run(self):
        clock = pygame.time.Clock()
        timer_thread = Thread(target=self.timer)
        timer_thread.start()

        while not self.game_over:
            self.draw_maze()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.message = "Game quit."
                    self.message_timer = pygame.time.get_ticks() + 2000
                    self.game_over = True
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.message = "Game quit."
                        self.message_timer = pygame.time.get_ticks() + 2000
                        self.game_over = True
                    elif event.key == pygame.K_w:
                        self.move_player('w')
                    elif event.key == pygame.K_s:
                        self.move_player('s')
                    elif event.key == pygame.K_a:
                        self.move_player('a')
                    elif event.key == pygame.K_d:
                        self.move_player('d')

            # Check if level completed
            if self.stop_timer.is_set() and not self.game_over:
                timer_thread.join()
                self.setup_level()
                timer_thread = Thread(target=self.timer)
                timer_thread.start()

            clock.tick(60)  # 60 FPS

        self.stop_timer.set()
        timer_thread.join()

        # Final screen
        self.draw_maze()
        pygame.time.wait(2000)  # Show final message
        pygame.quit()

if __name__ == "__main__":
    game = MazeGame()
    game.run()