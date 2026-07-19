"""
Answers Generator

Generates a comprehensive answers file with explanations and alternate solutions.
"""

from pathlib import Path
from datetime import datetime
from collections import Counter

from config import OUTPUT_DIR, WORKBOOK_TITLE
from models.question import Question


class AnswersGenerator:
    """Generates a comprehensive answers file with explanations."""
    
    def __init__(self, questions: list[Question]) -> None:
        self.questions = questions
        self.output_file = OUTPUT_DIR / "Answers.sql"
        self.readme_file = OUTPUT_DIR / "ANSWERS_README.md"
    
    def generate_sql(self) -> Path:
        """Generate the SQL answers file with explanations as comments."""
        
        with open(self.output_file, "w", encoding="utf-8") as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write(f"{WORKBOOK_TITLE}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Questions: {len(self.questions)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Difficulty summary
            diff_counts = Counter([q.difficulty for q in self.questions])
            f.write("-- Difficulty Distribution:\n")
            for diff, count in diff_counts.items():
                f.write(f"--   {diff}: {count} questions\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            # Questions
            for idx, question in enumerate(self.questions, 1):
                self._write_question(f, idx, question)
        
        return self.output_file
    
    def _write_question(self, f, idx: int, question: Question):
        """Write a single question with all its answers."""
        
        # Question header
        f.write(f"-- ============================================================\n")
        f.write(f"-- QUESTION {idx}\n")
        f.write(f"-- ============================================================\n")
        f.write(f"-- Topic     : {question.topic}\n")
        f.write(f"-- Difficulty: {question.difficulty}\n")
        f.write(f"--\n")
        f.write(f"-- {question.question}\n")
        f.write(f"-- ============================================================\n\n")
        
        # Main Answer
        f.write(f"-- ✅ MAIN ANSWER:\n")
        f.write(f"-- {question.explanation}\n")
        f.write(f"--\n")
        
        # Write the main query with proper formatting
        main_answer = question.answer.strip()
        if not main_answer.endswith(';'):
            main_answer += ';'
        
        # Format the query with better readability
        f.write(self._format_sql(main_answer))
        f.write("\n\n")
        
        # Alternative Answers
        f.write(f"-- 🔄 ALTERNATIVE SOLUTIONS:\n")
        f.write(f"--\n")
        
        alternatives = self._generate_alternatives(question)
        for alt in alternatives:
            f.write(f"-- Option {alt['option']}: {alt['description']}\n")
            f.write(self._format_sql(alt['query']))
            f.write("\n--   Pros: {}\n".format(alt['pros']))
            f.write("--\n\n")
        
        # Performance Tips
        f.write(f"-- ⚡ PERFORMANCE TIPS:\n")
        f.write(f"-- {self._get_performance_tip(question)}\n")
        
        # Common Mistakes
        f.write(f"-- ⚠️ COMMON MISTAKES TO AVOID:\n")
        mistakes = self._get_common_mistakes(question)
        for mistake in mistakes:
            f.write(f"--   • {mistake}\n")
        
        f.write("\n" + "-" * 80 + "\n\n")
    
    def _format_sql(self, query: str) -> str:
        """Format SQL query with proper indentation."""
        # Remove extra whitespace
        query = query.strip()
        
        # Capitalize keywords for readability
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 
                   'RIGHT JOIN', 'FULL JOIN', 'GROUP BY', 'ORDER BY', 'HAVING',
                   'LIMIT', 'OFFSET', 'UNION', 'INTERSECT', 'EXCEPT',
                   'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        
        for keyword in keywords:
            query = query.replace(keyword, keyword.upper())
        
        # Add line breaks for readability
        query = query.replace('SELECT', '\nSELECT')
        query = query.replace('FROM', '\nFROM')
        query = query.replace('WHERE', '\nWHERE')
        query = query.replace('JOIN', '\nJOIN')
        query = query.replace('INNER JOIN', '\nINNER JOIN')
        query = query.replace('LEFT JOIN', '\nLEFT JOIN')
        query = query.replace('RIGHT JOIN', '\nRIGHT JOIN')
        query = query.replace('FULL JOIN', '\nFULL JOIN')
        query = query.replace('GROUP BY', '\nGROUP BY')
        query = query.replace('ORDER BY', '\nORDER BY')
        query = query.replace('HAVING', '\nHAVING')
        query = query.replace('LIMIT', '\nLIMIT')
        
        # Indent lines
        lines = query.split('\n')
        formatted = []
        for line in lines:
            if line.strip():
                if any(keyword in line.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 
                    'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT']):
                    formatted.append(line)
                else:
                    formatted.append(f"  {line}")
            else:
                formatted.append(line)
        
        return '\n'.join(formatted) + ';'
    
    def _generate_alternatives(self, question: Question) -> list:
        """Generate alternative solutions for a question."""
        alternatives = []
        query = question.answer.strip().upper()
        
        # Alternative 1: Different JOIN type
        if 'JOIN' in query and 'LEFT' not in query and 'RIGHT' not in query:
            alternatives.append({
                'option': '1',
                'description': 'Using LEFT JOIN to include all rows from the left table',
                'query': question.answer.replace('JOIN', 'LEFT JOIN'),
                'pros': 'Includes all records from the left table even without matches'
            })
        
        # Alternative 2: Using subquery instead of JOIN
        if 'JOIN' in query and 'WHERE' in query:
            alt_query = self._join_to_subquery(question.answer)
            if alt_query != question.answer:
                alternatives.append({
                    'option': '2',
                    'description': 'Using subquery instead of JOIN',
                    'query': alt_query,
                    'pros': 'Sometimes more readable for simple relationships'
                })
        
        # Alternative 3: Using CTE
        if 'GROUP BY' in query or 'JOIN' in query:
            alt_query = self._to_cte(question.answer)
            if alt_query != question.answer:
                alternatives.append({
                    'option': '3',
                    'description': 'Using Common Table Expression (CTE) for better readability',
                    'query': alt_query,
                    'pros': 'Improves readability and can be reused'
                })
        
        # Alternative 4: Different approach
        if 'WHERE' in query and 'LIKE' in query:
            alternatives.append({
                'option': '4',
                'description': 'Using ILIKE for case-insensitive search',
                'query': question.answer.replace('LIKE', 'ILIKE'),
                'pros': 'Handles case-insensitive matching'
            })
        
        # If no alternatives generated, add a basic alternative
        if not alternatives:
            alternatives.append({
                'option': '1',
                'description': 'Using a different approach with the same result',
                'query': question.answer,
                'pros': 'Different ways to achieve the same result'
            })
        
        return alternatives[:4]  # Limit to 4 alternatives
    
    def _join_to_subquery(self, query: str) -> str:
        """Convert a JOIN query to a subquery."""
        # Simple conversion - this is a basic example
        if 'JOIN' in query:
            parts = query.split('JOIN')
            if len(parts) >= 2:
                main = parts[0].strip()
                join_part = parts[1].strip()
                # Extract table and condition
                if 'ON' in join_part:
                    join_info = join_part.split('ON')
                    table = join_info[0].strip()
                    condition = join_info[1].strip()
                    # Create a simple subquery version
                    return f"{main} WHERE {condition.split('=')[0].strip()} IN (SELECT {condition.split('=')[1].strip()} FROM {table})"
        return query
    
    def _to_cte(self, query: str) -> str:
        """Convert a query to use CTE."""
        # Simple conversion
        if 'FROM' in query:
            parts = query.split('FROM')
            if len(parts) >= 2:
                select_part = parts[0].replace('SELECT', '').strip()
                from_part = parts[1].strip()
                return f"WITH cte AS (SELECT * FROM {from_part}) SELECT {select_part} FROM cte;"
        return query
    
    def _get_performance_tip(self, question: Question) -> str:
        """Get performance tips based on the query type."""
        query = question.answer.upper()
        tips = []
        
        if 'SELECT *' in query:
            tips.append("Avoid SELECT *; specify only needed columns for better performance")
        
        if 'JOIN' in query:
            tips.append("Ensure there are indexes on JOIN columns for faster lookups")
        
        if 'WHERE' in query:
            tips.append("Index columns used in WHERE clauses for faster filtering")
        
        if 'ORDER BY' in query:
            tips.append("Index ORDER BY columns to avoid filesort operations")
        
        if 'GROUP BY' in query:
            tips.append("Use indexes on GROUP BY columns to improve aggregation performance")
        
        if 'LIKE' in query and '%' in query:
            tips.append("LIKE with leading '%' cannot use indexes; consider full-text search alternatives")
        
        if not tips:
            tips.append("Use EXPLAIN ANALYZE to understand query execution plan")
        
        return " | ".join(tips[:3])
    
    def _get_common_mistakes(self, question: Question) -> list:
        """Get common mistakes for this question type."""
        query = question.answer.upper()
        mistakes = []
        
        if 'WHERE' in query:
            mistakes.append("Using = NULL instead of IS NULL for checking null values")
            mistakes.append("Forgetting to quote string values properly")
        
        if 'JOIN' in query:
            mistakes.append("Forgetting JOIN conditions causing Cartesian products")
            mistakes.append("Using wrong column names in JOIN conditions")
        
        if 'GROUP BY' in query:
            mistakes.append("Including non-aggregated columns not in GROUP BY")
            mistakes.append("Using WHERE instead of HAVING for aggregated filters")
        
        if 'ORDER BY' in query:
            mistakes.append("Ordering by columns not in SELECT list (allowed but confusing)")
        
        if not mistakes:
            mistakes.append("Not testing queries on a sample dataset first")
            mistakes.append("Assuming data is clean without checking for NULLs")
        
        return mistakes[:3]
    
    def generate_readme(self) -> Path:
        """Generate a README file for the answers."""
        
        with open(self.readme_file, "w", encoding="utf-8") as f:
            f.write(f"# {WORKBOOK_TITLE} - Answer Key\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Questions: {len(self.questions)}\n\n")
            
            f.write("## Table of Contents\n\n")
            
            # Group by difficulty
            for difficulty in ['Beginner', 'Intermediate', 'Advanced', 'Expert']:
                qs = [q for q in self.questions if q.difficulty == difficulty]
                if qs:
                    f.write(f"### {difficulty} ({len(qs)} questions)\n")
                    for q in qs:
                        f.write(f"- Q{q.id}: {q.topic}\n")
                    f.write("\n")
            
            f.write("\n## Answer Format\n\n")
            f.write("Each answer includes:\n")
            f.write("- Main solution with explanation\n")
            f.write("- Alternative solutions with pros/cons\n")
            f.write("- Performance tips\n")
            f.write("- Common mistakes to avoid\n\n")
            
            f.write("### How to Use\n\n")
            f.write("1. Open the `Answers.sql` file\n")
            f.write("2. Each question is clearly marked with comments\n")
            f.write("3. Review the main solution and alternatives\n")
            f.write("4. Try running different solutions to compare\n")
            f.write("5. Use the performance tips to optimize your queries\n\n")
        
        return self.readme_file
