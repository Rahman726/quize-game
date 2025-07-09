import tkinter as tk
import asyncio
import threading
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

       # Setup async infrastructure
        self.loop = asyncio.new_event_loop()
        self.ai_thread = None
        self.running_tasks = []

    def run_async(self, coro):
        """Run an async coroutine in a background thread"""
        def start_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
            
        # Start the event loop thread if not running
        if self.ai_thread is None or not self.ai_thread.is_alive():
            self.ai_thread = threading.Thread(target=start_loop, daemon=True)
            self.ai_thread.start()
        
        # Schedule the coroutine and return the future
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        self.running_tasks.append(future)
        return future
    def setup_ui(self):
        """Initialize main UI components"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.configure('AI.TButton', background='#4CAF50', foreground='white')

    def show_ai_options(self):
        """Show AI quiz options screen"""
        self.clear_frame()
        
        ttk.Label(
            self.main_frame,
            text="AI Quiz Generator",
            font=('Helvetica', 20)
        ).pack(pady=20)
        
        # Topic Entry
        ttk.Label(self.main_frame, text="Enter Topic:").pack()
        self.ai_topic_entry = ttk.Entry(self.main_frame, width=30)
        self.ai_topic_entry.pack(pady=5)
        
        # Question Count
        ttk.Label(self.main_frame, text="Number of Questions:").pack()
        self.ai_count_var = tk.IntVar(value=10)
        ttk.Spinbox(self.main_frame, from_=5, to=20, textvariable=self.ai_count_var).pack(pady=5)
        
        # Generate Button - Now properly connected
        ttk.Button(
            self.main_frame,
            text="Generate Quiz",
            command=self.start_ai_quiz_wrapper,  # Changed to wrapper function
            style='AI.TButton'
        ).pack(pady=20)
        
        # Back Button
        ttk.Button(
            self.main_frame,
            text="Back",
            command=self.show_category_selection
        ).pack(pady=10)
    def start_ai_quiz_wrapper(self):
        """Wrapper function to start AI quiz generation"""
        topic = self.ai_topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("Error", "Please enter a topic!")
            return
            
        count = self.ai_count_var.get()
        
        # Show loading screen
        self.clear_frame()
        ttk.Label(
            self.main_frame,
            text="Generating questions...",
            font=('Helvetica', 16)
        ).pack(pady=50)
        self.root.update()
        
        # Run the async task in background
        self.run_async(self.async_start_ai_quiz(topic, count))

    async def async_start_ai_quiz(self, topic, count):
        """The actual async quiz starter"""
        try:
            success = await self.engine.generate_ai_quiz(topic, count)
            if success:
                # Schedule UI update on main thread
                self.root.after(0, self.show_question)
            else:
                self.root.after(0, lambda: (
                    messagebox.showerror("Error", "Failed to generate questions"),
                    self.show_category_selection()
                ))
        except Exception as e:
            self.root.after(0, lambda: (
                messagebox.showerror("Error", f"AI Error: {str(e)}"),
                self.show_category_selection()
            ))
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

            ttk.Button(
            self.main_frame,
            text="AI Generated Quiz",
            command=self.show_ai_options,
            style='AI.TButton'
        ).pack(pady=20)
            
            
    def show_ai_options(self):
        """Show AI quiz options"""
        self.clear_frame()
        
        ttk.Label(
            self.main_frame,
            text="AI Quiz Generator",
            font=('Helvetica', 20)
        ).pack(pady=20)
        
        # Topic Entry
        ttk.Label(self.main_frame, text="Enter Topic:").pack()
        self.ai_topic_entry = ttk.Entry(self.main_frame, width=30)
        self.ai_topic_entry.pack(pady=5)
        
        # Question Count
        ttk.Label(self.main_frame, text="Number of Questions:").pack()
        self.ai_count_var = tk.IntVar(value=10)
        ttk.Spinbox(self.main_frame, from_=5, to=20, textvariable=self.ai_count_var).pack(pady=5)
        
        # Generate Button
        ttk.Button(
            self.main_frame,
            text="Generate Quiz",
            command=lambda: asyncio.create_task(self.start_ai_quiz()),
            style='AI.TButton'
        ).pack(pady=20)
        
        # Back Button
        ttk.Button(
            self.main_frame,
            text="Back",
            command=self.show_category_selection
        ).pack(pady=10)

    async def start_ai_quiz(self):
        """Start AI-generated quiz"""
        topic = self.ai_topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("Error", "Please enter a topic!")
            return
            
        count = self.ai_count_var.get()
        
        # Show loading
        self.clear_frame()
        ttk.Label(
            self.main_frame,
            text="Generating questions...",
            font=('Helvetica', 16)
        ).pack(pady=50)
        self.root.update()
        
        # Generate questions
        success = await self.engine.generate_ai_quiz(topic, count)
        
        if success:
            self.show_question()
        else:
            messagebox.showerror("Error", "Failed to generate questions")
            self.show_category_selection()
        def on_ai_generate_clicked(self):
               """Handle AI generate button click"""
        topic = self.ai_topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("Error", "Please enter a topic!")
            return
            
        count = self.ai_count_var.get()
        
        # Show loading
        self.clear_frame()
        ttk.Label(
            self.main_frame,
            text="Generating questions...",
            font=('Helvetica', 16)
        ).pack(pady=50)
        self.root.update()
        
        # Run the async task in background
        self.run_async(self.start_ai_quiz(topic, count))


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
