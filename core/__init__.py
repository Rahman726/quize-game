"""
Quiz Game Core Module

Exposes the main functionality for the quiz game application.
"""

from .quiz_engine import QuizEngine
from .ai_integration import AIIntegration

# Version of the core module
__version__ = "1.0.0"

# API exports
__all__ = [
    'QuizEngine',
    'AIIntegration',
    '__version__'
]

# Package initialization
def init_core():
    """Initialize core module components"""
    # Any core module initialization logic goes here
    pass