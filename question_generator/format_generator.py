"""
Format Generator - Generates various SQL questions with different difficulty levels
"""

from typing import List
from models.table import Table
from models.question import Question
import random


class FormatQuestionGenerator:
    """Generates SQL questions with specific format."""
    
    def __init__(self, tables: List[Table]):
        self.tables = tables
        self.questions = []
        self.counter = 0
        self._seed = random.randint(1, 999999)
    
    def generate_all(self, count: int = 100) -> List[Question]:
        """Generate questions of various types."""
        self.questions = []
        self.counter = 0
        random.seed(self._seed + count)  # Vary seed for different runs
        
        # Generate a larger pool (3x the requested count)
        pool_size = count * 3
        all_questions = []
        
        # Collect all question generators
        generators = [
            self._generate_select_questions,
            self._generate_where_questions,
            self._generate_order_by_questions,
            self._generate_aggregation_questions,
            self._generate_join_questions,
            self._generate_group_by_questions,
            self._generate_subquery_questions,
            self._generate_cte_questions,
            self._generate_window_function_questions,
            self._generate_case_questions,
            self._generate_date_questions,
            self._generate_string_questions
        ]
        
        # Generate questions from each generator, aiming for pool_size total
        for gen in generators:
            gen()
        
        # Shuffle and pick the requested count
        random.shuffle(self.questions)
        if len(self.questions) > count:
            self.questions = self.questions[:count]
        
        # Reassign IDs
        for i, q in enumerate(self.questions, 1):
            q.id = i
        
        return self.questions
    
    def _add_question(self, topic: str, difficulty: str, question: str,
                      answer: str, explanation: str, tip: str):
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
    
    def _generate_select_questions(self):
        for table in self.tables:
            if len(table.columns) > 0:
                # Randomly pick columns
                cols = [c.name for c in table.columns]
                random.shuffle(cols)
                col_subset = cols[:min(3, len(cols))]
                cols_str = ", ".join(col_subset)
                self._add_question(
                    topic="SELECT",
                    difficulty="Beginner",
                    question=f"List all records from the {table.name} table.",
                    answer=f"SELECT * FROM {table.name};",
                    explanation=f"SELECT * returns every column and row from {table.name}.",
                    tip="Use specific columns instead of SELECT * in production."
                )
                self._add_question(
                    topic="SELECT",
                    difficulty="Beginner",
                    question=f"Show only {cols_str} from the {table.name} table.",
                    answer=f"SELECT {cols_str} FROM {table.name};",
                    explanation=f"SELECT with specific columns returns only those columns.",
                    tip="Specify columns for better performance."
                )
    
    def _generate_where_questions(self):
        for table in self.tables:
            text_cols = [c for c in table.columns if 'char' in c.data_type.lower() or c.data_type == 'text']
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
            if text_cols:
                col = random.choice(text_cols)
                # Random value for LIKE
                sample_values = ['test', 'example', 'sample', 'demo', 'admin']
                val = random.choice(sample_values)
                self._add_question(
                    topic="WHERE",
                    difficulty="Beginner",
                    question=f"Find all {table.name} where {col.name} contains '{val}'.",
                    answer=f"SELECT * FROM {table.name} WHERE {col.name} LIKE '%{val}%';",
                    explanation=f"LIKE with % performs a partial match.",
                    tip="Use ILIKE for case-insensitive searches."
                )
            if num_cols:
                col = random.choice(num_cols)
                value = random.randint(1, 100)
                self._add_question(
                    topic="WHERE",
                    difficulty="Beginner",
                    question=f"Find all {table.name} where {col.name} > {value}.",
                    answer=f"SELECT * FROM {table.name} WHERE {col.name} > {value};",
                    explanation=f"Filters rows where {col.name} is greater than {value}.",
                    tip="Use >, <, >=, <=, =, != for numeric comparisons."
                )
    
    def _generate_order_by_questions(self):
        for table in self.tables:
            if table.columns:
                col = random.choice(table.columns)
                order = random.choice(['ASC', 'DESC'])
                self._add_question(
                    topic="ORDER BY",
                    difficulty="Beginner",
                    question=f"List all {table.name} ordered by {col.name} {order}.",
                    answer=f"SELECT * FROM {table.name} ORDER BY {col.name} {order};",
                    explanation=f"ORDER BY {col.name} {order} sorts accordingly.",
                    tip="DESC shows largest numbers or latest dates first."
                )
    
    def _generate_aggregation_questions(self):
        for table in self.tables:
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
            for col in num_cols:
                func = random.choice(['AVG', 'SUM', 'COUNT', 'MAX', 'MIN'])
                if func == 'COUNT':
                    self._add_question(
                        topic="Aggregation",
                        difficulty="Intermediate",
                        question=f"Count the number of rows in {table.name}.",
                        answer=f"SELECT COUNT(*) FROM {table.name};",
                        explanation="COUNT(*) counts all rows.",
                        tip="COUNT(column) counts non-null values."
                    )
                else:
                    self._add_question(
                        topic="Aggregation",
                        difficulty="Intermediate",
                        question=f"Calculate the {func} of {col.name} from {table.name}.",
                        answer=f"SELECT {func}({col.name}) FROM {table.name};",
                        explanation=f"{func}({col.name}) calculates the {func.lower()}.",
                        tip="Use ROUND(AVG(column), 2) to limit decimals."
                    )
                break  # only one aggregation per table to avoid duplicates
    
    def _generate_join_questions(self):
        if len(self.tables) >= 2:
            # Pick two random tables
            tables = random.sample(self.tables, 2)
            t1, t2 = tables[0], tables[1]
            # Assume a foreign key exists (simplified)
            fk_col = f"{t1.name}_id"
            self._add_question(
                topic="JOIN",
                difficulty="Intermediate",
                question=f"Join the {t1.name} table with the {t2.name} table.",
                answer=f"SELECT * FROM {t1.name} JOIN {t2.name} ON {t1.name}.id = {t2.name}.{fk_col};",
                explanation=f"INNER JOIN connects {t1.name} to {t2.name} on the foreign key.",
                tip="Use table aliases to make queries more readable."
            )
    
    def _generate_group_by_questions(self):
        for table in self.tables:
            group_cols = [c for c in table.columns if c.data_type in ['character varying', 'text', 'integer'] and not c.primary_key]
            if group_cols:
                col = random.choice(group_cols)
                self._add_question(
                    topic="GROUP BY",
                    difficulty="Intermediate",
                    question=f"Count records in {table.name} grouped by {col.name}.",
                    answer=f"SELECT {col.name}, COUNT(*) FROM {table.name} GROUP BY {col.name};",
                    explanation=f"GROUP BY {col.name} creates groups and COUNT counts each group.",
                    tip="All non-aggregated columns in SELECT must be in GROUP BY."
                )
    
    def _generate_subquery_questions(self):
        for table in self.tables:
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
            if num_cols:
                col = random.choice(num_cols)
                self._add_question(
                    topic="Subquery",
                    difficulty="Advanced",
                    question=f"Find records in {table.name} where {col.name} is above average.",
                    answer=f"SELECT * FROM {table.name} WHERE {col.name} > (SELECT AVG({col.name}) FROM {table.name});",
                    explanation=f"Subquery computes the average, main query filters above it.",
                    tip="Subqueries can be slow; consider CTEs for complex queries."
                )
    
    def _generate_cte_questions(self):
        for table in self.tables:
            self._add_question(
                topic="CTE",
                difficulty="Advanced",
                question=f"Write a CTE to filter {table.name} and then query it.",
                answer=f"WITH filtered AS (SELECT * FROM {table.name} WHERE condition) SELECT * FROM filtered;",
                explanation="WITH creates a temporary named result set.",
                tip="CTEs make complex queries more readable and reusable."
            )
    
    def _generate_window_function_questions(self):
        for table in self.tables:
            order_cols = [c for c in table.columns if 'timestamp' in c.data_type.lower() or c.data_type in ['integer', 'date']]
            if order_cols:
                col = random.choice(order_cols)
                self._add_question(
                    topic="Window Functions",
                    difficulty="Expert",
                    question=f"Use ROW_NUMBER() to rank records in {table.name} by {col.name}.",
                    answer=f"SELECT *, ROW_NUMBER() OVER (ORDER BY {col.name}) FROM {table.name};",
                    explanation=f"ROW_NUMBER() assigns sequential numbers ordered by {col.name}.",
                    tip="Use PARTITION BY to reset numbering for each group."
                )
    
    def _generate_case_questions(self):
        for table in self.tables:
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
            if num_cols:
                col = random.choice(num_cols)
                self._add_question(
                    topic="CASE",
                    difficulty="Advanced",
                    question=f"Use CASE to categorize {col.name} in {table.name} (e.g., 'High', 'Medium', 'Low').",
                    answer=f"SELECT *, CASE WHEN {col.name} > 100 THEN 'High' WHEN {col.name} > 50 THEN 'Medium' ELSE 'Low' END AS category FROM {table.name};",
                    explanation="CASE creates conditional logic.",
                    tip="CASE is evaluated in order; the first matching condition wins."
                )
    
    def _generate_date_questions(self):
        for table in self.tables:
            date_cols = [c for c in table.columns if 'timestamp' in c.data_type.lower() or c.data_type == 'date']
            if date_cols:
                col = random.choice(date_cols)
                self._add_question(
                    topic="Date Functions",
                    difficulty="Advanced",
                    question=f"Extract the year from {col.name} in {table.name}.",
                    answer=f"SELECT EXTRACT(YEAR FROM {col.name}) FROM {table.name};",
                    explanation="EXTRACT(YEAR FROM ...) gets the year from a date.",
                    tip="Use DATE_TRUNC() for grouping by month, quarter, or year."
                )
    
    def _generate_string_questions(self):
        for table in self.tables:
            text_cols = [c for c in table.columns if 'char' in c.data_type.lower() or c.data_type == 'text']
            if text_cols:
                col = random.choice(text_cols)
                self._add_question(
                    topic="String Functions",
                    difficulty="Advanced",
                    question=f"Convert {col.name} to uppercase in {table.name}.",
                    answer=f"SELECT UPPER({col.name}) FROM {table.name};",
                    explanation="UPPER() converts text to uppercase.",
                    tip="Use LOWER() for case-insensitive comparisons."
                )
