"""
question_generator/generator.py

Basic question generator.
"""

from typing import List
from models.table import Table
from models.question import Question


class QuestionGenerator:
    """Basic SQL question generator."""

    def __init__(self, tables: List[Table]):
        self.tables = tables
        self.questions = []
        self.counter = 0

    def generate_all(self) -> List[Question]:
        """Generate all questions."""
        
        for table in self.tables:
            # SELECT all
            self._add_question(
                topic="SELECT",
                difficulty="Beginner",
                question=f"List all records from the {table.name} table.",
                answer=f"SELECT * FROM {table.name};",
                explanation=f"SELECT * returns every column and row from the {table.name} table.",
                tip="SELECT * is useful for exploration, but in production, specify only needed columns."
            )
            
            # ORDER BY on primary key
            for col in table.columns:
                if col.primary_key:
                    self._add_question(
                        topic="ORDER BY",
                        difficulty="Beginner",
                        question=f"List all {table.name} ordered by {col.name} descending.",
                        answer=f"SELECT * FROM {table.name} ORDER BY {col.name} DESC;",
                        explanation=f"ORDER BY {col.name} DESC sorts from highest to lowest.",
                        tip="DESC shows largest numbers or latest dates first."
                    )
                    break
        
        return self.questions

    def _add_question(self, topic: str, difficulty: str, question: str,
                      answer: str, explanation: str, tip: str):
        """Add a question to the collection."""
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
