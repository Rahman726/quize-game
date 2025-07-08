import tkinter as tk
from tkinter import ttk, messagebox
from core.quiz_engine import QuizEngine

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game")
        self.root.geometry("800x600")
        self.engine = QuizEngine()
        self.current_question = 0
        self.score = 0
        self.setup_ui()
        
        # Start with welcome screen
        self.show_welcome_screen()

    def setup_ui(self):
        """Initialize all UI components"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        """Display welcome screen with start button"""
        self.clear_frame()
        
        ttk.Label(
            self.main_frame,
            text="Welcome to Quiz Game!",
            font=('Helvetica', 24, 'bold')
        ).pack(pady=50)
        
        ttk.Button(
            self.main_frame,
            text="Start Quiz",
            command=self.show_category_selection
        ).pack(pady=20)

    def show_category_selection(self):
        """Show category selection screen"""
        self.clear_frame()
        
        ttk.Label(
            self.main_frame,
            text="Select Quiz Category",
            font=('Helvetica', 20)
        ).pack(pady=30)
        
        categories = self.engine.get_categories()
        
        for category in categories:
            ttk.Button(
                self.main_frame,
                text=category,
                command=lambda c=category: self.start_quiz(c),
                width=20
            ).pack(pady=10)
            
        ttk.Button(
            self.main_frame,
            text="Exit",
            command=self.root.quit
        ).pack(pady=20)

    def start_quiz(self, category):
        """Start quiz with selected category"""
        self.engine.start_quiz(category)
        self.current_question = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        """Display current question and options"""
        self.clear_frame()
        
        if not self.engine.has_next_question():
            self.show_results()
            return
            
        question = self.engine.get_current_question()
        
        # Question text
        ttk.Label(
            self.main_frame,
            text=question['question'],
            font=('Helvetica', 16),
            wraplength=700
        ).pack(pady=20)
        
        # Difficulty indicator
        ttk.Label(
            self.main_frame,
            text=f"Difficulty: {question['difficulty']}",
            font=('Helvetica', 12, 'italic')
        ).pack()
        
        # Options
        self.option_buttons = []
        for i, option in enumerate(question['options']):
            btn = ttk.Button(
                self.main_frame,
                text=option,
                command=lambda idx=i: self.check_answer(idx),
                width=40
            )
            btn.pack(pady=5)
            self.option_buttons.append(btn)
        
        # Score display
        self.score_label = ttk.Label(
            self.main_frame,
            text=f"Score: {self.score}",
            font=('Helvetica', 14)
        )
        self.score_label.pack(pady=20)

    def check_answer(self, selected_index):
        """Check if answer is correct and update UI"""
        is_correct = self.engine.check_answer(selected_index)
        
        if is_correct:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
        
        # Highlight correct answer
        correct_idx = self.engine.get_current_question()['answer']
        self.option_buttons[correct_idx].config(style='Success.TButton')
        
        if not is_correct:
            self.option_buttons[selected_index].config(style='Error.TButton')
        
        # Move to next question after delay
        self.root.after(1500, self.next_question)

    def next_question(self):
        """Proceed to next question or show results"""
        self.engine.next_question()
        self.current_question += 1
        self.show_question()

    def show_results(self):
        """Display final results"""
        self.clear_frame()
        
        result = self.engine.get_results()
        
        ttk.Label(
            self.main_frame,
            text="Quiz Completed!",
            font=('Helvetica', 24, 'bold')
        ).pack(pady=30)
        
        ttk.Label(
            self.main_frame,
            text=f"Final Score: {result['score']}/{result['total']}",
            font=('Helvetica', 18)
        ).pack(pady=20)
        
        ttk.Label(
            self.main_frame,
            text=f"Percentage: {result['percentage']:.1f}%",
            font=('Helvetica', 16)
        ).pack(pady=10)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=30)
        
        ttk.Button(
            button_frame,
            text="Try Again",
            command=self.show_category_selection
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit
        ).pack(side=tk.LEFT, padx=10)

    def configure_styles(self):
        """Configure custom widget styles"""
        style = ttk.Style()
        style.configure('Success.TButton', foreground='green')
        style.configure('Error.TButton', foreground='red')