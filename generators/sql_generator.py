"""
SQL Answer File Generator

Creates an Answers.sql file from the loaded questions.
"""

from pathlib import Path

from config import OUTPUT_DIR
from models.question import Question


class SQLGenerator:
    """Generates a SQL file containing all answer queries."""

    def __init__(self, questions: list[Question]) -> None:
        self.questions = questions
        self.output_file = OUTPUT_DIR / "Answers.sql"

    def generate(self) -> Path:
        """Generate the Answers.sql file."""

        with open(self.output_file, "w", encoding="utf-8") as file:

            file.write("-- ==========================================\n")
            file.write("-- SQL Workbook - Answer Queries\n")
            file.write("-- ==========================================\n\n")

            for question in self.questions:

                file.write(f"-- Question {question.id}\n")
                file.write(f"-- Topic: {question.topic}\n")
                file.write(f"-- Difficulty: {question.difficulty}\n\n")

                sql = question.answer.strip()

                file.write(sql)

                if not sql.endswith(";"):
                    file.write(";")

                file.write("\n\n-- ------------------------------------------\n\n")

        return self.output_file
