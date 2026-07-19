"""
Format Generator - Generates questions with specific formatting
"""

from typing import List
from models.table import Table
from models.question import Question


class FormatQuestionGenerator:
    """Generates SQL questions with specific format."""
    
    def __init__(self, tables: List[Table]):
        self.tables = tables
        self.questions = []
        self.counter = 0
    
    def generate_all(self, count: int = 100) -> List[Question]:
        """Generate questions."""
        # Use the basic generator
        from question_generator.generator import QuestionGenerator
        basic_gen = QuestionGenerator(self.tables)
        self.questions = basic_gen.generate_all()
        
        # Limit to count if needed
        if len(self.questions) > count:
            self.questions = self.questions[:count]
        
        # Reassign IDs
        for i, q in enumerate(self.questions, 1):
            q.id = i
        
        return self.questions
    
    def _add_question(self, topic: str, difficulty: str, question: str,
                      answer: str, explanation: str, tip: str):
        """Add a question."""
        self.counter += 1
        self.questions.append(
            Question(
                id=self.counter,
                topic=topic,
                difficulty=difficulty,
                question=question,
                answer=answer,
                explanation=explanation,
                tip=tip
            )
        )
