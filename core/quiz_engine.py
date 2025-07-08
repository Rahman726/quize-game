import random
import json
from constants import (
    DIFFICULTY_COLORS,
    DEFAULT_QUESTIONS,
    Difficulty
)
from core.ai_integration import AIIntegration

class QuizEngine:
    def __init__(self):
        self.questions = []
        self.filtered_questions = []
        self.current_question_index = 0
        self.score = 0
        self.time_left = 15
        self.timer_running = False
        self.ai = AIIntegration()
        self.load_questions()

    def load_questions(self):
        """Load questions from JSON file or use defaults"""
        try:
            with open('quiz_questions.json', 'r') as f:
                question_data = json.load(f)
                self._process_questions(question_data)
        except (FileNotFoundError, json.JSONDecodeError):
            self._process_questions(DEFAULT_QUESTIONS)

    def _process_questions(self, question_data):
        """Process raw question data into standardized format"""
        self.questions = []
        for category, difficulties in question_data.items():
            for difficulty_level, qs in difficulties.items():
                for q in qs:
                    q['category'] = category
                    q['difficulty'] = difficulty_level
                    q['difficulty_color'] = DIFFICULTY_COLORS.get(difficulty_level, "#3498db")
                    self.questions.append(q)

    def get_categories(self):
        """Return list of available categories with question counts"""
        categories = {}
        for question in self.questions:
            if question['category'] not in categories:
                categories[question['category']] = 0
            categories[question['category']] += 1
        return categories

    def start_quiz(self, category, difficulty=None):
        """Initialize quiz with filtered questions"""
        self.filtered_questions = [
            q for q in self.questions 
            if q['category'] == category and 
            (difficulty is None or q['difficulty'] == difficulty)
        ]
        random.shuffle(self.filtered_questions)
        self.current_question_index = 0
        self.score = 0
        self.time_left = 15
        return len(self.filtered_questions)

    # ... [Include all other methods from previous implementation]