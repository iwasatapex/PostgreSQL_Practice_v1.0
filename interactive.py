"""
Interactive SQL Learning System

Provides an interactive CLI for generating and practicing SQL questions.
Users can:
1. Choose how many questions to generate
2. View questions with answers on demand
3. Get explanations and tips
4. Track progress
"""

import os
import sys
import random
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from parser.sql_parser import SQLParser
from parser.python_parser import PythonParser
from question_generator.format_generator import FormatQuestionGenerator
from models.question import Question


class InteractiveSQLLearner:
    """Interactive SQL learning system."""
    
    def __init__(self):
        self.questions: List[Question] = []
        self.current_index = 0
        self.score = 0
        self.attempted = 0
        self.showing_answer = False
        
        # Color codes for terminal
        self.colors = {
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'red': '\033[91m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'underline': '\033[4m',
            'end': '\033[0m'
        }
    
    def print_header(self, text: str, color: str = 'blue'):
        """Print a formatted header."""
        print(f"\n{self.colors[color]}{'=' * 80}{self.colors['end']}")
        print(f"{self.colors['bold']}{self.colors[color]}{text.center(80)}{self.colors['end']}")
        print(f"{self.colors[color]}{'=' * 80}{self.colors['end']}\n")
    
    def print_section(self, text: str, color: str = 'yellow'):
        """Print a section header."""
        print(f"\n{self.colors[color]}─── {text} ───{self.colors['end']}")
    
    def print_success(self, text: str):
        """Print success message."""
        print(f"{self.colors['green']}✅ {text}{self.colors['end']}")
    
    def print_error(self, text: str):
        """Print error message."""
        print(f"{self.colors['red']}❌ {text}{self.colors['end']}")
    
    def print_info(self, text: str):
        """Print info message."""
        print(f"{self.colors['cyan']}ℹ️  {text}{self.colors['end']}")
    
    def print_warning(self, text: str):
        """Print warning message."""
        print(f"{self.colors['yellow']}⚠️  {text}{self.colors['end']}")
    
    def load_questions(self, file_path: str, count: int = 50) -> bool:
        """Load questions from a SQL or Python file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.print_error(f"File not found: {file_path}")
                return False
            
            print(f"\n📄 Loading questions from: {file_path.name}")
            
            # Parse based on extension
            if file_path.suffix.lower() == '.sql':
                parser = SQLParser(file_path)
            elif file_path.suffix.lower() == '.py':
                parser = PythonParser(file_path)
            else:
                self.print_error(f"Unsupported file type: {file_path.suffix}")
                return False
            
            schema = parser.parse()
            
            # Generate questions
            generator = FormatQuestionGenerator(schema)
            self.questions = generator.generate_all(count)
            
            self.print_success(f"Loaded {len(self.questions)} questions")
            return True
            
        except Exception as e:
            self.print_error(f"Error loading questions: {e}")
            return False
    
    def show_menu(self):
        """Show the main menu."""
        self.print_header("📚 SQL Interactive Learning System", 'purple')
        
        print(f"{self.colors['cyan']}Available Commands:{self.colors['end']}")
        print(f"  {self.colors['yellow']}next{self.colors['end']}     - Show next question")
        print(f"  {self.colors['yellow']}answer{self.colors['end']}   - Show answer for current question")
        print(f"  {self.colors['yellow']}hint{self.colors['end']}     - Show a hint")
        print(f"  {self.colors['yellow']}explain{self.colors['end']}  - Show detailed explanation")
        print(f"  {self.colors['yellow']}stats{self.colors['end']}    - Show your progress")
        print(f"  {self.colors['yellow']}random{self.colors['end']}   - Jump to random question")
        print(f"  {self.colors['yellow']}goto N{self.colors['end']}   - Go to question N")
        print(f"  {self.colors['yellow']}reset{self.colors['end']}    - Reset progress")
        print(f"  {self.colors['yellow']}save{self.colors['end']}     - Save answers to file")
        print(f"  {self.colors['yellow']}export{self.colors['end']}   - Export all answers")
        print(f"  {self.colors['yellow']}quit{self.colors['end']}     - Exit\n")
    
    def show_question(self):
        """Display the current question."""
        if not self.questions:
            self.print_error("No questions loaded. Please load a file first.")
            return
        
        q = self.questions[self.current_index]
        stars = {
            'Beginner': '⭐',
            'Intermediate': '⭐⭐',
            'Advanced': '⭐⭐⭐',
            'Expert': '⭐⭐⭐⭐'
        }
        
        self.print_header(f"Question {self.current_index + 1} of {len(self.questions)}", 'blue')
        
        print(f"{self.colors['bold']}Topic:{self.colors['end']} {q.topic}")
        print(f"{self.colors['bold']}Difficulty:{self.colors['end']} {q.difficulty} {stars.get(q.difficulty, '')}")
        print(f"{self.colors['bold']}Progress:{self.colors['end']} {self.attempted}/{len(self.questions)} attempted\n")
        
        # Show the question
        print(f"{self.colors['bold']}{self.colors['yellow']}Q: {self.colors['end']}{q.question}\n")
        
        # Show progress bar
        self._show_progress_bar()
        
        # Show answer if already revealed
        if self.showing_answer:
            self._show_answer()
        else:
            print(f"\n{self.colors['cyan']}💡 Type '{self.colors['yellow']}answer{self.colors['cyan']}' to see the answer{self.colors['end']}")
            print(f"{self.colors['cyan']}   Type '{self.colors['yellow']}hint{self.colors['cyan']}' for a hint{self.colors['end']}\n")
    
    def _show_progress_bar(self):
        """Show a progress bar."""
        total = len(self.questions)
        if total == 0:
            return
        
        progress = self.attempted / total
        bar_length = 40
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\n{self.colors['cyan']}Progress: [{bar}] {self.attempted}/{total} ({int(progress * 100)}%){self.colors['end']}")
    
    def _show_answer(self):
        """Show the answer for the current question."""
        q = self.questions[self.current_index]
        
        print(f"\n{self.colors['bold']}{self.colors['green']}✓ ANSWER:{self.colors['end']}")
        print(f"{self.colors['green']}{q.answer}{self.colors['end']}\n")
        
        print(f"{self.colors['bold']}{self.colors['yellow']}📖 Explanation:{self.colors['end']}")
        print(f"{q.explanation}\n")
        
        print(f"{self.colors['bold']}{self.colors['purple']}💡 Tip:{self.colors['end']}")
        print(f"{q.tip}\n")
    
    def show_hint(self):
        """Show a hint for the current question."""
        q = self.questions[self.current_index]
        
        # Extract keywords from the question
        words = q.question.lower().split()
        keywords = [w for w in words if len(w) > 4 and w not in ['from', 'with', 'where', 'when', 'what']]
        
        if keywords:
            hint = random.choice(keywords)
            print(f"\n{self.colors['yellow']}💡 Hint: Think about using '{hint}' in your query{self.colors['end']}")
        else:
            print(f"\n{self.colors['yellow']}💡 Hint: Consider what columns you need to SELECT{self.colors['end']}")
    
    def show_explanation(self):
        """Show detailed explanation for the current question."""
        q = self.questions[self.current_index]
        
        self.print_header("Detailed Explanation", 'purple')
        print(f"{self.colors['bold']}Question:{self.colors['end']}")
        print(f"  {q.question}\n")
        
        print(f"{self.colors['bold']}Answer:{self.colors['end']}")
        print(f"  {q.answer}\n")
        
        print(f"{self.colors['bold']}Explanation:{self.colors['end']}")
        print(f"  {q.explanation}\n")
        
        print(f"{self.colors['bold']}Key Concept:{self.colors['end']}")
        concepts = self._extract_concepts(q.topic)
        for concept in concepts:
            print(f"  • {concept}")
        
        print(f"\n{self.colors['bold']}Best Practice:{self.colors['end']}")
        print(f"  {q.tip}\n")
    
    def _extract_concepts(self, topic: str) -> List[str]:
        """Extract key concepts from topic."""
        concepts = {
            'SELECT': ['Projection', 'Column selection', 'Data retrieval'],
            'WHERE': ['Filtering', 'Predicates', 'Conditional logic'],
            'JOIN': ['Relationships', 'Connecting tables', 'Foreign keys'],
            'GROUP BY': ['Aggregation', 'Grouping', 'Summary statistics'],
            'ORDER BY': ['Sorting', 'Ascending/Descending', 'Data organization'],
            'LIMIT': ['Row restriction', 'Pagination', 'Top-N queries'],
            'DISTINCT': ['Uniqueness', 'Duplicate removal', 'Value filtering'],
            'Aggregation': ['Summary functions', 'Statistics', 'Data analysis'],
            'HAVING': ['Group filtering', 'Post-aggregation filtering'],
            'Subquery': ['Nested queries', 'Inline views', 'Correlated queries'],
            'CTE': ['Common table expressions', 'With clause', 'Temporary results'],
            'Window Functions': ['Ranking', 'Running totals', 'Moving averages'],
            'CASE': ['Conditional logic', 'If-then-else', 'Data transformation'],
            'JSONB': ['JSON operations', 'Semi-structured data', 'Document storage'],
            'Recursive CTE': ['Hierarchical queries', 'Tree traversal', 'Self-referencing'],
            'Performance': ['Query optimization', 'Indexing', 'Execution plans']
        }
        
        for key, value in concepts.items():
            if key in topic or topic in key:
                return value
        
        return ['SQL query writing', 'Data manipulation', 'Database concepts']
    
    def show_stats(self):
        """Show statistics."""
        self.print_header("📊 Your Progress", 'green')
        
        total = len(self.questions)
        if total == 0:
            self.print_error("No questions loaded.")
            return
        
        print(f"{self.colors['bold']}Questions Attempted:{self.colors['end']} {self.attempted}/{total}")
        print(f"{self.colors['bold']}Completion:{self.colors['end']} {int(self.attempted/total*100)}%\n")
        
        # Progress by difficulty
        difficulty_counts = {}
        for q in self.questions:
            diff = q.difficulty
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        print(f"{self.colors['bold']}Questions by Difficulty:{self.colors['end']}")
        for diff, count in difficulty_counts.items():
            print(f"  {diff}: {count} questions")
        
        # Current position
        print(f"\n{self.colors['bold']}Current Position:{self.colors['end']} {self.current_index + 1}")
        print(f"{self.colors['bold']}Questions Remaining:{self.colors['end']} {total - self.current_index - 1}")
    
    def next_question(self):
        """Move to the next question."""
        if not self.questions:
            self.print_error("No questions loaded.")
            return
        
        self.showing_answer = False
        self.attempted += 1
        
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
        else:
            self.print_success("🎉 You've completed all questions!")
            self.current_index = 0
            self.attempted = len(self.questions)
        
        self.show_question()
    
    def random_question(self):
        """Jump to a random question."""
        if not self.questions:
            self.print_error("No questions loaded.")
            return
        
        self.current_index = random.randint(0, len(self.questions) - 1)
        self.showing_answer = False
        self.attempted += 1
        self.show_question()
    
    def goto_question(self, num: int):
        """Go to a specific question number."""
        if not self.questions:
            self.print_error("No questions loaded.")
            return
        
        try:
            idx = int(num) - 1
            if 0 <= idx < len(self.questions):
                self.current_index = idx
                self.showing_answer = False
                self.attempted += 1
                self.show_question()
            else:
                self.print_error(f"Question {num} not found (1-{len(self.questions)})")
        except ValueError:
            self.print_error("Please enter a valid number")
    
    def reset(self):
        """Reset progress."""
        self.current_index = 0
        self.attempted = 0
        self.showing_answer = False
        self.print_success("Progress reset! Starting from question 1.")
        self.show_question()
    
    def save_answers(self):
        """Save answers to a file."""
        if not self.questions:
            self.print_error("No questions to save.")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"answers_{timestamp}.txt"
        filepath = Path("output") / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"SQL Answers - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for idx, q in enumerate(self.questions, 1):
                f.write(f"\nQuestion {idx}\n")
                f.write("-" * 40 + "\n")
                f.write(f"{q.question}\n\n")
                f.write(f"Answer: {q.answer}\n\n")
                f.write(f"Explanation: {q.explanation}\n\n")
                f.write(f"Tip: {q.tip}\n")
                f.write("-" * 40 + "\n")
        
        self.print_success(f"Answers saved to: {filepath}")
    
    def export_all_answers(self):
        """Export all answers in a comprehensive format."""
        if not self.questions:
            self.print_error("No questions to export.")
            return
        
        from generators.text_answers_generator import TextAnswersGenerator
        generator = TextAnswersGenerator(self.questions)
        filepath = generator.generate()
        self.print_success(f"Comprehensive answers exported to: {filepath}")
    
    def run(self):
        """Main interactive loop."""
        self.print_header("📚 Welcome to SQL Interactive Learning System", 'purple')
        
        # Get the SQL file
        while True:
            print("Enter the path to your SQL or Python file:")
            print(f"  {self.colors['cyan']}(e.g., examples/ecommerce.sql){self.colors['end']}")
            file_path = input("\n📂 File path: ").strip()
            
            if not file_path:
                print("Please enter a file path.")
                continue
            
            # Ask for number of questions
            while True:
                count_input = input(f"\n{self.colors['cyan']}How many questions would you like? (default: 50): {self.colors['end']}").strip()
                if not count_input:
                    count = 50
                    break
                try:
                    count = int(count_input)
                    if count > 0:
                        break
                    else:
                        print("Please enter a positive number.")
                except ValueError:
                    print("Please enter a valid number.")
            
            if self.load_questions(file_path, count):
                break
        
        self.show_question()
        
        while True:
            try:
                command = input(f"\n{self.colors['green']}>>> {self.colors['end']}").strip().lower()
                
                if not command:
                    continue
                
                if command in ['quit', 'exit', 'q']:
                    self.print_success("👋 Goodbye! Happy learning!")
                    break
                
                elif command in ['next', 'n']:
                    self.next_question()
                
                elif command in ['answer', 'a']:
                    self.showing_answer = True
                    self.attempted += 1
                    self.show_question()
                
                elif command in ['hint', 'h']:
                    self.show_hint()
                
                elif command in ['explain', 'e']:
                    self.show_explanation()
                
                elif command in ['stats', 's']:
                    self.show_stats()
                
                elif command in ['random', 'r']:
                    self.random_question()
                
                elif command.startswith('goto'):
                    parts = command.split()
                    if len(parts) > 1:
                        self.goto_question(parts[1])
                    else:
                        print("Usage: goto <question_number>")
                
                elif command in ['reset']:
                    self.reset()
                
                elif command in ['save']:
                    self.save_answers()
                
                elif command in ['export']:
                    self.export_all_answers()
                
                elif command in ['menu', 'm', 'help', '?']:
                    self.show_menu()
                
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'menu' to see available commands.")
                    
            except KeyboardInterrupt:
                print(f"\n{self.colors['yellow']}Interrupted. Type 'quit' to exit.{self.colors['end']}")
            except Exception as e:
                self.print_error(f"Error: {e}")


def main():
    """Main entry point."""
    learner = InteractiveSQLLearner()
    learner.run()


if __name__ == "__main__":
    main()
