import tkinter as tk
from tkinter import ttk, messagebox
from core.quiz_engine import QuizEngine

class QuizApp:
    # ... existing code ...
    
    def show_ai_options(self):
        """Show AI quiz generation screen"""
        self.clear_frame()
        
        ttk.Label(self.main_frame, 
                text="AI Quiz Generator",
                style="Title.TLabel").pack(pady=20)
        
        # Topic Entry
        ttk.Label(self.main_frame, text="Enter Topic:").pack()
        self.ai_topic_entry = ttk.Entry(self.main_frame, width=30)
        self.ai_topic_entry.pack(pady=5)
        
        # Question Count
        ttk.Label(self.main_frame, text="Number of Questions:").pack()
        self.ai_count_var = tk.IntVar(value=10)
        ttk.Spinbox(self.main_frame, from_=5, to=20, 
                   textvariable=self.ai_count_var).pack(pady=5)
        
        # Generate Button
        ttk.Button(self.main_frame, 
                 text="Generate Quiz",
                 command=self.start_ai_quiz).pack(pady=20)

    async def start_ai_quiz(self):
        """Start an AI-generated quiz"""
        topic = self.ai_topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("Error", "Please enter a topic!")
            return
            
        self.show_loading_screen("Generating questions...")
        
        count = self.ai_count_var.get()
        success = await self.engine.generate_ai_quiz(topic, count)
        
        if success:
            self.show_question()
        else:
            self.show_category_selection()