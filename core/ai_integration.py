import google.generativeai as genai
import json
import asyncio
from tkinter import messagebox
from constants.difficulty import Difficulty

class AIIntegration:
    def __init__(self):
        self.model = None
        self.configure_gemini()
        self.max_retries = 3
        self.timeout = 30  # seconds

    def configure_gemini(self):
        """Configure the Gemini AI API with proper error handling"""
        try:
            # Replace with your actual API key
            genai.configure(api_key="AIzaSyAyoNcqDldQLlTuMbcQYcPYzcAj55to9VA")
            
            # Initialize model with safety settings
            self.model = genai.GenerativeModel(
                'gemini-pro',
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000,
                    "top_p": 0.9
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )
        except Exception as e:
            messagebox.showerror(
                "AI Configuration Error",
                f"Failed to initialize Gemini AI:\n{str(e)}\n\n"
                "Please check your API key and internet connection."
            )
            self.model = None

    async def generate_quiz_questions(self, topic: str, count: int = 5, 
                                    difficulty: str = None) -> list:
        """
        Generate quiz questions using AI with retry logic
        
        Args:
            topic: The quiz topic (e.g. "Pakistan History")
            count: Number of questions to generate (1-20)
            difficulty: Optional difficulty level (Easy/Medium/Hard/Expert)
        
        Returns:
            List of question dictionaries or None if failed
        """
        if not self.model:
            messagebox.showwarning(
                "AI Disabled",
                "Gemini AI is not available. Using default questions."
            )
            return None

        # Validate input
        count = max(1, min(20, count))  # Clamp between 1-20
        
        for attempt in range(self.max_retries):
            try:
                prompt = self._build_prompt(topic, count, difficulty)
                response = await asyncio.wait_for(
                    self.model.generate_content_async(prompt),
                    timeout=self.timeout
                )
                
                questions = self._parse_response(response.text, topic)
                if self._validate_questions(questions, count):
                    return questions
                
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    messagebox.showerror(
                        "AI Timeout",
                        "The AI request timed out. Please try again later."
                    )
            except Exception as e:
                if attempt == self.max_retries - 1:
                    messagebox.showerror(
                        "AI Error",
                        f"Failed to generate questions after {self.max_retries} attempts:\n{str(e)}"
                    )
        
        return None

    def _build_prompt(self, topic: str, count: int, difficulty: str = None) -> str:
        """Construct the AI prompt with clear instructions"""
        base_prompt = f"""
        Generate exactly {count} multiple-choice quiz questions about {topic}.
        Each question must have:
        - A clear, concise question text
        - 4 plausible options (A-D)
        - Correct answer index (0-3)
        - Difficulty level (Easy/Medium/Hard/Expert)
        - Brief explanation (1 sentence)

        Format each question as valid JSON like this:
        {{
            "question": "question text",
            "options": ["A", "B", "C", "D"],
            "answer": 0,
            "difficulty": "Easy",
            "explanation": "Brief explanation"
        }}

        Important:
        - Questions should be factual and verifiable
        - Options should be mutually exclusive
        - Return ONLY the JSON array
        """
        
        if difficulty:
            base_prompt += f"\n- All questions must be {difficulty} difficulty"
        
        return base_prompt.strip()

    def _parse_response(self, response_text: str, topic: str) -> list:
        """Parse and clean the AI response"""
        try:
            # Clean common formatting issues
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:-3].strip()
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:-3].strip()
            
            questions = json.loads(cleaned_text)
            
            # Add metadata
            for q in questions:
                q['category'] = topic
                q['ai_generated'] = True
                if 'difficulty' not in q:
                    q['difficulty'] = "Medium"
            
            return questions
            
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "AI Parse Error",
                f"Failed to parse AI response:\n{str(e)}\n\n"
                f"Response received:\n{response_text[:200]}..."
            )
            return None

    def _validate_questions(self, questions: list, expected_count: int) -> bool:
        """Validate the generated questions meet requirements"""
        if not isinstance(questions, list):
            return False
            
        if len(questions) != expected_count:
            messagebox.showwarning(
                "AI Warning",
                f"Requested {expected_count} questions but got {len(questions)}"
            )
            return False
            
        required_fields = {'question', 'options', 'answer', 'difficulty', 'explanation'}
        for i, q in enumerate(questions):
            if not all(field in q for field in required_fields):
                messagebox.showerror(
                    "AI Validation Error",
                    f"Question {i+1} is missing required fields"
                )
                return False
                
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                messagebox.showerror(
                    "AI Validation Error",
                    f"Question {i+1} must have exactly 4 options"
                )
                return False
                
            if not 0 <= q['answer'] <= 3:
                messagebox.showerror(
                    "AI Validation Error",
                    f"Question {i+1} has invalid answer index {q['answer']}"
                )
                return False
                
        return True

    async def explain_answer(self, question: str, user_answer: str) -> str:
        """Generate explanation for why an answer is correct/incorrect"""
        if not self.model:
            return "AI explanation unavailable"
            
        prompt = f"""
        Given the question:
        {question}
        
        And the user's answer:
        {user_answer}
        
        Provide a concise, 1-2 sentence explanation about whether the answer is correct
        and why. Focus on key facts and avoid lengthy explanations.
        """
        
        try:
            response = await asyncio.wait_for(
                self.model.generate_content_async(prompt),
                timeout=15
            )
            return response.text.strip()
        except Exception as e:
            return f"Could not generate explanation: {str(e)}"