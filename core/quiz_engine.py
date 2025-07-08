import random
import json
from constants.questions import DEFAULT_QUESTIONS

class QuizEngine:
    def __init__(self):
        self.questions = []
        self.filtered_questions = []
        self.current_question_index = 0
        self.score = 0
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
                    self.questions.append(q)

    def get_categories(self):
        """Return list of all available categories"""
        categories = set()
        for question in self.questions:
            categories.add(question['category'])
        return sorted(list(categories))

    def start_quiz(self, category):
        """Initialize quiz with questions from selected category"""
        self.filtered_questions = [
            q for q in self.questions 
            if q['category'] == category
        ]
        random.shuffle(self.filtered_questions)
        self.current_question_index = 0
        self.score = 0

    def get_current_question(self):
        """Return the current question data"""
        if self.current_question_index < len(self.filtered_questions):
            return self.filtered_questions[self.current_question_index]
        return None

    def check_answer(self, selected_index):
        """
        Check if selected answer is correct
        Returns True if correct, False otherwise
        """
        current_q = self.get_current_question()
        if current_q and selected_index == current_q['answer']:
            self.score += 1
            return True
        return False

    def next_question(self):
        """Advance to the next question in the quiz"""
        if self.has_next_question():
            self.current_question_index += 1
            return True
        return False

    def has_next_question(self):
        """Check if there are more questions remaining"""
        return self.current_question_index + 1 < len(self.filtered_questions)

    def get_results(self):
        """Calculate and return quiz results"""
        total_questions = len(self.filtered_questions)
        percentage = (self.score / total_questions) * 100 if total_questions > 0 else 0
        
        return {
            'score': self.score,
            'total': total_questions,
            'percentage': percentage,
            'category': self.filtered_questions[0]['category'] if total_questions > 0 else ''
        }

    def reset_quiz(self):
        """Reset the quiz state"""
        self.filtered_questions = []
        self.current_question_index = 0
        self.score = 0