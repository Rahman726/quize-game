
import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import json
import os
import asyncio

class Difficulty:
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    expert = "expert"

class ColorfulQuizGame:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered Quiz Game")
        self.root.geometry("900x700")
        self.root.configure(bg="#2c3e50")
        
        # Configure Gemini AI
        self.configure_gemini()
        
        # Color scheme
        self.colors = {
            "background": "#2c3e50",
            "primary": "#3498db",
            "secondary": "#2980b9",
            "accent": "#e74c3c",
            "success": "#2ecc71",
            "warning": "#deb676",
            "text": "#ff6309",
            "button_text": "#ffffff",
            "card_bg": "#5e3434"
        }
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.configure_styles()
        
        # Game variables
        self.score = 0
        self.current_question = 0
        self.time_left = 15
        self.timer_running = False
        self.selected_category = None
        self.player_name = ""
        self.questions = []
        self.ai_generated_questions = []
        self.use_ai = False  # Flag to toggle AI questions
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Load questions
        self.load_questions()
        
        # Show welcome screen
        self.show_welcome_screen()
    
    def configure_gemini(self):
        """Configure Gemini AI with API key"""
        try:
            # Replace with your actual API key
            api_key="YOUR_API_KEY"
            self.gemini_model =('gemini-pro')
        except Exception as e:
            messagebox.showerror("AI Error", f"Failed to initialize Gemini AI: {str(e)}")
            self.gemini_model = None
    
    def configure_styles(self):
        """Configure all widget styles"""
        self.style.configure("TFrame", background=self.colors["background"])
        self.style.configure("TLabel", background=self.colors["background"], 
                           foreground=self.colors["text"], font=("Helvetica", 12))
        self.style.configure("Title.TLabel", background=self.colors["background"], 
                           foreground=self.colors["primary"], font=("Helvetica", 24, "bold"))
        self.style.configure("Question.TLabel", background=self.colors["card_bg"], 
                           foreground=self.colors["text"], font=("Helvetica", 14), 
                           wraplength=700, padding=10)
        self.style.configure("Score.TLabel", background=self.colors["background"], 
                           foreground=self.colors["success"], font=("Helvetica", 14, "bold"))
        self.style.configure("Timer.TLabel", background=self.colors["background"], 
                           foreground=self.colors["accent"], font=("Helvetica", 14, "bold"))
        
        # Button styles
        self.style.configure("Primary.TButton", background=self.colors["primary"], 
                           foreground=self.colors["button_text"], font=("Helvetica", 12), 
                           padding=10, borderwidth=0)
        self.style.map("Primary.TButton",
                      background=[('pressed', self.colors["secondary"]), 
                                ('active', self.colors["secondary"])])
        
        self.style.configure("Success.TButton", background=self.colors["success"], 
                           foreground=self.colors["button_text"], font=("Helvetica", 12), 
                           padding=10, borderwidth=0)
        self.style.map("Success.TButton",
                      background=[('pressed', '#27ae60'), 
                                ('active', '#27ae60')])
        
        self.style.configure("Danger.TButton", background=self.colors["accent"], 
                           foreground=self.colors["button_text"], font=("Helvetica", 12), 
                           padding=10, borderwidth=0)
        self.style.map("Danger.TButton",
                      background=[('pressed', '#c0392b'), 
                                ('active', '#c0392b')])
        
        self.style.configure("AI.TButton", background="#9b59b6", 
                           foreground=self.colors["button_text"], font=("Helvetica", 12), 
                           padding=10, borderwidth=0)
        self.style.map("AI.TButton",
                      background=[('pressed', '#8e44ad'), 
                                ('active', '#8e44ad')])
    
    def load_questions(self):
        """Load questions from a JSON file or use default if file doesn't exist"""
        try:
            with open('quiz_questions.json', 'r') as f:
                question_data = json.load(f)
                # Flatten questions into single list with category and difficulty
                self.questions = []
                for category, difficulties in question_data.items():
                    for difficulty_level, qs in difficulties.items():
                        for q in qs:
                            q['category'] = category
                            q['difficulty'] = difficulty_level
                            self.questions.append(q)
        except (FileNotFoundError, json.JSONDecodeError):
            # Default questions
            default_questions = {
                "Pakistan": {
                    "Easy": [
                        {"question": "Capital of Pakistan?", "options": ["Karachi", "Lahore", "Islamabad", "Peshawar"], "answer": 2},
                        {"question": "Pakistan's Independence Day?", "options": ["14 August", "23 March", "6 September", "25 December"], "answer": 0},
                        {"question": "Pakistan's national language?", "options": ["Punjabi", "Urdu", "Sindhi", "English"], "answer": 1},
                        {"question": "Pakistan's national sport?", "options": ["Cricket", "Hockey", "Football", "Squash"], "answer": 1},
                        {"question": "Pakistan's national flower?", "options": ["Rose", "Jasmine", "Lotus", "Tulip"], "answer": 1},
                        {"question": "Pakistan's currency?", "options": ["Rupee", "Dinar", "Taka", "Rial"], "answer": 0},
                        {"question": "Founder of Pakistan?", "options": ["Allama Iqbal", "Liaquat Ali", "Quaid-e-Azam", "Ayub Khan"], "answer": 2}
                    ],
                    "Medium": [
                        {"question": "Pakistan's first female PM?", "options": ["Fatima Jinnah", "Benazir Bhutto", "Hina Rabbani", "Maryam Nawaz"], "answer": 1},
                        {"question": "Pakistan's national animal?", "options": ["Lion", "Markhor", "Snow Leopard", "Deer"], "answer": 1},
                        {"question": "Pakistan's largest dam?", "options": ["Mangla", "Tarbela", "Warsak", "Diamer-Bhasha"], "answer": 1},
                        {"question": "Pakistan's first capital?", "options": ["Karachi", "Lahore", "Rawalpindi", "Islamabad"], "answer": 0},
                        {"question": "Pakistan's national bird?", "options": ["Eagle", "Hawk", "Chakor", "Pigeon"], "answer": 2},
                        {"question": "Pakistan's largest desert?", "options": ["Thar", "Cholistan", "Thal", "Kharan"], "answer": 1},
                        {"question": "Pakistan's first constitution?", "options": ["1947", "1956", "1962", "1973"], "answer": 1}
                    ],
                    "Hard": [
                        {"question": "Pakistan's first Nobel winner?", "options": ["Abdus Salam", "Malala", "Imran Khan", "Benazir Bhutto"], "answer": 0},
                        {"question": "Pakistan's first satellite?", "options": ["Badr-I", "Paksat", "Suparco-I", "Space-III"], "answer": 0},
                        {"question": "Pakistan's first nuclear test?", "options": ["1974", "1998", "2002", "1988"], "answer": 1},
                        {"question": "Pakistan's first female judge?", "options": ["Majida Rizvi", "Asma Jahangir", "Hina Jillani", "Nasira Iqbal"], "answer": 0},
                        {"question": "Pakistan's first female bank CEO?", "options": ["Shamshad Akhtar", "Atiya Zaidi", "Rukhsana Bangash", "Simone Kamil"], "answer": 0},
                        {"question": "Pakistan's first Oscar winner?", "options": ["Shoaib Mansoor", "Sharmeen Obaid", "Mehreen Jabbar", "Sabiha Sumar"], "answer": 1}
                    ]
                },
                "General": {
                    "Easy": [
                        {"question": "Capital of France?", "options": ["London", "Paris", "Berlin", "Madrid"], "answer": 1},
                        {"question": "2 + 2 = ?", "options": ["3", "4", "5", "6"], "answer": 1},
                        {"question": "Colors in rainbow?", "options": ["5", "6", "7", "8"], "answer": 2},
                        {"question": "Largest planet?", "options": ["Earth", "Mars", "Jupiter", "Saturn"], "answer": 2},
                        {"question": "Baby dog called?", "options": ["Cub", "Puppy", "Kitten", "Calf"], "answer": 1},
                        {"question": "Longest river?", "options": ["Amazon", "Nile", "Yangtze", "Mississippi"], "answer": 1},
                        {"question": "Which is not a fruit?", "options": ["Apple", "Carrot", "Banana", "Orange"], "answer": 1}
                    ],
                    "Medium": [
                        {"question": "Chemical symbol for Gold?", "options": ["Go", "Gd", "Au", "Ag"], "answer": 2},
                        {"question": "Who painted Mona Lisa?", "options": ["Van Gogh", "Picasso", "Da Vinci", "Michelangelo"], "answer": 2},
                        {"question": "Land of Rising Sun?", "options": ["China", "Thailand", "Japan", "South Korea"], "answer": 2},
                        {"question": "Largest mammal?", "options": ["Elephant", "Giraffe", "Blue Whale", "Hippo"], "answer": 2},
                        {"question": "What is H2O?", "options": ["Gold", "Salt", "Water", "Oxygen"], "answer": 2},
                        {"question": "Planet with rings?", "options": ["Jupiter", "Saturn", "Uranus", "Neptune"], "answer": 1},
                        {"question": "First element?", "options": ["Helium", "Hydrogen", "Oxygen", "Carbon"], "answer": 1}
                    ],
                    "Hard": [
                        {"question": "Inventor of telephone?", "options": ["Edison", "Bell", "Tesla", "Marconi"], "answer": 1},
                        {"question": "Hardest natural substance?", "options": ["Gold", "Iron", "Diamond", "Platinum"], "answer": 2},
                        {"question": "Year WWII ended?", "options": ["1943", "1945", "1947", "1950"], "answer": 1},
                        {"question": "Element with atomic number 79?", "options": ["Silver", "Platinum", "Gold", "Mercury"], "answer": 2},
                        {"question": "Planet with most moons?", "options": ["Jupiter", "Saturn", "Uranus", "Neptune"], "answer": 0},
                        {"question": "Who wrote Romeo and Juliet?", "options": ["Dickens", "Twain", "Shakespeare", "Austen"], "answer": 2}
                    ]
                }
            }
            
            # Load default questions with proper structure
            self.questions = []
            for category, difficulties in default_questions.items():
                for difficulty_level, qs in difficulties.items():
                    for q in qs:
                        q['category'] = category
                        q['difficulty'] = difficulty_level
                        self.questions.append(q)
    
    async def generate_ai_questions(self, topic, count=5):
        """Generate quiz questions using Gemini AI"""
        if not self.gemini_model:
            messagebox.showwarning("AI Disabled", "Gemini AI is not available. Using default questions.")
            return []
        
        try:
            prompt = f"""
            Generate {count} multiple-choice quiz questions about {topic}.
            Each question should have 4 options and indicate the correct answer.
            Format each question as JSON like this:
            {{
                "question": "question text",
                "options": ["option1", "option2", "option3", "option4"],
                "answer": index_of_correct_answer,
                "difficulty": "Easy/Medium/Hard"
            }}
            Return only the JSON array of questions.
            """
            
            response = await self.gemini_model.generate_content_async(prompt)
            questions = json.loads(response.text)
            for q in questions:
                q['category'] = topic
                q['ai_generated'] = True
            return questions
        except Exception as e:
            messagebox.showerror("AI Error", f"Failed to generate questions: {str(e)}")
            return []
    
    def clear_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def create_color_blocks(self):
        """Create decorative color blocks at the bottom"""
        color_frame = ttk.Frame(self.main_frame)
        color_frame.pack(side=tk.BOTTOM, pady=20)
        
        colors = [self.colors["primary"], self.colors["success"], 
                self.colors["accent"], self.colors["warning"]]
        
        for color in colors:
            block = tk.Canvas(color_frame, width=50, height=10, bg=color, 
                             highlightthickness=0)
            block.pack(side=tk.LEFT, padx=5)
    
    def show_welcome_screen(self):
        """Display the welcome screen with player name input"""
        self.clear_frame()
        
        # Title
        title_label = ttk.Label(self.main_frame, text="AI Quiz Game", 
                              style="Title.TLabel")
        title_label.pack(pady=(20, 40))
        
        # Player name input
        name_frame = ttk.Frame(self.main_frame)
        name_frame.pack(pady=10)
        
        ttk.Label(name_frame, text="Enter your name:", 
                 font=("Helvetica", 14)).pack(side=tk.LEFT, padx=5)
        
        self.name_entry = ttk.Entry(name_frame, font=("Helvetica", 14), width=25)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        # Start button
        start_button = ttk.Button(self.main_frame, text="Start Game", 
                                 style="Primary.TButton", 
                                 command=self.start_game)
        start_button.pack(pady=20, ipadx=20, ipady=10)
        
        # Decorative elements
        self.create_color_blocks()
    
    def start_game(self):
        """Start the game after getting player name"""
        self.player_name = self.name_entry.get().strip()
        if not self.player_name:
            messagebox.showwarning("Missing Name", "Please enter your name to continue!")
            return
        
        self.show_category_selection()
    
    def show_category_selection(self):
        """Show category selection screen with AI option"""
        self.clear_frame()
        
        # Title
        title_label = ttk.Label(self.main_frame, 
                               text=f"Welcome, {self.player_name}!\nChoose a category:", 
                               style="Title.TLabel")
        title_label.pack(pady=(20, 40))
        
        # Category buttons
        categories_frame = ttk.Frame(self.main_frame)
        categories_frame.pack(pady=20)
        
        pakistan_button = ttk.Button(categories_frame, text="Pakistan Quiz", 
                                   style="Primary.TButton",
                                   command=lambda: self.select_category("Pakistan"))
        pakistan_button.grid(row=0, column=0, padx=20, pady=10, ipadx=20, ipady=15)
        
        general_button = ttk.Button(categories_frame, text="General Knowledge", 
                                  style="Success.TButton",
                                  command=lambda: self.select_category("General"))
        general_button.grid(row=0, column=1, padx=20, pady=10, ipadx=20, ipady=15)
        
        # AI Button
        ai_button = ttk.Button(categories_frame, text="AI Generated Quiz", 
                             style="AI.TButton",
                             command=self.show_ai_options)
        ai_button.grid(row=1, column=0, columnspan=2, pady=10, ipadx=20, ipady=15)
        
        # Back button
        back_button = ttk.Button(self.main_frame, text="Back", 
                               style="Danger.TButton",
                               command=self.show_welcome_screen)
        back_button.pack(pady=20, ipadx=20, ipady=5)
    
    def show_ai_options(self):
        """Show options for AI-generated quiz"""
        self.clear_frame()
        
        # Title
        title_label = ttk.Label(self.main_frame, 
                               text="AI Quiz Generator", 
                               style="Title.TLabel")
        title_label.pack(pady=(20, 40))
        
        # Topic input
        topic_frame = ttk.Frame(self.main_frame)
        topic_frame.pack(pady=10)
        
        ttk.Label(topic_frame, text="Enter quiz topic:", 
                 font=("Helvetica", 14)).pack(side=tk.LEFT, padx=5)
        
        self.topic_entry = ttk.Entry(topic_frame, font=("Helvetica", 14), width=25)
        self.topic_entry.pack(side=tk.LEFT, padx=5)
        
        # Question count
        count_frame = ttk.Frame(self.main_frame)
        count_frame.pack(pady=10)
        
        ttk.Label(count_frame, text="Number of questions:", 
                 font=("Helvetica", 14)).pack(side=tk.LEFT, padx=5)
        
        self.count_var = tk.IntVar(value=10)
        count_spin = ttk.Spinbox(count_frame, from_=5, to=20, textvariable=self.count_var, 
                                font=("Helvetica", 14), width=5)
        count_spin.pack(side=tk.LEFT, padx=5)
        
        # Generate button
        generate_button = ttk.Button(self.main_frame, text="Generate Quiz", 
                                   style="AI.TButton",
                                   command=self.generate_ai_quiz)
        generate_button.pack(pady=20, ipadx=20, ipady=10)
        
        # Back button
        back_button = ttk.Button(self.main_frame, text="Back", 
                               style="Danger.TButton",
                               command=self.show_category_selection)
        back_button.pack(pady=10, ipadx=20, ipady=5)
    
    def generate_ai_quiz(self):
        """Generate and start an AI quiz"""
        topic = self.topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("Missing Topic", "Please enter a quiz topic!")
            return
        
        count = self.count_var.get()
        
        # Show loading message
        loading = ttk.Label(self.main_frame, text="Generating questions with AI...", 
                          style="Title.TLabel")
        loading.pack(pady=50)
        self.root.update()
        
        # Generate questions asynchronously
        self.ai_generated_questions = asyncio.run(self.generate_ai_questions(topic, count))
        
        if not self.ai_generated_questions:
            messagebox.showerror("AI Error", "Failed to generate questions. Using default questions.")
            self.filtered_questions = self.questions[:count] if self.questions else []
        else:
            self.filtered_questions = self.ai_generated_questions
        
        if not self.filtered_questions:
            messagebox.showerror("No Questions", "No questions available for this topic.")
            return
        
        self.use_ai = True
        self.selected_category = f"AI: {topic}"
        self.score = 0
        self.current_question = 0
        random.shuffle(self.filtered_questions)
        self.show_question()
    
    def select_category(self, category):
        """Select a quiz category and start the game"""
        self.use_ai = False
        self.selected_category = category
        self.score = 0
        self.current_question = 0
        
        # Filter questions by selected category
        self.filtered_questions = [q for q in self.questions 
                                 if q["category"] == category]
        
        if not self.filtered_questions:
            messagebox.showerror("Error", f"No questions found for category: {category}")
            return
        
        random.shuffle(self.filtered_questions)
        self.show_question()
    
    def show_question(self):
        """Display the current question"""
        self.clear_frame()
        
        if self.current_question >= len(self.filtered_questions):
            self.show_results()
            return
        
        question_data = self.filtered_questions[self.current_question]
        
        # Header with score and timer
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        score_label = ttk.Label(header_frame, text=f"Score: {self.score}", 
                              style="Score.TLabel")
        score_label.pack(side=tk.LEFT)
        
        self.timer_label = ttk.Label(header_frame, text=f"Time: {self.time_left}", 
                                   style="Timer.TLabel")
        self.timer_label.pack(side=tk.RIGHT)
        
        # Question card
        card_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        card_frame.pack(fill=tk.X, pady=10, padx=10)
        
        difficulty_label = ttk.Label(card_frame, 
                                   text=f"Difficulty: {question_data['difficulty']}", 
                                   font=("Helvetica", 12, "italic"),
                                   foreground=self.get_difficulty_color(question_data['difficulty']))
        difficulty_label.pack(anchor=tk.W, pady=(10, 0))
        
        question_label = ttk.Label(card_frame, text=question_data["question"], 
                                 style="Question.TLabel")
        question_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Options
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.option_buttons = []
        for i, option in enumerate(question_data["options"]):
            btn = ttk.Button(options_frame, text=option, style="Primary.TButton",
                            command=lambda i=i: self.check_answer(i))
            btn.pack(fill=tk.X, pady=5, ipady=10)
            self.option_buttons.append(btn)
        
        # Start timer
        self.time_left = 15
        self.timer_running = True
        self.update_timer()
    
    def get_difficulty_color(self, difficulty):
        """Return color based on question difficulty"""
        colors = {
            "Easy": "#2ecc71",  # Green
            "Medium": "#f39c12",  # Orange
            "Hard": "#e74c3c"  # Red
        }
        return colors.get(difficulty, "#3498db")
    
    def update_timer(self):
        """Update the timer display"""
        if self.time_left > 0 and self.timer_running:
            self.timer_label.config(text=f"Time: {self.time_left}")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0 and self.timer_running:
            self.timer_running = False
            messagebox.showinfo("Time's Up!", "You ran out of time!")
            self.current_question += 1
            self.show_question()
    
    def check_answer(self, choice):
        """Check if the selected answer is correct"""
        self.timer_running = False
        question_data = self.filtered_questions[self.current_question]
        correct_answer = question_data["options"][question_data["answer"]]
        selected_option = question_data["options"][choice]
        
        # Highlight the selected button
        self.option_buttons[choice].configure(style="Danger.TButton")
        
        # Find and highlight the correct answer
        for i, option in enumerate(question_data["options"]):
            if option == correct_answer:
                self.option_buttons[i].configure(style="Success.TButton")
                break
        
        if selected_option == correct_answer:
            self.score += 1
            feedback = "Correct! Well done!"
        else:
            feedback = f"Incorrect! The correct answer was: {correct_answer}"
        
        # Show feedback and proceed after a delay
        self.root.after(1500, lambda: self.process_answer_feedback(selected_option == correct_answer))
    
    def process_answer_feedback(self, was_correct):
        """Process the answer feedback and move to next question"""
        self.current_question += 1
        self.show_question()
    
    def show_results(self):
        """Show the final results screen"""
        self.clear_frame()
        
        # Title
        title_label = ttk.Label(self.main_frame, 
                              text="Quiz Completed!", 
                              style="Title.TLabel")
        title_label.pack(pady=(40, 20))
        
        # Calculate percentage safely
        try:
            percentage = (self.score/len(self.filtered_questions))*100 if self.filtered_questions else 0
        except ZeroDivisionError:
            percentage = 0
        
        # Results card
        card_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        card_frame.pack(fill=tk.X, pady=20, padx=50)
        
        result_text = (f"Player: {self.player_name}\n\n"
                      f"Category: {self.selected_category}\n\n"
                      f"Final Score: {self.score}/{len(self.filtered_questions)}\n\n"
                      f"Percentage: {percentage:.1f}%")
        
        result_label = ttk.Label(card_frame, text=result_text, 
                               style="Question.TLabel",
                               font=("Helvetica", 16))
        result_label.pack(pady=30, padx=30)
        
        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        retry_button = ttk.Button(button_frame, text="Try Again", 
                                style="Primary.TButton",
                                command=lambda: self.select_category(self.selected_category))
        retry_button.grid(row=0, column=0, padx=10, ipadx=20, ipady=10)
        
        new_category_button = ttk.Button(button_frame, text="New Category", 
                                       style="Success.TButton",
                                       command=self.show_category_selection)
        new_category_button.grid(row=0, column=1, padx=10, ipadx=20, ipady=10)
        
        quit_button = ttk.Button(button_frame, text="Quit", 
                               style="Danger.TButton",
                               command=self.root.quit)
        quit_button.grid(row=0, column=2, padx=10, ipadx=20, ipady=10)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ColorfulQuizGame(root)
    root.mainloop()