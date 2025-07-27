DEFAULT_QUESTIONS = {
    "Pakistan": {
        "Easy": [
            {
                "question": "Which river is called the 'Lifeline of Pakistan'?",
                "options": ["Jhelum", "Chenab", "Indus", "Ravi"],
                "answer": 2,
                "explanation": "The Indus River provides water for 90% of Pakistan's agriculture."
            },
            {
                "question": "Pakistan's first Nobel Prize winner won in which field?",
                "options": ["Chemistry", "Physics", "Peace", "Literature"],
                "answer": 1,
                "explanation": "Dr. Abdus Salam won the 1979 Physics Prize for electroweak unification."
            }
        ],
        "Medium": [
            {
                "question": "The ancient city of Taxila was a center of which civilization?",
                "options": ["Indus Valley", "Gandhara", "Persian", "Mughal"],
                "answer": 1,
                "explanation": "Taxila was a major Gandhara Buddhist center from 1000 BCE–500 CE."
            }
        ],
        "Hard": [
            {
                "question": "Which article of Pakistan's Constitution declares Islam as the state religion?",
                "options": ["Article 1", "Article 2", "Article 31", "Article 227"],
                "answer": 1,
                "explanation": "Article 2 was added in 1985 making Islam the state religion."
            }
        ],
        "Expert": [
            {
                "question": "Pakistan's Space and Upper Atmosphere Research Commission (SUPARCO) was established in which year?",
                "options": ["1947", "1961", "1973", "1985"],
                "answer": 1,
                "explanation": "SUPARCO was founded on 16 September 1961 by Dr. Abdus Salam."
            }
        ]
    },
    "Science": {
        "Easy": [
            {
                "question": "What is the chemical formula for table salt?",
                "options": ["NaCl", "H₂O", "CO₂", "C₆H₁₂O₆"],
                "answer": 0,
                "explanation": "Sodium chloride (NaCl) is common table salt."
            }
        ],
        "Medium": [
            {
                "question": "Which law states 'For every action, there is an equal and opposite reaction'?",
                "options": ["Newton's 1st Law", "Newton's 2nd Law", "Newton's 3rd Law", "Ohm's Law"],
                "answer": 2,
                "explanation": "Newton's Third Law of Motion describes action-reaction pairs."
            }
        ],
        "Hard": [
            {
                "question": "What is the approximate value of Avogadro's number?",
                "options": ["6.02 × 10²³", "3.00 × 10⁸", "1.60 × 10⁻¹⁹", "9.81 × 10⁰"],
                "answer": 0,
                "explanation": "Avogadro's number defines particles in one mole of substance."
            }
        ],
        "Expert": [
            {
                "question": "In quantum mechanics, what does the Schrödinger equation describe?",
                "options": [
                    "Particle trajectories",
                    "Wave function evolution",
                    "Blackbody radiation",
                    "Relativistic effects"
                ],
                "answer": 1,
                "explanation": "The equation describes how quantum systems change over time."
            }
        ]
    },
    "Math": {
        "Easy": [
            {
                "question": "What is the sum of angles in any triangle?",
                "options": ["90°", "180°", "270°", "360°"],
                "answer": 1,
                "explanation": "This is a fundamental property of Euclidean geometry."
            }
        ],
        "Medium": [
            {
                "question": "If 3x - 7 = 14, what is x?",
                "options": ["5", "7", "9", "21"],
                "answer": 1,
                "explanation": "Add 7 to both sides: 3x = 21 → x = 7."
            }
        ],
        "Hard": [
            {
                "question": "What is the derivative of sin(x)?",
                "options": ["cos(x)", "-cos(x)", "tan(x)", "-sin(x)"],
                "answer": 2,
                "explanation": "d/dx[sin(x)] = cos(x) is a basic differentiation rule."
            }
        ],
        "Expert": [
            {
                "question": "Evaluate ∫(2x dx) from 0 to 3",
                "options": ["3", "6", "9", "12"],
                "answer": 2,
                "explanation": "The integral evaluates to x²|₀³ = 9 - 0 = 9."
            }
        ]
    },
    "General Knowledge": {
        "Easy": [
            {
                "question": "Which planet is known as the 'Red Planet'?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "answer": 1,
                "explanation": "Mars appears red due to iron oxide on its surface."
            }
        ],
        "Medium": [
            {
                "question": "What is the largest organ in the human body?",
                "options": ["Liver", "Brain", "Skin", "Lungs"],
                "answer": 2,
                "explanation": "Skin covers about 20 square feet in adults."
            }
        ],
        "Hard": [
            {
                "question": "Which country has the most UNESCO World Heritage Sites?",
                "options": ["China", "France", "Italy", "Spain"],
                "answer": 2,
                "explanation": "Italy has 59 sites as of 2023 (e.g., Colosseum, Venice)."
            }
        ],
        "Expert": [
            {
                "question": "What is the only known moon in our solar system with a substantial atmosphere?",
                "options": ["Europa", "Titan", "Ganymede", "Io"],
                "answer": 1,
                "explanation": "Saturn's moon Titan has a nitrogen-rich atmosphere thicker than Earth's."
            }
        ]
    }
}

__all__ = ['DEFAULT_QUESTIONS']