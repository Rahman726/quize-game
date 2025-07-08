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
        self.engine.run_quiz()
        self.engine.display_results()

if __name__ == "__main__":
    app = QuizApp()
    app.run()