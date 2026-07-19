"""
question_generator/enhanced_generator.py

Enhanced question generator that uses schema analysis.
"""

from typing import List
from models.schema import Schema
from models.question import Question
from parser.schema_analyzer import SchemaAnalyzer


class EnhancedQuestionGenerator:
    """Generates questions using schema analysis."""
    
    def __init__(self, schema: Schema):
        self.schema = schema
        self.analyzer = SchemaAnalyzer(schema)
        self.questions: List[Question] = []
        self.counter = 0
    
    def generate_all(self) -> List[Question]:
        """Generate all questions."""
        
        features = self.analyzer.detect_features()
        topics = self.analyzer.get_question_topics()
        
        # Generate beginner questions
        self._generate_beginner_questions(topics['beginner'])
        
        # Generate intermediate questions
        self._generate_intermediate_questions(topics['intermediate'], features)
        
        # Generate advanced questions
        self._generate_advanced_questions(topics['advanced'], features)
        
        # Generate expert questions
        self._generate_expert_questions(topics['expert'], features)
        
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
    
    def _generate_beginner_questions(self, topics: List[str]):
        """Generate beginner questions."""
        
        for table in self.schema.tables:
            # SELECT all
            self._add_question(
                topic="SELECT",
                difficulty="Beginner",
                question=f"List all records from the {table.name} table.",
                answer=f"SELECT * FROM {table.name};",
                explanation=f"SELECT * returns every column and row from the {table.name} table.",
                tip="SELECT * is useful for exploration, but in production, specify only needed columns."
            )
            
            # Find text columns for LIKE queries
            for col in table.columns:
                if col.data_type in ['character varying', 'text'] and not col.primary_key:
                    self._add_question(
                        topic="WHERE",
                        difficulty="Beginner",
                        question=f"Find all {table.name} where {col.name} contains 'test'.",
                        answer=f"SELECT * FROM {table.name} WHERE {col.name} LIKE '%test%';",
                        explanation=f"LIKE with % performs a partial match on the {col.name} column.",
                        tip="Use ILIKE for case-insensitive searches in PostgreSQL."
                    )
                    break
            
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
    
    def _generate_intermediate_questions(self, topics: List[str], features: dict):
        """Generate intermediate questions."""
        
        # Aggregations
        for table in self.schema.tables:
            for col in table.columns:
                if col.data_type in ['integer', 'numeric', 'decimal']:
                    if not col.primary_key and not col.foreign_key:
                        self._add_question(
                            topic="Aggregation",
                            difficulty="Intermediate",
                            question=f"Calculate the average {col.name} from the {table.name} table.",
                            answer=f"SELECT AVG({col.name}) AS average_{col.name} FROM {table.name};",
                            explanation=f"AVG({col.name}) calculates the mean of all {col.name} values.",
                            tip=f"Use ROUND(AVG({col.name}), 2) to limit decimal places."
                        )
                        break
        
        # GROUP BY
        for table in self.schema.tables:
            has_fk = False
            for col in table.columns:
                if col.foreign_key:
                    has_fk = True
                    break
            if has_fk:
                self._add_question(
                    topic="GROUP BY",
                    difficulty="Intermediate",
                    question=f"Count the number of records in {table.name} grouped by a foreign key.",
                    answer=f"SELECT foreign_key_column, COUNT(*) FROM {table.name} GROUP BY foreign_key_column;",
                    explanation=f"GROUP BY creates one row per foreign key value with its count.",
                    tip="Always GROUP BY non-aggregated columns; use HAVING to filter groups."
                )
                break
        
        # JOINs
        for rel in self.schema.relationships:
            self._add_question(
                topic="JOIN",
                difficulty="Intermediate",
                question=f"Join the {rel.source_table} table with the {rel.target_table} table.",
                answer=f"SELECT * FROM {rel.source_table} JOIN {rel.target_table} ON {rel.source_table}.{rel.source_column} = {rel.target_table}.{rel.target_column};",
                explanation=f"INNER JOIN connects {rel.source_table} to {rel.target_table} where {rel.source_column} matches {rel.target_column}.",
                tip="Use table aliases to make queries shorter and more readable."
            )
            break
    
    def _generate_advanced_questions(self, topics: List[str], features: dict):
        """Generate advanced questions."""
        
        # Window functions
        if features['has_timestamps']:
            for table_name in features['tables_with_timestamps']:
                table = self.schema.get_table(table_name)
                if table:
                    # Find a timestamp column
                    for col in table.columns:
                        if 'timestamp' in col.data_type.lower():
                            self._add_question(
                                topic="Window Functions",
                                difficulty="Advanced",
                                question=f"Use ROW_NUMBER() to rank records in {table.name} by {col.name}.",
                                answer=f"SELECT *, ROW_NUMBER() OVER (ORDER BY {col.name}) AS row_num FROM {table.name};",
                                explanation=f"ROW_NUMBER() assigns a unique sequential number to each row ordered by {col.name}.",
                                tip="Use PARTITION BY to restart numbering for each group."
                            )
                            break
        
        # CTEs
        self._add_question(
            topic="CTE",
            difficulty="Advanced",
            question="Write a query using a Common Table Expression (WITH clause).",
            answer="WITH cte_name AS (SELECT * FROM users WHERE email IS NOT NULL) SELECT * FROM cte_name;",
            explanation="WITH creates a temporary named result set that can be referenced in the main query.",
            tip="CTEs make complex queries more readable and can be referenced multiple times."
        )
    
    def _generate_expert_questions(self, topics: List[str], features: dict):
        """Generate expert questions."""
        
        # JSONB queries
        if features['has_jsonb']:
            for table_name in features['tables_with_jsonb']:
                table = self.schema.get_table(table_name)
                if table:
                    for col in table.columns:
                        if 'json' in col.data_type.lower():
                            self._add_question(
                                topic="JSONB",
                                difficulty="Expert",
                                question=f"Extract a specific field from the JSONB column {col.name} in {table.name}.",
                                answer=f"SELECT {col.name}->>'field_name' AS field FROM {table.name};",
                                explanation=f"->> extracts a JSON field as text from the {col.name} column.",
                                tip="Use -> for JSON objects and ->> for text values."
                            )
                            break
        
        # Recursive CTE
        if features['has_recursive']:
            for table_name in features['self_referencing_tables']:
                self._add_question(
                    topic="Recursive CTE",
                    difficulty="Expert",
                    question=f"Write a recursive CTE to traverse the hierarchy in the {table_name} table.",
                    answer=f"WITH RECURSIVE hierarchy AS (SELECT * FROM {table_name} WHERE parent_id IS NULL UNION ALL SELECT child.* FROM {table_name} child JOIN hierarchy parent ON child.parent_id = parent.id) SELECT * FROM hierarchy;",
                    explanation="Recursive CTE starts with root records (no parent) and traverses the hierarchy.",
                    tip="The anchor (first SELECT) defines the starting point; the recursive part adds children."
                )
                break
