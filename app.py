import tkinter as tk
from tkinter import ttk ,messagebox
from core.quiz_engine import QuizEngine
from core.ai_integration import AIIntegration

class QuizApp:
    def __init__(self, root):
        """Initialize the application with root window"""
        self.root = root
        self.root.title("Quiz Game")
        self.root.geometry("800x600")
        
        # Initialize core components
        self.engine = QuizEngine()
        self.ai = AIIntegration()
        
        # Setup UI
        self.setup_ui()
        self.show_welcome_screen()

    def setup_ui(self):
        """Create main application frames"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def show_welcome_screen(self):
        """Display welcome screen"""
        self.clear_frame()
        
        ttk.Label(
            self.main_frame,
            text="Welcome to Quiz Game!",
            font=('Helvetica', 24)
        ).pack(pady=50)
        
        ttk.Button(
            self.main_frame,
            text="Start Quiz",
            command=self.show_category_selection
        ).pack(pady=20)

    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_category_selection(self):
        """Show category selection screen"""
        self.clear_frame()
        
        ttk.Label(
            self.main_frame,
            text="Select Category",
            font=('Helvetica', 20)
        ).pack(pady=30)
        
        # Add your category buttons here
        categories = self.engine.get_categories()
        for category in categories:
            ttk.Button(
                self.main_frame,
                text=category,
                command=lambda c=category: self.start_quiz(c)
            ).pack(pady=10)

    def start_quiz(self, category):
        """Start quiz with selected category"""
        self.engine.start_quiz(category)
        self.show_question()
    def show_question(self):
        """Display current question"""
        self.clear_frame()
        question = self.engine.get_current_question()
        
        if not question:
            self.show_results()
            return
            
        # Question text
        ttk.Label(
            self.main_frame,
            text=question['question'],
            font=('Helvetica', 16),
            wraplength=700
        ).pack(pady=20)
        
        # Options
        for i, option in enumerate(question['options']):
            ttk.Button(
                self.main_frame,
                text=option,
                command=lambda idx=i: self.check_answer(idx),
                width=40
            ).pack(pady=5)

    def check_answer(self, selected_index):
        """Check selected answer and proceed"""
        is_correct = self.engine.check_answer(selected_index)
        feedback = "Correct!" if is_correct else "Incorrect!"
        messagebox.showinfo("Result", feedback)
        self.next_question()

    def next_question(self):
        """Move to next question or show results"""
        if self.engine.next_question():
            self.show_question()
        else:
            self.show_results()

    def show_results(self):
        """Display final score"""
        self.clear_frame()
        ttk.Label(
            self.main_frame,
            text=f"Quiz Completed!\nScore: {self.engine.score}/{len(self.engine.filtered_questions)}",
            font=('Helvetica', 24)
        ).pack(pady=50)
        
        ttk.Button(
            self.main_frame,
            text="Play Again",
            command=self.show_welcome_screen
        ).pack(pady=20)
