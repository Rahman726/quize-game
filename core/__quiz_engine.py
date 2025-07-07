import random
import json
from constants.questions import DEFAULT_QUESTIONS

class QuizEngine:
    def __init__(self):
        self.questions = []
        self.filtered_questions = []
        self.current_question = 0
        self.score = 0
        self.load_questions()

    def load_questions(self):
        try:
            with open('quiz_questions.json', 'r') as f:
                question_data = json.load(f)
                self._process_questions(question_data)
        except (FileNotFoundError, json.JSONDecodeError):
            self._process_questions(DEFAULT_QUESTIONS)

    def _process_questions(self, question_data):
        self.questions = []
        for category, difficulties in question_data.items():
            for difficulty_level, qs in difficulties.items():
                for q in qs:
                    q['category'] = category
                    q['difficulty'] = difficulty_level
                    self.questions.append(q)

    # ... rest of the QuizEngine methods