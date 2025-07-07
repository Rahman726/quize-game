import tkinter as tk
from core.quiz_engine import QuizEngine
from core.ai_integration import AIIntegration
from styles.theme import configure_styles
from views.welcome import WelcomeView
from views.category import CategoryView
# ... other view imports

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered Quiz Game")
        self.root.geometry("900x700")
        
        self.quiz_engine = QuizEngine()
        self.ai = AIIntegration()
        self.styles = configure_styles()
        
        # Initialize views
        self.welcome_view = WelcomeView(root, self)
        self.category_view = CategoryView(root, self)
        # ... other views
        
        self.show_welcome()

    def show_welcome(self):
        self.welcome_view.show()

    def start_game(self, player_name):
        self.player_name = player_name
        self.welcome_view.hide()
        self.category_view.show()

    # ... other controller methods