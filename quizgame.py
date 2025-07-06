import random

def generate_ai_question(category):
    # This would connect to an AI API in a real implementation
    # For now, we'll use placeholder data
    questions = {
        "science": [
            {"question": "What is the chemical symbol for gold?", "options": ["Go", "Gd", "Au", "Ag"], "answer": 2},
            {"question": "How many planets are in our solar system?", "options": ["7", "8", "9", "10"], "answer": 1}
        ],
        "history": [
            {"question": "In what year did WWII end?", "options": ["1943", "1945", "1947", "1950"], "answer": 1},
            {"question": "Who was the first US president?", "options": ["Washington", "Jefferson", "Adams", "Lincoln"], "answer": 0}
        ]
    }
    return random.choice(questions[category])

def play_quiz():
    score = 0
    category = input("Choose category (science/history): ").lower()
    num_questions = int(input("How many questions? "))
    
    for _ in range(num_questions):
        q = generate_ai_question(category)
        print("\n" + q["question"])
        for i, option in enumerate(q["options"]):
            print(f"{i+1}. {option}")
        
        answer = int(input("Your answer (1-4): ")) - 1
        if answer == q["answer"]:
            print("Correct!")
            score += 1
        else:
            print(f"Wrong! The correct answer was: {q['options'][q['answer']]}")
    
    print(f"\nYour final score: {score}/{num_questions}")

play_quiz()