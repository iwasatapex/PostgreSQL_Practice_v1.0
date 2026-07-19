"""
Text Answers Generator

Generates a comprehensive text-based answers file with explanations
and alternate solutions in plain text format.
"""

from pathlib import Path
from datetime import datetime
from collections import Counter

from config import OUTPUT_DIR, WORKBOOK_TITLE
from models.question import Question


class TextAnswersGenerator:
    """Generates a comprehensive text-based answers file."""
    
    def __init__(self, questions: list[Question]) -> None:
        self.questions = questions
        self.output_file = OUTPUT_DIR / "ANSWERS.txt"
    
    def generate(self) -> Path:
        """Generate the text answers file."""
        
        with open(self.output_file, "w", encoding="utf-8") as f:
            # Header
            f.write("=" * 100 + "\n")
            f.write(f"{WORKBOOK_TITLE}\n")
            f.write("=" * 100 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Questions: {len(self.questions)}\n")
            f.write("=" * 100 + "\n\n")
            
            # Difficulty summary
            f.write("DIFFICULTY DISTRIBUTION\n")
            f.write("-" * 40 + "\n")
            diff_counts = Counter([q.difficulty for q in self.questions])
            for diff, count in diff_counts.items():
                f.write(f"  {diff}: {count} questions\n")
            f.write("\n" + "=" * 100 + "\n\n")
            
            # Table of Contents
            f.write("TABLE OF CONTENTS\n")
            f.write("=" * 100 + "\n\n")
            
            for difficulty in ['Beginner', 'Intermediate', 'Advanced', 'Expert']:
                qs = [q for q in self.questions if q.difficulty == difficulty]
                if qs:
                    f.write(f"\n{difficulty.upper()} ({len(qs)} questions)\n")
                    f.write("-" * 60 + "\n")
                    for q in qs[:20]:  # Show first 20
                        f.write(f"  Q{q.id:4d}: {q.topic}\n")
                    if len(qs) > 20:
                        f.write(f"  ... and {len(qs) - 20} more questions\n")
            
            f.write("\n" + "=" * 100 + "\n\n")
            
            # Questions with answers
            for idx, question in enumerate(self.questions, 1):
                self._write_question(f, idx, question)
        
        return self.output_file
    
    def _write_question(self, f, idx: int, question: Question):
        """Write a single question with all its answers."""
        
        # Question header
        f.write(f"\n{'=' * 100}\n")
        f.write(f"QUESTION {idx}\n")
        f.write(f"{'=' * 100}\n")
        f.write(f"Topic     : {question.topic}\n")
        f.write(f"Difficulty: {question.difficulty}\n")
        f.write(f"\n{question.question}\n")
        f.write(f"\n{'-' * 100}\n\n")
        
        # Main Answer
        f.write(f"MAIN ANSWER:\n")
        f.write(f"{'-' * 60}\n")
        f.write(f"{question.answer}\n\n")
        f.write(f"Explanation: {question.explanation}\n\n")
        
        # Alternative Solutions
        f.write(f"ALTERNATIVE SOLUTIONS:\n")
        f.write(f"{'-' * 60}\n")
        
        alternatives = self._generate_alternatives(question)
        for alt in alternatives:
            f.write(f"\n  Option {alt['option']}: {alt['description']}\n")
            f.write(f"  {alt['query']}\n")
            f.write(f"  ✓ Pros: {alt['pros']}\n")
        
        # Performance Tips
        f.write(f"\nPERFORMANCE TIPS:\n")
        f.write(f"{'-' * 60}\n")
        tips = self._get_performance_tips(question)
        for tip in tips:
            f.write(f"  • {tip}\n")
        
        # Common Mistakes
        f.write(f"\nCOMMON MISTAKES TO AVOID:\n")
        f.write(f"{'-' * 60}\n")
        mistakes = self._get_common_mistakes(question)
        for mistake in mistakes:
            f.write(f"  ✗ {mistake}\n")
        
        # Best Practice
        f.write(f"\nBEST PRACTICE:\n")
        f.write(f"{'-' * 60}\n")
        f.write(f"  {self._get_best_practice(question)}\n")
        
        f.write(f"\n{'=' * 100}\n")
        f.write(f"{' ' * 45}Page {idx}\n")
        f.write(f"{'=' * 100}\n\n")
    
    def _generate_alternatives(self, question: Question) -> list:
        """Generate alternative solutions for a question."""
        alternatives = []
        query = question.answer.strip().upper()
        
        # Alternative 1: Different approach
        if 'SELECT *' in query:
            # Get column names from the query context
            alt_query = question.answer.replace('SELECT *', 'SELECT id, name, created_at')
            alternatives.append({
                'option': '1',
                'description': 'Specify only needed columns instead of SELECT *',
                'query': alt_query,
                'pros': 'Better performance, more readable, explicit intent'
            })
        
        # Alternative 2: Using different JOIN type
        if 'JOIN' in query and 'LEFT' not in query and 'RIGHT' not in query:
            alt_query = question.answer.replace('JOIN', 'LEFT JOIN')
            alternatives.append({
                'option': '2',
                'description': 'Using LEFT JOIN to include all rows from left table',
                'query': alt_query,
                'pros': 'Includes unmatched rows from left table'
            })
        
        # Alternative 3: Using subquery
        if 'JOIN' in query:
            alt_query = self._join_to_subquery(question.answer)
            if alt_query != question.answer:
                alternatives.append({
                    'option': '3',
                    'description': 'Using subquery instead of JOIN',
                    'query': alt_query,
                    'pros': 'Sometimes more intuitive for simple relationships'
                })
        
        # Alternative 4: Using CTE
        if 'GROUP BY' in query or 'JOIN' in query:
            alt_query = self._to_cte(question.answer)
            if alt_query != question.answer:
                alternatives.append({
                    'option': '4',
                    'description': 'Using Common Table Expression (CTE)',
                    'query': alt_query,
                    'pros': 'More readable, can be reused, easier to debug'
                })
        
        # Alternative 5: Using window function
        if 'GROUP BY' in query and 'COUNT' in query:
            alt_query = self._to_window_function(question.answer)
            if alt_query != question.answer:
                alternatives.append({
                    'option': '5',
                    'description': 'Using window function for running totals',
                    'query': alt_query,
                    'pros': 'More efficient, preserves detail rows'
                })
        
        # If no alternatives generated, add a basic alternative
        if not alternatives:
            alternatives.append({
                'option': '1',
                'description': 'Alternative approach with same result',
                'query': question.answer,
                'pros': 'Different ways to achieve the same result'
            })
        
        return alternatives[:4]  # Limit to 4 alternatives
    
    def _join_to_subquery(self, query: str) -> str:
        """Convert a JOIN query to a subquery."""
        if 'JOIN' in query and 'ON' in query:
            parts = query.split('JOIN')
            if len(parts) >= 2:
                main = parts[0].strip()
                join_part = parts[1].strip()
                if 'ON' in join_part:
                    join_info = join_part.split('ON')
                    table = join_info[0].strip()
                    condition = join_info[1].strip()
                    # Simple subquery conversion
                    if '=' in condition:
                        left, right = condition.split('=')
                        return f"{main} WHERE {left.strip()} IN (SELECT {right.strip()} FROM {table})"
        return query
    
    def _to_cte(self, query: str) -> str:
        """Convert a query to use CTE."""
        if 'SELECT' in query and 'FROM' in query:
            parts = query.split('FROM')
            if len(parts) >= 2:
                select_part = parts[0].replace('SELECT', '').strip()
                from_part = parts[1].strip()
                return f"WITH cte AS (SELECT * FROM {from_part}) SELECT {select_part} FROM cte;"
        return query
    
    def _to_window_function(self, query: str) -> str:
        """Convert GROUP BY query to use window function."""
        if 'GROUP BY' in query and 'COUNT' in query:
            # Simple conversion for demonstration
            return query.replace('GROUP BY', 'OVER (PARTITION BY')
        return query
    
    def _get_performance_tips(self, question: Question) -> list:
        """Get performance tips based on the query type."""
        query = question.answer.upper()
        tips = []
        
        if 'SELECT *' in query:
            tips.append("Avoid SELECT *; specify only needed columns for better performance and clarity")
        
        if 'JOIN' in query:
            tips.append("Ensure indexes exist on JOIN columns for faster lookups")
        
        if 'WHERE' in query:
            tips.append("Index columns used in WHERE clauses for faster filtering")
        
        if 'ORDER BY' in query:
            tips.append("Index ORDER BY columns to avoid filesort operations")
        
        if 'GROUP BY' in query:
            tips.append("Use indexes on GROUP BY columns to improve aggregation performance")
        
        if 'LIKE' in query and '%' in query:
            tips.append("LIKE with leading '%' cannot use indexes; consider full-text search")
        
        if not tips:
            tips.append("Use EXPLAIN ANALYZE to understand and optimize query execution plan")
        
        return tips[:4]
    
    def _get_common_mistakes(self, question: Question) -> list:
        """Get common mistakes for this question type."""
        query = question.answer.upper()
        mistakes = []
        
        if 'WHERE' in query:
            mistakes.append("Using = NULL instead of IS NULL for checking null values")
            mistakes.append("Forgetting to quote string values properly (use single quotes)")
            mistakes.append("Using OR conditions without parentheses")
        
        if 'JOIN' in query:
            mistakes.append("Forgetting JOIN conditions causing Cartesian products")
            mistakes.append("Using wrong column names in JOIN conditions")
            mistakes.append("Joining tables without proper foreign key relationships")
        
        if 'GROUP BY' in query:
            mistakes.append("Including non-aggregated columns not in GROUP BY clause")
            mistakes.append("Using WHERE instead of HAVING for aggregated filters")
            mistakes.append("Order of execution: WHERE filters rows, HAVING filters groups")
        
        if 'ORDER BY' in query:
            mistakes.append("Ordering by columns not in SELECT list (allowed but confusing)")
        
        if not mistakes:
            mistakes.append("Not testing queries on a sample dataset first")
            mistakes.append("Assuming data is clean without checking for NULLs")
            mistakes.append("Not using proper formatting for readability")
        
        return mistakes[:4]
    
    def _get_best_practice(self, question: Question) -> str:
        """Get best practice recommendation."""
        query = question.answer.upper()
        
        if 'SELECT *' in query:
            return "Always specify explicit column names for better performance and maintainability"
        elif 'JOIN' in query:
            return "Use appropriate JOIN types and ensure proper indexing on foreign keys"
        elif 'GROUP BY' in query:
            return "Group by meaningful columns and use HAVING for post-aggregation filtering"
        elif 'WHERE' in query:
            return "Use WHERE clauses efficiently with proper indexing for large datasets"
        elif 'ORDER BY' in query:
            return "Order by indexed columns for better performance on large datasets"
        else:
            return "Test queries with EXPLAIN ANALYZE and optimize based on execution plan"
