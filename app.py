import os
import sys

# Get the absolute path to the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core.quiz_engine import QuizEngine
except ImportError as e:
    print(f"ImportError: {e}")
    print("Current Python path:")
    for path in sys.path:
        print(f"  - {path}")
    raise

class QuizApp:
    def __init__(self):
        self.engine = QuizEngine()
        
    def run(self):
        print("Welcome to the Quiz Game!")
        self.engine.load_questions() 
import tkinter as tk
from tkinter import ttk
from core.quiz_engine import QuizEngine  # Import from package

class QuizApp:
    def __init__(self, root):  # Accept root window parameter
        self.root = root
        self.root.title("Quiz Game")
        self.engine = QuizEngine()
        self.setup_ui()

    def setup_ui(self):
        # Basic UI setup
        self.frame = ttk.Frame(self.root)
        self.frame.pack(padx=20, pady=20)
        
        self.welcome_label = ttk.Label(
            self.frame, 
            text="Welcome to Quiz Game!", 
            font=('Helvetica', 16)
        )
        self.welcome_label.pack(pady=10)

    def start_quiz(self):
        # Quiz logic will go here
        pass
        self.engine.run_quiz()
        self.engine.display_results()

if __name__ == "__main__":
    app = QuizApp()
    app.run()