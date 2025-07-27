import pygame
import sys
import random
import time
from enum import Enum
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from threading import Thread
import webbrowser

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 900
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (247, 247, 105, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
FONT = pygame.font.SysFont('Arial', 24)
LARGE_FONT = pygame.font.SysFont('Arial', 36)

# Chess Enums
class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class PieceColor(Enum):
    WHITE = 0
    BLACK = 1

class GameMode(Enum):
    COMPUTER = 0
    PUZZLE = 1
    MULTIPLAYER = 2
    FRIEND = 3

# Chess Piece Class
class Piece:
    def __init__(self, color, piece_type, position):
        self.color = color
        self.type = piece_type
        self.position = position  # (row, col)
        self.has_moved = False
        self.possible_moves = []
    
    def get_symbol(self):
        symbols = {
            PieceType.PAWN: '♙',
            PieceType.KNIGHT: '♘',
            PieceType.BISHOP: '♗',
            PieceType.ROOK: '♖',
            PieceType.QUEEN: '♕',
            PieceType.KING: '♔'
        }
        # Use white symbols but color them appropriately
        return symbols[self.type]
    
    def get_value(self):
        values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 0  # Priceless!
        }
        return values[self.type]

# Chess Game Class
class ChessGame:
    def __init__(self, mode=GameMode.COMPUTER):
        self.board = self.initialize_board()
        self.current_turn = PieceColor.WHITE
        self.selected_piece = None
        self.move_history = []
        self.white_time = 600  # 10 minutes in seconds
        self.black_time = 600
        self.last_move_time = time.time()
        self.game_over = False
        self.winner = None
        self.check = False
        self.checkmate = False
        self.stalemate = False
        self.mode = mode
        self.puzzle_solution = []
        self.puzzle_moves = []
        self.player_color = PieceColor.WHITE
        self.ai_thinking = False
        self.message = ""
        self.message_timer = 0
    
    def initialize_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Pawns
        for col in range(8):
            board[1][col] = Piece(PieceColor.BLACK, PieceType.PAWN, (1, col))
            board[6][col] = Piece(PieceColor.WHITE, PieceType.PAWN, (6, col))
        
        # Rooks
        board[0][0] = board[0][7] = Piece(PieceColor.BLACK, PieceType.ROOK, (0, 0))
        board[7][0] = board[7][7] = Piece(PieceColor.WHITE, PieceType.ROOK, (7, 0))
        
        # Knights
        board[0][1] = board[0][6] = Piece(PieceColor.BLACK, PieceType.KNIGHT, (0, 1))
        board[7][1] = board[7][6] = Piece(PieceColor.WHITE, PieceType.KNIGHT, (7, 1))
        
        # Bishops
        board[0][2] = board[0][5] = Piece(PieceColor.BLACK, PieceType.BISHOP, (0, 2))
        board[7][2] = board[7][5] = Piece(PieceColor.WHITE, PieceType.BISHOP, (7, 2))
        
        # Queens
        board[0][3] = Piece(PieceColor.BLACK, PieceType.QUEEN, (0, 3))
        board[7][3] = Piece(PieceColor.WHITE, PieceType.QUEEN, (7, 3))
        
        # Kings
        board[0][4] = Piece(PieceColor.BLACK, PieceType.KING, (0, 4))
        board[7][4] = Piece(PieceColor.WHITE, PieceType.KING, (7, 4))
        
        return board
    
    def update_timer(self):
        current_time = time.time()
        time_elapsed = current_time - self.last_move_time
        self.last_move_time = current_time
        
        if not self.game_over and not self.ai_thinking:
            if self.current_turn == PieceColor.WHITE:
                self.white_time -= time_elapsed
                if self.white_time <= 0:
                    self.game_over = True
                    self.winner = PieceColor.BLACK
                    self.message = "White ran out of time! Black wins!"
                    self.message_timer = 5
            else:
                self.black_time -= time_elapsed
                if self.black_time <= 0:
                    self.game_over = True
                    self.winner = PieceColor.WHITE
                    self.message = "Black ran out of time! White wins!"
                    self.message_timer = 5
    
    def is_valid_position(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8
    
    def get_possible_moves(self, piece):
        moves = []
        row, col = piece.position
        
        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == PieceColor.WHITE else 1
            # Forward move
            if self.is_valid_position(row + direction, col) and not self.board[row + direction][col]:
                moves.append((row + direction, col))
                # Double move from starting position
                start_row = 6 if piece.color == PieceColor.WHITE else 1
                if row == start_row and not self.board[row + 2*direction][col]:
                    moves.append((row + 2*direction, col))
            # Captures
            for dc in [-1, 1]:
                if self.is_valid_position(row + direction, col + dc):
                    target = self.board[row + direction][col + dc]
                    if target and target.color != piece.color:
                        moves.append((row + direction, col + dc))
        
        elif piece.type == PieceType.KNIGHT:
            knight_moves = [
                (row+2, col+1), (row+2, col-1),
                (row-2, col+1), (row-2, col-1),
                (row+1, col+2), (row+1, col-2),
                (row-1, col+2), (row-1, col-2)
            ]
            for r, c in knight_moves:
                if self.is_valid_position(r, c):
                    target = self.board[r][c]
                    if not target or target.color != piece.color:
                        moves.append((r, c))
        
        elif piece.type == PieceType.BISHOP:
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    r, c = row + i*dr, col + i*dc
                    if not self.is_valid_position(r, c):
                        break
                    target = self.board[r][c]
                    if not target:
                        moves.append((r, c))
                    else:
                        if target.color != piece.color:
                            moves.append((r, c))
                        break
        
        elif piece.type == PieceType.ROOK:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    r, c = row + i*dr, col + i*dc
                    if not self.is_valid_position(r, c):
                        break
                    target = self.board[r][c]
                    if not target:
                        moves.append((r, c))
                    else:
                        if target.color != piece.color:
                            moves.append((r, c))
                        break
        
        elif piece.type == PieceType.QUEEN:
            # Combine bishop and rook moves
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), 
                          (1, 0), (-1, 0), (0, 1), (0, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    r, c = row + i*dr, col + i*dc
                    if not self.is_valid_position(r, c):
                        break
                    target = self.board[r][c]
                    if not target:
                        moves.append((r, c))
                    else:
                        if target.color != piece.color:
                            moves.append((r, c))
                        break
        
        elif piece.type == PieceType.KING:
            king_moves = [
                (row+1, col), (row-1, col),
                (row, col+1), (row, col-1),
                (row+1, col+1), (row+1, col-1),
                (row-1, col+1), (row-1, col-1)
            ]
            for r, c in king_moves:
                if self.is_valid_position(r, c):
                    target = self.board[r][c]
                    if not target or target.color != piece.color:
                        moves.append((r, c))
        
        return moves
    
    def make_move(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.board[start_row][start_col]
        
        if not piece or piece.color != self.current_turn:
            return False
        
        possible_moves = self.get_possible_moves(piece)
        if (end_row, end_col) not in possible_moves:
            return False
        
        # Check if move would leave king in check
        # (This is a simplified check - in a real game you'd need to make the move and verify)
        
        # Update timer
        self.update_timer()
        
        # Move the piece
        captured_piece = self.board[end_row][end_col]
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.position = (end_row, end_col)
        piece.has_moved = True
        
        # Record move
        self.move_history.append((start_pos, end_pos, captured_piece))
        
        # Check for pawn promotion
        if piece.type == PieceType.PAWN and (end_row == 0 or end_row == 7):
            piece.type = PieceType.QUEEN  # Auto-queen for simplicity
        
        # Check for game end conditions
        self.check_for_check()
        self.check_for_game_end()
        
        # Switch turns
        self.current_turn = PieceColor.BLACK if self.current_turn == PieceColor.WHITE else PieceColor.WHITE
        
        return True
    
    def check_for_check(self):
        # Find kings
        white_king_pos = None
        black_king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.type == PieceType.KING:
                    if piece.color == PieceColor.WHITE:
                        white_king_pos = (row, col)
                    else:
                        black_king_pos = (row, col)
        
        # Check if either king is under attack
        self.check = False
        if white_king_pos:
            self.check = self.is_square_under_attack(white_king_pos, PieceColor.BLACK)
        if black_king_pos and not self.check:
            self.check = self.is_square_under_attack(black_king_pos, PieceColor.WHITE)
    
    def is_square_under_attack(self, position, by_color):
        row, col = position
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == by_color:
                    if (row, col) in self.get_possible_moves(piece):
                        return True
        return False
    
    def check_for_game_end(self):
        # Check for checkmate or stalemate
        has_legal_moves = False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == self.current_turn:
                    if self.get_possible_moves(piece):
                        has_legal_moves = True
                        break
            if has_legal_moves:
                break
        
        if not has_legal_moves:
            if self.check:
                self.checkmate = True
                self.game_over = True
                self.winner = PieceColor.BLACK if self.current_turn == PieceColor.WHITE else PieceColor.WHITE
                self.message = "Checkmate! " + ("White" if self.winner == PieceColor.WHITE else "Black") + " wins!"
                self.message_timer = 5
            else:
                self.stalemate = True
                self.game_over = True
                self.message = "Stalemate! Game drawn."
                self.message_timer = 5
    
    def draw(self, screen):
        # Draw board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                # Highlight selected piece and possible moves
                if self.selected_piece and self.selected_piece.position == (row, col):
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(HIGHLIGHT)
                    screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                # Highlight possible moves
                if self.selected_piece:
                    possible_moves = self.get_possible_moves(self.selected_piece)
                    for r, c in possible_moves:
                        if (r, c) == (row, col):
                            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                            highlight.fill((100, 255, 100, 150))
                            screen.blit(highlight, (c * SQUARE_SIZE, r * SQUARE_SIZE))
        
        # Draw pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    text_color = WHITE if piece.color == PieceColor.WHITE else BLACK
                    symbol = piece.get_symbol()
                    text = FONT.render(symbol, True, text_color)
                    screen.blit(text, (col * SQUARE_SIZE + SQUARE_SIZE//2 - text.get_width()//2, 
                                      row * SQUARE_SIZE + SQUARE_SIZE//2 - text.get_height()//2))
        
        # Draw timer
        white_time_text = FONT.render(f"White: {int(self.white_time//60)}:{int(self.white_time%60):02d}", True, BLACK)
        black_time_text = FONT.render(f"Black: {int(self.black_time//60)}:{int(self.black_time%60):02d}", True, BLACK)
        screen.blit(white_time_text, (20, HEIGHT - 80))
        screen.blit(black_time_text, (WIDTH - 150, HEIGHT - 80))
        
        # Draw game status
        if self.message_timer > 0:
            status_text = LARGE_FONT.render(self.message, True, RED)
            screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 40))
            self.message_timer -= 1/FPS
        elif self.game_over:
            if self.checkmate:
                status_text = LARGE_FONT.render(f"Checkmate! {'White' if self.winner == PieceColor.WHITE else 'Black'} wins!", True, RED)
            elif self.stalemate:
                status_text = LARGE_FONT.render("Stalemate! Game drawn.", True, BLUE)
            else:
                status_text = LARGE_FONT.render(f"Game Over! {'White' if self.winner == PieceColor.WHITE else 'Black'} wins!", True, RED)
            screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 40))
        elif self.check:
            status_text = FONT.render("CHECK!", True, RED)
            screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 40))
        
        # Draw current turn indicator
        turn_text = FONT.render(f"Current turn: {'White' if self.current_turn == PieceColor.WHITE else 'Black'}", 
                               True, GREEN if self.current_turn == PieceColor.WHITE else BLACK)
        screen.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, HEIGHT - 120))
        
        # Draw mode indicator
        mode_text = FONT.render(f"Mode: {self.mode.name}", True, BLUE)
        screen.blit(mode_text, (WIDTH//2 - mode_text.get_width()//2, 10))

# Chess AI
class ChessAI:
    def __init__(self, game):
        self.game = game
        self.difficulty = 1  # 1-3
    
    def evaluate_board(self):
        score = 0
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece:
                    value = piece.get_value()
                    score += value if piece.color == PieceColor.WHITE else -value
        return score
    
    def minimax(self, depth, is_maximizing, alpha, beta):
        if depth == 0 or self.game.game_over:
            return self.evaluate_board()
        
        if is_maximizing:
            max_eval = -float('inf')
            for row in range(8):
                for col in range(8):
                    piece = self.game.board[row][col]
                    if piece and piece.color == PieceColor.WHITE:
                        moves = self.game.get_possible_moves(piece)
                        for move in moves:
                            # Make move
                            original_pos = piece.position
                            captured_piece = self.game.board[move[0]][move[1]]
                            self.game.board[move[0]][move[1]] = piece
                            self.game.board[original_pos[0]][original_pos[1]] = None
                            piece.position = move
                            
                            # Evaluate
                            eval = self.minimax(depth - 1, False, alpha, beta)
                            max_eval = max(max_eval, eval)
                            alpha = max(alpha, eval)
                            
                            # Undo move
                            self.game.board[original_pos[0]][original_pos[1]] = piece
                            self.game.board[move[0]][move[1]] = captured_piece
                            piece.position = original_pos
                            
                            if beta <= alpha:
                                return max_eval
            return max_eval
        else:
            min_eval = float('inf')
            for row in range(8):
                for col in range(8):
                    piece = self.game.board[row][col]
                    if piece and piece.color == PieceColor.BLACK:
                        moves = self.game.get_possible_moves(piece)
                        for move in moves:
                            # Make move
                            original_pos = piece.position
                            captured_piece = self.game.board[move[0]][move[1]]
                            self.game.board[move[0]][move[1]] = piece
                            self.game.board[original_pos[0]][original_pos[1]] = None
                            piece.position = move
                            
                            # Evaluate
                            eval = self.minimax(depth - 1, True, alpha, beta)
                            min_eval = min(min_eval, eval)
                            beta = min(beta, eval)
                            
                            # Undo move
                            self.game.board[original_pos[0]][original_pos[1]] = piece
                            self.game.board[move[0]][move[1]] = captured_piece
                            piece.position = original_pos
                            
                            if beta <= alpha:
                                return min_eval
            return min_eval
    
    def find_best_move(self):
        best_move = None
        best_value = -float('inf') if self.game.current_turn == PieceColor.WHITE else float('inf')
        
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece and piece.color == self.game.current_turn:
                    moves = self.game.get_possible_moves(piece)
                    for move in moves:
                        # Make move
                        original_pos = piece.position
                        captured_piece = self.game.board[move[0]][move[1]]
                        self.game.board[move[0]][move[1]] = piece
                        self.game.board[original_pos[0]][original_pos[1]] = None
                        piece.position = move
                        
                        # Evaluate
                        board_value = self.minimax(self.difficulty, self.game.current_turn == PieceColor.BLACK, -float('inf'), float('inf'))
                        
                        # Undo move
                        self.game.board[original_pos[0]][original_pos[1]] = piece
                        self.game.board[move[0]][move[1]] = captured_piece
                        piece.position = original_pos
                        
                        if (self.game.current_turn == PieceColor.WHITE and board_value > best_value) or \
                           (self.game.current_turn == PieceColor.BLACK and board_value < best_value):
                            best_value = board_value
                            best_move = ((row, col), move)
        
        return best_move
    
    def make_move(self):
        self.game.ai_thinking = True
        time.sleep(0.5)  # Simulate thinking time
        
        if self.difficulty > 1:
            best_move = self.find_best_move()
        else:
            # For lower difficulty, just pick a random move
            possible_moves = []
            for row in range(8):
                for col in range(8):
                    piece = self.game.board[row][col]
                    if piece and piece.color == self.game.current_turn:
                        moves = self.game.get_possible_moves(piece)
                        for move in moves:
                            possible_moves.append(((row, col), move))
            best_move = random.choice(possible_moves) if possible_moves else None
        
        if best_move:
            self.game.make_move(best_move[0], best_move[1])
        
        self.game.ai_thinking = False

# Puzzle Database
puzzles = [
    {
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
        "solution": ["f3g5"],
        "description": "Fork the king and queen"
    },
    {
        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
        "solution": ["f3e5", "f6e4", "d1d8"],
        "description": "Double attack leading to queen capture"
    }
]

# Flask Web Application for Authentication
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database setup
def get_db_connection():
    conn = sqlite3.connect('chess_users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('chess_users.db'):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                rating INTEGER DEFAULT 1000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1 TEXT NOT NULL,
                player2 TEXT,
                fen TEXT NOT NULL,
                status TEXT DEFAULT 'ongoing',
                winner TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

# HTML Templates
base_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chess Game</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .alert-error { background-color: #ffdddd; color: #ff0000; }
        .alert-success { background-color: #ddffdd; color: #00aa00; }
        .alert-info { background-color: #ddddff; color: #0000aa; }
        .game-mode { 
            display: inline-block; 
            width: 200px; 
            height: 100px; 
            margin: 10px; 
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            text-align: center;
            vertical-align: top;
            cursor: pointer;
        }
        .game-mode:hover { background-color: #f0f0f0; }
        nav { background: #f8f8f8; padding: 10px; margin-bottom: 20px; }
        nav a { margin-right: 15px; text-decoration: none; color: #333; }
        nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        {% if 'username' in session %}
            <a href="/play">Play</a>
            <a href="/puzzles">Puzzles</a>
            <a href="/multiplayer">Multiplayer</a>
            <a href="/logout">Logout ({{ session['username'] }})</a>
        {% else %}
            <a href="/login">Login</a>
            <a href="/register">Register</a>
        {% endif %}
    </nav>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
</body>
</html>
'''

login_template = '''
{% extends "base.html" %}
{% block content %}
    <h1>Login</h1>
    <form method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br>
        <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
{% endblock %}
'''

register_template = '''
{% extends "base.html" %}
{% block content %}
    <h1>Register</h1>
    <form method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required><br>
        <label for="email">Email (optional):</label>
        <input type="email" id="email" name="email"><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
{% endblock %}
'''

play_template = '''
{% extends "base.html" %}
{% block content %}
    <h1>Choose Game Mode</h1>
    <div>
        <div class="game-mode" onclick="window.location.href='/start_game?mode=computer'">
            <h3>vs Computer</h3>
            <p>Play against AI with adjustable difficulty</p>
        </div>
        <div class="game-mode" onclick="window.location.href='/start_game?mode=puzzle'">
            <h3>Puzzles</h3>
            <p>Solve tactical chess puzzles</p>
        </div>
        <div class="game-mode" onclick="window.location.href='/start_game?mode=multiplayer'">
            <h3>Multiplayer</h3>
            <p>Play against random opponents online</p>
        </div>
        <div class="game-mode" onclick="window.location.href='/start_game?mode=friend'">
            <h3>Play with Friend</h3>
            <p>Challenge a specific friend</p>
        </div>
    </div>
{% endblock %}
'''

# Flask Routes
@app.route('/')
def index():
    if 'username' in session:
        return render_template_string(base_template + '''
            <h1>Welcome to Chess Game, {{ session['username'] }}!</h1>
            <p>Select a game mode from the navigation menu to start playing.</p>
        ''')
    return render_template_string(base_template + '''
        <h1>Welcome to Chess Game!</h1>
        <p>Please <a href="/login">login</a> or <a href="/register">register</a> to play.</p>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template_string(login_template)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form.get('email', '')
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                         (username, password, email))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'error')
        finally:
            conn.close()
    
    return render_template_string(register_template)

@app.route('/play')
def play_menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template_string(play_template)

@app.route('/start_game')
def start_game():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    mode = request.args.get('mode', 'computer')
    if mode == 'computer':
        game_mode = GameMode.COMPUTER
    elif mode == 'puzzle':
        game_mode = GameMode.PUZZLE
    elif mode == 'multiplayer':
        game_mode = GameMode.MULTIPLAYER
    elif mode == 'friend':
        game_mode = GameMode.FRIEND
    else:
        flash('Invalid game mode', 'error')
        return redirect(url_for('play_menu'))
    
    # In a real app, you would launch the game window here
    # For this example, we'll just show a message
    flash(f'Starting {mode} game...', 'info')
    return redirect(url_for('index'))

@app.route('/puzzles')
def puzzle_mode():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Puzzle mode would launch here"

@app.route('/multiplayer')
def multiplayer():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "Multiplayer mode would launch here"

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Main Game Loop
def run_chess_game(mode=GameMode.COMPUTER):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Python Chess')
    clock = pygame.time.Clock()
    
    game = ChessGame(mode)
    ai = ChessAI(game)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game.game_over and not game.ai_thinking:
                if event.button == 1:  # Left click
                    col = event.pos[0] // SQUARE_SIZE
                    row = event.pos[1] // SQUARE_SIZE
                    
                    if 0 <= row < 8 and 0 <= col < 8:
                        if game.selected_piece:
                            # Try to move the selected piece
                            if game.make_move(game.selected_piece.position, (row, col)):
                                game.selected_piece = None
                                # AI move in computer mode
                                if mode == GameMode.COMPUTER and not game.game_over and game.current_turn != game.player_color:
                                    ai.make_move()
                            elif game.mode == GameMode.PUZZLE:
                                # Check puzzle solution
                                pass
                        else:
                            # Select a piece
                            piece = game.board[row][col]
                            if piece and piece.color == game.current_turn:
                                game.selected_piece = piece
        
        # Update timer
        game.update_timer()
        
        # Draw everything
        screen.fill(WHITE)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

# Run the application
if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start Flask server in a separate thread
    flask_thread = Thread(target=lambda: app.run(port=5000, threaded=True))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Wait a moment for the server to start
    time.sleep(1)
    
    # Open browser to the login page
    webbrowser.open('http://localhost:5000')
    
    # Run the chess game (for demo purposes, we'll run vs computer)
    run_chess_game(GameMode.COMPUTER)