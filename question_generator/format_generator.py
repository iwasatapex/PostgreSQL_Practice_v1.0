"""
question_generator/format_generator.py

Generates SQL questions with gradual difficulty progression
from Beginner to Expert using the specified format.
"""

import random
from typing import List, Dict, Any
from models.schema import Schema
from models.question import Question
from parser.schema_analyzer import SchemaAnalyzer


class FormatQuestionGenerator:
    """Generates SQL questions with gradual difficulty progression."""
    
    def __init__(self, schema: Schema):
        self.schema = schema
        self.analyzer = SchemaAnalyzer(schema)
        self.questions: List[Question] = []
        self.counter = 0
        self.features = self.analyzer.detect_features()
        
        # Progressive difficulty levels
        self.difficulty_levels = [
            'Beginner',
            'Intermediate',
            'Advanced',
            'Expert'
        ]
    
    def generate_all(self, target_count: int = 1000) -> List[Question]:
        """Generate questions with gradual difficulty progression."""
        
        print(f"\n🎯 Generating {target_count} questions with gradual difficulty...")
        
        # Calculate distribution (gradual increase)
        # Beginner: 25%, Intermediate: 35%, Advanced: 25%, Expert: 15%
        distribution = {
            'Beginner': int(target_count * 0.25),
            'Intermediate': int(target_count * 0.35),
            'Advanced': int(target_count * 0.25),
            'Expert': int(target_count * 0.15)
        }
        
        # Adjust for rounding
        total = sum(distribution.values())
        if total < target_count:
            distribution['Beginner'] += target_count - total
        
        print(f"📊 Difficulty Distribution:")
        for level, count in distribution.items():
            print(f"  - {level}: {count} questions")
        
        # Generate questions by difficulty
        self._generate_beginner_questions(distribution['Beginner'])
        self._generate_intermediate_questions(distribution['Intermediate'])
        self._generate_advanced_questions(distribution['Advanced'])
        self._generate_expert_questions(distribution['Expert'])
        
        # Sort by difficulty (Beginner → Expert)
        difficulty_order = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2, 'Expert': 3}
        self.questions.sort(key=lambda q: difficulty_order.get(q.difficulty, 0))
        
        # Reassign IDs
        for i, q in enumerate(self.questions, 1):
            q.id = i
        
        print(f"✅ Generated {len(self.questions)} questions")
        return self.questions
    
    def _add_question(self, topic: str, difficulty: str, question: str,
                      answer: str, explanation: str, tip: str):
        """Add a question in the specified format."""
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
    
    # ==================== BEGINNER QUESTIONS (Level 1) ====================
    
    def _generate_beginner_questions(self, count: int):
        """Generate Beginner level questions (simple SELECT, WHERE, ORDER BY)."""
        
        templates = []
        
        for table in self.schema.tables:
            # SELECT all
            templates.append({
                'topic': 'SELECT',
                'question': f"List all records from the {table.name} table.",
                'answer': f"SELECT * FROM {table.name};",
                'explanation': f"SELECT * returns every column and row from the {table.name} table.",
                'tip': "Use specific columns instead of SELECT * in production."
            })
            
            # SELECT specific columns
            if len(table.columns) >= 2:
                cols = [c.name for c in table.columns[:3]]
                templates.append({
                    'topic': 'SELECT',
                    'question': f"Display only the {', '.join(cols)} columns from the {table.name} table.",
                    'answer': f"SELECT {', '.join(cols)} FROM {table.name};",
                    'explanation': f"SELECT with specific columns returns only the specified columns from {table.name}.",
                    'tip': "Specifying columns improves performance and readability."
                })
            
            # WHERE with text column
            text_cols = [c for c in table.columns if 'char' in c.data_type.lower() or c.data_type == 'text']
            if text_cols:
                col = text_cols[0]
                templates.append({
                    'topic': 'WHERE',
                    'question': f"Find all records in {table.name} where {col.name} contains the word 'test'.",
                    'answer': f"SELECT * FROM {table.name} WHERE {col.name} LIKE '%test%';",
                    'explanation': f"LIKE with % performs a partial match on the {col.name} column.",
                    'tip': "Use ILIKE for case-insensitive searches in PostgreSQL."
                })
            
            # WHERE with numeric column
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal', 'bigint']]
            if num_cols:
                col = num_cols[0]
                value = random.randint(10, 100)
                templates.append({
                    'topic': 'WHERE',
                    'question': f"Find all records in {table.name} where {col.name} is greater than {value}.",
                    'answer': f"SELECT * FROM {table.name} WHERE {col.name} > {value};",
                    'explanation': f"Filters rows where {col.name} is greater than {value}.",
                    'tip': "Use >, <, >=, <=, =, != for numeric comparisons."
                })
            
            # ORDER BY
            if table.columns:
                col = table.columns[0]
                templates.append({
                    'topic': 'ORDER BY',
                    'question': f"List all records from {table.name} sorted by {col.name} in ascending order.",
                    'answer': f"SELECT * FROM {table.name} ORDER BY {col.name} ASC;",
                    'explanation': f"ORDER BY {col.name} ASC sorts from lowest to highest.",
                    'tip': "ORDER BY defaults to ASC if not specified."
                })
            
            # LIMIT
            limit = random.choice([5, 10, 15])
            templates.append({
                'topic': 'LIMIT',
                'question': f"Show only the first {limit} records from the {table.name} table.",
                'answer': f"SELECT * FROM {table.name} LIMIT {limit};",
                'explanation': f"LIMIT {limit} restricts the output to {limit} rows.",
                'tip': "Use LIMIT with OFFSET for pagination."
            })
            
            # DISTINCT
            text_cols = [c for c in table.columns if 'char' in c.data_type.lower() or c.data_type == 'text']
            if text_cols:
                col = text_cols[0]
                templates.append({
                    'topic': 'DISTINCT',
                    'question': f"Show all unique values of the {col.name} column from the {table.name} table.",
                    'answer': f"SELECT DISTINCT {col.name} FROM {table.name};",
                    'explanation': f"DISTINCT removes duplicate values from the {col.name} column.",
                    'tip': "DISTINCT applies to all columns in the SELECT list."
                })
        
        # Select random templates up to count
        selected = random.sample(templates, min(count, len(templates))) if templates else []
        
        # If we need more questions, repeat with variations
        while len(selected) < count and templates:
            for template in templates[:]:
                if len(selected) >= count:
                    break
                # Create variation
                variation = template.copy()
                if 'LIMIT' in variation['topic']:
                    variation['limit'] = random.choice([5, 10, 15, 20, 25])
                    variation['question'] = variation['question'].replace(str(template.get('limit', 10)), str(variation['limit']))
                selected.append(variation)
        
        for template in selected[:count]:
            self._add_question(
                topic=template['topic'],
                difficulty="Beginner",
                question=template['question'],
                answer=template['answer'],
                explanation=template['explanation'],
                tip=template['tip']
            )
    
    # ==================== INTERMEDIATE QUESTIONS (Level 2) ====================
    
    def _generate_intermediate_questions(self, count: int):
        """Generate Intermediate level questions (Aggregations, GROUP BY, JOINs)."""
        
        templates = []
        
        # Aggregations (COUNT, SUM, AVG)
        for table in self.schema.tables:
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal', 'bigint']]
            if num_cols:
                col = num_cols[0]
                funcs = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']
                for func in funcs:
                    templates.append({
                        'topic': 'Aggregation',
                        'question': f"Calculate the {func} of the {col.name} column from the {table.name} table.",
                        'answer': f"SELECT {func}({col.name}) FROM {table.name};",
                        'explanation': f"{func}() calculates the {func.lower()} of all {col.name} values.",
                        'tip': f"Use ROUND() with AVG to limit decimal places."
                    })
        
        # GROUP BY
        for table in self.schema.tables:
            group_cols = [c for c in table.columns if not c.primary_key and c.data_type in ['character varying', 'text', 'integer']]
            if group_cols:
                col = group_cols[0]
                templates.append({
                    'topic': 'GROUP BY',
                    'question': f"Count the number of records in the {table.name} table, grouped by the {col.name} column.",
                    'answer': f"SELECT {col.name}, COUNT(*) FROM {table.name} GROUP BY {col.name};",
                    'explanation': f"GROUP BY {col.name} creates groups and COUNT(*) counts each group.",
                    'tip': "All non-aggregated columns in SELECT must be in GROUP BY."
                })
        
        # HAVING
        for table in self.schema.tables:
            group_cols = [c for c in table.columns if not c.primary_key and c.data_type in ['character varying', 'text']]
            if group_cols:
                col = group_cols[0]
                templates.append({
                    'topic': 'HAVING',
                    'question': f"Find groups in the {table.name} table that have more than 5 records.",
                    'answer': f"SELECT {col.name}, COUNT(*) FROM {table.name} GROUP BY {col.name} HAVING COUNT(*) > 5;",
                    'explanation': "HAVING filters groups after aggregation.",
                    'tip': "Use WHERE for row filtering, HAVING for group filtering."
                })
        
        # JOINs
        for rel in self.schema.relationships:
            templates.append({
                'topic': 'JOIN',
                'question': f"Join the {rel.source_table} table with the {rel.target_table} table.",
                'answer': f"SELECT * FROM {rel.source_table} JOIN {rel.target_table} ON {rel.source_table}.{rel.source_column} = {rel.target_table}.{rel.target_column};",
                'explanation': f"INNER JOIN connects {rel.source_table} to {rel.target_table} on the foreign key relationship.",
                'tip': "Use table aliases to make queries more readable and concise."
            })
        
        # Subqueries
        for table in self.schema.tables:
            templates.append({
                'topic': 'Subquery',
                'question': f"Write a subquery to find records in the {table.name} table based on a condition.",
                'answer': f"SELECT * FROM {table.name} WHERE column IN (SELECT column FROM {table.name} WHERE condition);",
                'explanation': "Subqueries can be used in WHERE, FROM, or SELECT clauses.",
                'tip': "Subqueries can be slow; consider JOINs or CTEs for better performance."
            })
        
        # Select random templates
        selected = random.sample(templates, min(count, len(templates))) if templates else []
        
        while len(selected) < count and templates:
            for template in templates[:]:
                if len(selected) >= count:
                    break
                selected.append(template)
        
        for template in selected[:count]:
            self._add_question(
                topic=template['topic'],
                difficulty="Intermediate",
                question=template['question'],
                answer=template['answer'],
                explanation=template['explanation'],
                tip=template['tip']
            )
    
    # ==================== ADVANCED QUESTIONS (Level 3) ====================
    
    def _generate_advanced_questions(self, count: int):
        """Generate Advanced level questions (Window Functions, CTEs, CASE)."""
        
        templates = []
        
        # Window Functions (if timestamps exist)
        if self.features['has_timestamps']:
            for table_name in self.features['tables_with_timestamps']:
                table = self.schema.get_table(table_name)
                if table:
                    time_cols = [c for c in table.columns if 'timestamp' in c.data_type.lower()]
                    if time_cols:
                        col = time_cols[0]
                        templates.append({
                            'topic': 'Window Functions',
                            'question': f"Use ROW_NUMBER() to assign a sequential number to each record in the {table.name} table, ordered by {col.name}.",
                            'answer': f"SELECT *, ROW_NUMBER() OVER (ORDER BY {col.name}) FROM {table.name};",
                            'explanation': f"ROW_NUMBER() assigns sequential numbers to rows ordered by {col.name}.",
                            'tip': "Use PARTITION BY to reset numbering for each group."
                        })
                        
                        templates.append({
                            'topic': 'Window Functions',
                            'question': f"Calculate a running total of a numeric column in the {table.name} table.",
                            'answer': f"SELECT *, SUM(numeric_column) OVER (ORDER BY {col.name}) FROM {table.name};",
                            'explanation': f"SUM() OVER creates a cumulative total without GROUP BY.",
                            'tip': "Running totals are useful for financial and inventory analysis."
                        })
        
        # CTEs
        for table in self.schema.tables:
            templates.append({
                'topic': 'CTE',
                'question': f"Write a CTE to filter the {table.name} table and then query the result.",
                'answer': f"WITH filtered AS (SELECT * FROM {table.name} WHERE condition) SELECT * FROM filtered;",
                'explanation': "WITH creates a temporary named result set that can be referenced in the main query.",
                'tip': "CTEs make complex queries more readable and can be referenced multiple times."
            })
        
        # CASE
        for table in self.schema.tables:
            templates.append({
                'topic': 'CASE',
                'question': f"Use CASE to categorize records in the {table.name} table into multiple categories.",
                'answer': f"SELECT *, CASE WHEN condition THEN 'Category1' WHEN other_condition THEN 'Category2' ELSE 'Category3' END AS category FROM {table.name};",
                'explanation': "CASE creates conditional logic in SQL.",
                'tip': "CASE is evaluated in order; the first matching condition wins."
            })
        
        # Date Functions
        if self.features['has_timestamps']:
            for table_name in self.features['tables_with_timestamps']:
                table = self.schema.get_table(table_name)
                if table:
                    time_cols = [c for c in table.columns if 'timestamp' in c.data_type.lower()]
                    if time_cols:
                        col = time_cols[0]
                        templates.append({
                            'topic': 'Date Functions',
                            'question': f"Extract the year from the {col.name} column in the {table.name} table.",
                            'answer': f"SELECT EXTRACT(YEAR FROM {col.name}) FROM {table.name};",
                            'explanation': "EXTRACT(YEAR FROM ...) gets the year from a timestamp.",
                            'tip': "Use DATE_TRUNC() for grouping by month, quarter, or year."
                        })
                        
                        templates.append({
                            'topic': 'Date Functions',
                            'question': f"Find all records in the {table.name} table from the last 30 days.",
                            'answer': f"SELECT * FROM {table.name} WHERE {col.name} >= NOW() - INTERVAL '30 days';",
                            'explanation': "NOW() - INTERVAL gets records from the last 30 days.",
                            'tip': "Use CURRENT_DATE for date-only comparisons."
                        })
        
        # String Functions
        for table in self.schema.tables:
            string_cols = [c for c in table.columns if 'char' in c.data_type.lower() or c.data_type == 'text']
            if string_cols:
                col = string_cols[0]
                templates.append({
                    'topic': 'String Functions',
                    'question': f"Convert the {col.name} column to uppercase in the {table.name} table.",
                    'answer': f"SELECT UPPER({col.name}) FROM {table.name};",
                    'explanation': "UPPER() converts text to uppercase.",
                    'tip': "Use LOWER() for case-insensitive comparisons."
                })
                
                templates.append({
                    'topic': 'String Functions',
                    'question': f"Find the length of the {col.name} column in the {table.name} table.",
                    'answer': f"SELECT LENGTH({col.name}) FROM {table.name};",
                    'explanation': "LENGTH() returns the number of characters in a string.",
                    'tip': "Use CHAR_LENGTH() for multi-byte character count."
                })
        
        # Select random templates
        selected = random.sample(templates, min(count, len(templates))) if templates else []
        
        while len(selected) < count and templates:
            for template in templates[:]:
                if len(selected) >= count:
                    break
                selected.append(template)
        
        for template in selected[:count]:
            self._add_question(
                topic=template['topic'],
                difficulty="Advanced",
                question=template['question'],
                answer=template['answer'],
                explanation=template['explanation'],
                tip=template['tip']
            )
    
    # ==================== EXPERT QUESTIONS (Level 4) ====================
    
    def _generate_expert_questions(self, count: int):
        """Generate Expert level questions (JSONB, Recursive CTEs, Performance)."""
        
        templates = []
        
        # JSONB (if available)
        if self.features['has_jsonb']:
            for table_name in self.features['tables_with_jsonb']:
                table = self.schema.get_table(table_name)
                if table:
                    json_cols = [c for c in table.columns if 'json' in c.data_type.lower()]
                    if json_cols:
                        col = json_cols[0]
                        templates.append({
                            'topic': 'JSONB',
                            'question': f"Extract a specific field from the JSONB column {col.name} in the {table.name} table.",
                            'answer': f"SELECT {col.name}->>'field_name' AS field FROM {table.name};",
                            'explanation': f"->> extracts a JSON field as text from the {col.name} column.",
                            'tip': "Use -> for JSON objects and ->> for text values."
                        })
                        
                        templates.append({
                            'topic': 'JSONB',
                            'question': f"Find all records in the {table.name} table where a JSONB field equals a specific value.",
                            'answer': f"SELECT * FROM {table.name} WHERE {col.name}->>'field_name' = 'value';",
                            'explanation': f"Uses JSONB extraction to filter rows based on JSON field values.",
                            'tip': "JSONB supports containment operators: @> to check if JSON contains key-value pairs."
                        })
        
        # Recursive CTEs (if self-referencing)
        if self.features['has_recursive']:
            for table_name in self.features['self_referencing_tables']:
                table = self.schema.get_table(table_name)
                if table:
                    templates.append({
                        'topic': 'Recursive CTE',
                        'question': f"Write a recursive CTE to traverse the hierarchy in the {table.name} table.",
                        'answer': f"WITH RECURSIVE hierarchy AS (SELECT * FROM {table.name} WHERE parent_id IS NULL UNION ALL SELECT child.* FROM {table.name} child JOIN hierarchy parent ON child.parent_id = parent.id) SELECT * FROM hierarchy;",
                        'explanation': "Recursive CTE starts with root records (no parent) and traverses the hierarchy.",
                        'tip': "The anchor (first SELECT) defines the starting point; the recursive part adds children."
                    })
        
        # Performance
        for table in self.schema.tables:
            templates.append({
                'topic': 'Performance',
                'question': f"Analyze the execution plan for a query on the {table.name} table.",
                'answer': f"EXPLAIN ANALYZE SELECT * FROM {table.name} WHERE condition;",
                'explanation': "EXPLAIN ANALYZE shows the actual execution plan and timing.",
                'tip': "Look for Seq Scan, Index Scan, and Nested Loop to understand performance."
            })
        
        # Advanced JOINs (3+ tables)
        if len(self.schema.tables) >= 3:
            tables = random.sample(self.schema.tables, min(3, len(self.schema.tables)))
            table_names = [t.name for t in tables]
            templates.append({
                'topic': 'Advanced JOIN',
                'question': f"Write a query that joins three tables: {', '.join(table_names)}.",
                'answer': f"SELECT * FROM {table_names[0]} JOIN {table_names[1]} ON {table_names[0]}.id = {table_names[1]}.{table_names[0]}_id JOIN {table_names[2]} ON {table_names[1]}.id = {table_names[2]}.{table_names[1]}_id;",
                'explanation': "Multiple JOINs connect three or more tables based on foreign key relationships.",
                'tip': "Use LEFT JOIN if you want to keep all rows from the left table."
            })
        
        # Select random templates
        selected = random.sample(templates, min(count, len(templates))) if templates else []
        
        while len(selected) < count and templates:
            for template in templates[:]:
                if len(selected) >= count:
                    break
                selected.append(template)
        
        for template in selected[:count]:
            self._add_question(
                topic=template['topic'],
                difficulty="Expert",
                question=template['question'],
                answer=template['answer'],
                explanation=template['explanation'],
                tip=template['tip']
            )
