"""
question_generator/mega_generator.py

Generates 1000+ SQL questions with difficulty distribution.
"""

import random
from typing import List, Dict, Any
from models.schema import Schema
from models.question import Question
from parser.schema_analyzer import SchemaAnalyzer


class MegaQuestionGenerator:
    """Generates 1000+ SQL questions with difficulty distribution."""
    
    def __init__(self, schema: Schema):
        self.schema = schema
        self.analyzer = SchemaAnalyzer(schema)
        self.questions: List[Question] = []
        self.counter = 0
        self.features = self.analyzer.detect_features()
        
        # Difficulty distribution (percentage)
        self.distribution = {
            'Beginner': 25,      # 250 questions
            'Intermediate': 35,  # 350 questions
            'Advanced': 25,      # 250 questions
            'Expert': 15         # 150 questions
        }
    
    def generate_all(self, target_count: int = 1000) -> List[Question]:
        """Generate target number of questions with difficulty distribution."""
        
        print(f"\n🎯 Generating {target_count} questions...")
        
        # Calculate counts per difficulty
        counts = {}
        for level, percentage in self.distribution.items():
            counts[level] = int(target_count * percentage / 100)
        
        # Adjust for rounding
        total = sum(counts.values())
        if total < target_count:
            counts['Beginner'] += target_count - total
        
        print(f"📊 Difficulty Distribution:")
        for level, count in counts.items():
            print(f"  - {level}: {count} questions")
        
        # Generate questions by difficulty
        self._generate_beginner_questions(counts['Beginner'])
        self._generate_intermediate_questions(counts['Intermediate'])
        self._generate_advanced_questions(counts['Advanced'])
        self._generate_expert_questions(counts['Expert'])
        
        # Shuffle to mix difficulties
        random.shuffle(self.questions)
        
        # Reassign IDs
        for i, q in enumerate(self.questions, 1):
            q.id = i
        
        print(f"✅ Generated {len(self.questions)} questions")
        
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
    
    def _generate_beginner_questions(self, count: int):
        """Generate Beginner level questions."""
        
        topics = [
            ('SELECT', self._generate_select_question),
            ('WHERE', self._generate_where_question),
            ('ORDER BY', self._generate_order_by_question),
            ('LIMIT', self._generate_limit_question),
            ('DISTINCT', self._generate_distinct_question),
        ]
        
        for _ in range(count):
            topic, generator = random.choice(topics)
            generator(topic)
    
    def _generate_intermediate_questions(self, count: int):
        """Generate Intermediate level questions."""
        
        topics = [
            ('Aggregation', self._generate_aggregation_question),
            ('GROUP BY', self._generate_group_by_question),
            ('HAVING', self._generate_having_question),
            ('JOIN', self._generate_join_question),
            ('Subquery', self._generate_subquery_question),
        ]
        
        for _ in range(count):
            topic, generator = random.choice(topics)
            generator(topic)
    
    def _generate_advanced_questions(self, count: int):
        """Generate Advanced level questions."""
        
        topics = []
        
        if self.features['has_timestamps']:
            topics.append(('Window Functions', self._generate_window_question))
        
        topics.append(('CTE', self._generate_cte_question))
        topics.append(('CASE', self._generate_case_question))
        topics.append(('Date Functions', self._generate_date_question))
        topics.append(('String Functions', self._generate_string_question))
        
        if not topics:
            topics = [('CTE', self._generate_cte_question)]
        
        for _ in range(count):
            topic, generator = random.choice(topics)
            generator(topic)
    
    def _generate_expert_questions(self, count: int):
        """Generate Expert level questions."""
        
        topics = []
        
        if self.features['has_jsonb']:
            topics.append(('JSONB', self._generate_json_question))
        
        if self.features['has_recursive']:
            topics.append(('Recursive CTE', self._generate_recursive_question))
        
        topics.append(('Performance', self._generate_performance_question))
        topics.append(('Advanced JOIN', self._generate_advanced_join_question))
        
        if not topics:
            topics = [('Advanced JOIN', self._generate_advanced_join_question)]
        
        for _ in range(count):
            topic, generator = random.choice(topics)
            generator(topic)
    
    # ==================== BEGINNER QUESTION GENERATORS ====================
    
    def _generate_select_question(self, topic: str):
        """Generate SELECT questions."""
        table = random.choice(self.schema.tables)
        
        templates = [
            (f"List all records from the {table.name} table.",
             f"SELECT * FROM {table.name};",
             f"SELECT * returns every column and row from the {table.name} table."),
            
            (f"Show only the first 10 rows from {table.name}.",
             f"SELECT * FROM {table.name} LIMIT 10;",
             f"LIMIT 10 restricts the output to only 10 rows."),
            
            (f"Display specific columns from {table.name}.",
             f"SELECT {', '.join([c.name for c in table.columns[:3]])} FROM {table.name};",
             f"SELECT with specific columns returns only those columns."),
        ]
        
        question, answer, explanation = random.choice(templates)
        self._add_question(
            topic=topic,
            difficulty="Beginner",
            question=question,
            answer=answer,
            explanation=explanation,
            tip="Use specific columns instead of SELECT * in production."
        )
    
    def _generate_where_question(self, topic: str):
        """Generate WHERE questions."""
        table = random.choice(self.schema.tables)
        
        # Find a text or numeric column
        text_cols = [c for c in table.columns if 'char' in c.data_type.lower()]
        num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
        
        if text_cols:
            col = random.choice(text_cols)
            self._add_question(
                topic=topic,
                difficulty="Beginner",
                question=f"Find all {table.name} where {col.name} contains 'test'.",
                answer=f"SELECT * FROM {table.name} WHERE {col.name} LIKE '%test%';",
                explanation=f"LIKE with % performs a partial match on {col.name}.",
                tip="Use ILIKE for case-insensitive searches."
            )
        elif num_cols:
            col = random.choice(num_cols)
            value = random.randint(1, 100)
            self._add_question(
                topic=topic,
                difficulty="Beginner",
                question=f"Find all {table.name} where {col.name} > {value}.",
                answer=f"SELECT * FROM {table.name} WHERE {col.name} > {value};",
                explanation=f"Filters rows where {col.name} is greater than {value}.",
                tip="Use =, <>, <, >, <=, >= for numeric comparisons."
            )
    
    def _generate_order_by_question(self, topic: str):
        """Generate ORDER BY questions."""
        table = random.choice(self.schema.tables)
        col = random.choice(table.columns)
        
        orders = ['ASC', 'DESC']
        order = random.choice(orders)
        
        self._add_question(
            topic=topic,
            difficulty="Beginner",
            question=f"List all {table.name} ordered by {col.name} {order}.",
            answer=f"SELECT * FROM {table.name} ORDER BY {col.name} {order};",
            explanation=f"ORDER BY {col.name} {order} sorts from {'lowest to highest' if order == 'ASC' else 'highest to lowest'}.",
            tip="ORDER BY defaults to ASC if not specified."
        )
    
    def _generate_limit_question(self, topic: str):
        """Generate LIMIT questions."""
        table = random.choice(self.schema.tables)
        limit = random.choice([5, 10, 15, 20, 25])
        
        self._add_question(
            topic=topic,
            difficulty="Beginner",
            question=f"Show the first {limit} records from {table.name}.",
            answer=f"SELECT * FROM {table.name} LIMIT {limit};",
            explanation=f"LIMIT {limit} restricts output to {limit} rows.",
            tip="Use LIMIT with OFFSET for pagination."
        )
    
    def _generate_distinct_question(self, topic: str):
        """Generate DISTINCT questions."""
        table = random.choice(self.schema.tables)
        col = random.choice(table.columns)
        
        self._add_question(
            topic=topic,
            difficulty="Beginner",
            question=f"Show unique values of {col.name} from {table.name}.",
            answer=f"SELECT DISTINCT {col.name} FROM {table.name};",
            explanation=f"DISTINCT removes duplicate values from {col.name}.",
            tip="DISTINCT applies to all columns in the SELECT list."
        )
    
    # ==================== INTERMEDIATE QUESTION GENERATORS ====================
    
    def _generate_aggregation_question(self, topic: str):
        """Generate Aggregation questions."""
        table = random.choice(self.schema.tables)
        num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
        
        if not num_cols:
            return self._generate_group_by_question(topic)
        
        col = random.choice(num_cols)
        func = random.choice(['COUNT', 'SUM', 'AVG', 'MIN', 'MAX'])
        
        self._add_question(
            topic=topic,
            difficulty="Intermediate",
            question=f"Calculate the {func} of {col.name} from {table.name}.",
            answer=f"SELECT {func}({col.name}) FROM {table.name};",
            explanation=f"{func}() calculates the {func.lower()} of all {col.name} values.",
            tip=f"Use ROUND() with AVG to limit decimal places."
        )
    
    def _generate_group_by_question(self, topic: str):
        """Generate GROUP BY questions."""
        table = random.choice(self.schema.tables)
        
        # Find columns good for grouping
        group_cols = [c for c in table.columns if not c.primary_key and c.data_type in ['character varying', 'text', 'integer']]
        
        if not group_cols:
            group_cols = table.columns
        
        col = random.choice(group_cols)
        
        self._add_question(
            topic=topic,
            difficulty="Intermediate",
            question=f"Count the number of records in {table.name} grouped by {col.name}.",
            answer=f"SELECT {col.name}, COUNT(*) FROM {table.name} GROUP BY {col.name};",
            explanation=f"GROUP BY {col.name} creates groups and COUNT(*) counts each group.",
            tip="All non-aggregated columns in SELECT must be in GROUP BY."
        )
    
    def _generate_having_question(self, topic: str):
        """Generate HAVING questions."""
        table = random.choice(self.schema.tables)
        
        self._add_question(
            topic=topic,
            difficulty="Intermediate",
            question=f"Find groups in {table.name} with more than 5 records.",
            answer=f"SELECT some_column, COUNT(*) FROM {table.name} GROUP BY some_column HAVING COUNT(*) > 5;",
            explanation="HAVING filters groups after aggregation.",
            tip="Use WHERE for row filtering, HAVING for group filtering."
        )
    
    def _generate_join_question(self, topic: str):
        """Generate JOIN questions."""
        if len(self.schema.relationships) == 0:
            return self._generate_subquery_question(topic)
        
        rel = random.choice(self.schema.relationships)
        
        self._add_question(
            topic=topic,
            difficulty="Intermediate",
            question=f"Join {rel.source_table} with {rel.target_table}.",
            answer=f"SELECT * FROM {rel.source_table} JOIN {rel.target_table} ON {rel.source_table}.{rel.source_column} = {rel.target_table}.{rel.target_column};",
            explanation=f"INNER JOIN connects {rel.source_table} to {rel.target_table}.",
            tip="Use table aliases to make queries more readable."
        )
    
    def _generate_subquery_question(self, topic: str):
        """Generate Subquery questions."""
        table = random.choice(self.schema.tables)
        
        self._add_question(
            topic=topic,
            difficulty="Intermediate",
            question=f"Write a subquery to find records in {table.name} with a condition.",
            answer=f"SELECT * FROM {table.name} WHERE column IN (SELECT column FROM {table.name} WHERE condition);",
            explanation="Subqueries can be used in WHERE, FROM, or SELECT clauses.",
            tip="Subqueries can be slow; consider JOINs or CTEs for better performance."
        )
    
    # ==================== ADVANCED QUESTION GENERATORS ====================
    
    def _generate_window_question(self, topic: str):
        """Generate Window Function questions."""
        if not self.features['has_timestamps']:
            return self._generate_cte_question(topic)
        
        table = self.schema.get_table(random.choice(self.features['tables_with_timestamps']))
        if not table:
            return self._generate_cte_question(topic)
        
        time_cols = [c for c in table.columns if 'timestamp' in c.data_type.lower()]
        if not time_cols:
            return self._generate_cte_question(topic)
        
        col = random.choice(time_cols)
        
        self._add_question(
            topic=topic,
            difficulty="Advanced",
            question=f"Use ROW_NUMBER() to rank records in {table.name} by {col.name}.",
            answer=f"SELECT *, ROW_NUMBER() OVER (ORDER BY {col.name}) FROM {table.name};",
            explanation=f"ROW_NUMBER() assigns sequential numbers ordered by {col.name}.",
            tip="Use PARTITION BY to reset numbering for each group."
        )
    
    def _generate_cte_question(self, topic: str):
        """Generate CTE questions."""
        table = random.choice(self.schema.tables)
        
        self._add_question(
            topic=topic,
            difficulty="Advanced",
            question=f"Write a CTE to filter {table.name} and then query it.",
            answer=f"WITH filtered AS (SELECT * FROM {table.name} WHERE condition) SELECT * FROM filtered;",
            explanation="WITH creates a temporary named result set.",
            tip="CTEs make complex queries more readable and can be referenced multiple times."
        )
    
    def _generate_case_question(self, topic: str):
        """Generate CASE questions."""
        table = random.choice(self.schema.tables)
        
        self._add_question(
            topic=topic,
            difficulty="Advanced",
            question=f"Use CASE to categorize records in {table.name}.",
            answer=f"SELECT *, CASE WHEN condition THEN 'Category1' WHEN other_condition THEN 'Category2' ELSE 'Category3' END AS category FROM {table.name};",
            explanation="CASE creates conditional logic in SQL.",
            tip="CASE is evaluated in order; the first matching condition wins."
        )
    
    def _generate_date_question(self, topic: str):
        """Generate Date Function questions."""
        if not self.features['has_timestamps']:
            return self._generate_string_question(topic)
        
        table = self.schema.get_table(random.choice(self.features['tables_with_timestamps']))
        if not table:
            return self._generate_string_question(topic)
        
        time_cols = [c for c in table.columns if 'timestamp' in c.data_type.lower()]
        if not time_cols:
            return self._generate_string_question(topic)
        
        col = random.choice(time_cols)
        
        self._add_question(
            topic=topic,
            difficulty="Advanced",
            question=f"Extract the year from {col.name} in {table.name}.",
            answer=f"SELECT EXTRACT(YEAR FROM {col.name}) FROM {table.name};",
            explanation="EXTRACT(YEAR FROM ...) gets the year from a timestamp.",
            tip="Use DATE_TRUNC() for grouping by month, quarter, or year."
        )
    
    def _generate_string_question(self, topic: str):
        """Generate String Function questions."""
        table = random.choice(self.schema.tables)
        string_cols = [c for c in table.columns if 'char' in c.data_type.lower() or c.data_type == 'text']
        
        if not string_cols:
            return self._generate_cte_question(topic)
        
        col = random.choice(string_cols)
        
        self._add_question(
            topic=topic,
            difficulty="Advanced",
            question=f"Convert {col.name} to uppercase in {table.name}.",
            answer=f"SELECT UPPER({col.name}) FROM {table.name};",
            explanation="UPPER() converts text to uppercase.",
            tip="Use LOWER() for case-insensitive comparisons."
        )
    
    # ==================== EXPERT QUESTION GENERATORS ====================
    
    def _generate_json_question(self, topic: str):
        """Generate JSONB questions."""
        if not self.features['has_jsonb']:
            return self._generate_recursive_question(topic)
        
        table = self.schema.get_table(random.choice(self.features['tables_with_jsonb']))
        if not table:
            return self._generate_recursive_question(topic)
        
        json_cols = [c for c in table.columns if 'json' in c.data_type.lower()]
        if not json_cols:
            return self._generate_recursive_question(topic)
        
        col = random.choice(json_cols)
        
        self._add_question(
            topic=topic,
            difficulty="Expert",
            question=f"Extract a specific field from the JSONB column {col.name} in {table.name}.",
            answer=f"SELECT {col.name}->>'field_name' AS field FROM {table.name};",
            explanation=f"->> extracts a JSON field as text from {col.name}.",
            tip="Use -> for JSON objects and ->> for text values."
        )
    
    def _generate_recursive_question(self, topic: str):
        """Generate Recursive CTE questions."""
        if not self.features['has_recursive']:
            return self._generate_performance_question(topic)
        
        table = self.schema.get_table(random.choice(self.features['self_referencing_tables']))
        if not table:
            return self._generate_performance_question(topic)
        
        self._add_question(
            topic=topic,
            difficulty="Expert",
            question=f"Write a recursive CTE to traverse the hierarchy in {table.name}.",
            answer=f"WITH RECURSIVE hierarchy AS (SELECT * FROM {table.name} WHERE parent_id IS NULL UNION ALL SELECT child.* FROM {table.name} child JOIN hierarchy parent ON child.parent_id = parent.id) SELECT * FROM hierarchy;",
            explanation="Recursive CTE starts with root records and traverses the hierarchy.",
            tip="Add a depth limit to prevent infinite recursion."
        )
    
    def _generate_performance_question(self, topic: str):
        """Generate Performance/EXPLAIN questions."""
        table = random.choice(self.schema.tables)
        
        self._add_question(
            topic=topic,
            difficulty="Expert",
            question=f"Analyze the execution plan for a query on {table.name}.",
            answer=f"EXPLAIN ANALYZE SELECT * FROM {table.name} WHERE condition;",
            explanation="EXPLAIN ANALYZE shows the actual execution plan and timing.",
            tip="Look for Seq Scan, Index Scan, and Nested Loop to understand performance."
        )
    
    def _generate_advanced_join_question(self, topic: str):
        """Generate Advanced JOIN questions."""
        if len(self.schema.tables) < 3:
            return self._generate_performance_question(topic)
        
        tables = random.sample(self.schema.tables, min(3, len(self.schema.tables)))
        
        self._add_question(
            topic=topic,
            difficulty="Expert",
            question=f"Join three tables: {', '.join([t.name for t in tables])}.",
            answer=f"SELECT * FROM {tables[0].name} JOIN {tables[1].name} ON {tables[0].name}.id = {tables[1].name}.{tables[0].name}_id JOIN {tables[2].name} ON {tables[1].name}.id = {tables[2].name}.{tables[1].name}_id;",
            explanation="Multiple JOINs connect three or more tables.",
            tip="Use LEFT JOIN if you want to keep all rows from the left table."
        )
