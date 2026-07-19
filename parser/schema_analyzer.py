"""
parser/schema_analyzer.py

Analyzes schema and detects patterns for question generation.
"""

from typing import List, Dict
from models.schema import Schema


class SchemaAnalyzer:
    """Analyzes schema to detect patterns and features."""
    
    def __init__(self, schema: Schema):
        self.schema = schema
    
    def detect_features(self) -> Dict[str, any]:
        """Detect all features in the schema."""
        
        features = {
            'has_jsonb': False,
            'has_timestamps': False,
            'has_recursive': False,
            'has_joins': False,
            'has_aggregates': False,
            'has_window_functions': False,
            'tables_with_jsonb': [],
            'tables_with_timestamps': [],
            'self_referencing_tables': [],
            'join_candidates': [],
            'aggregate_candidates': []
        }
        
        # Check for JSONB
        for table in self.schema.tables:
            for col in table.columns:
                if 'json' in col.data_type.lower():
                    features['has_jsonb'] = True
                    features['tables_with_jsonb'].append(table.name)
                    break
        
        # Check for timestamps
        for table in self.schema.tables:
            for col in table.columns:
                if 'timestamp' in col.data_type.lower():
                    features['has_timestamps'] = True
                    features['tables_with_timestamps'].append(table.name)
                    break
        
        # Check for self-referencing
        for rel in self.schema.relationships:
            if rel.source_table.lower() == rel.target_table.lower():
                features['has_recursive'] = True
                features['self_referencing_tables'].append(rel.source_table)
        
        # Check for join candidates (tables with foreign keys)
        for table in self.schema.tables:
            has_fk = False
            for col in table.columns:
                if col.foreign_key:
                    has_fk = True
                    break
            if has_fk:
                features['join_candidates'].append(table.name)
        
        # Check for aggregate candidates (tables with numeric columns)
        for table in self.schema.tables:
            for col in table.columns:
                if col.data_type in ['integer', 'numeric', 'decimal', 'bigint']:
                    if not col.primary_key and not col.foreign_key:
                        features['has_aggregates'] = True
                        features['aggregate_candidates'].append(table.name)
                        break
        
        return features
    
    def get_table_complexity(self, table) -> int:
        """Calculate table complexity score."""
        
        score = 0
        
        # Columns
        score += len(table.columns) * 2
        
        # Primary keys
        for col in table.columns:
            if col.primary_key:
                score += 5
        
        # Foreign keys
        for col in table.columns:
            if col.foreign_key:
                score += 3
        
        # Data types
        for col in table.columns:
            if 'json' in col.data_type.lower():
                score += 4
            if 'timestamp' in col.data_type.lower():
                score += 2
        
        return score
    
    def get_question_topics(self) -> Dict[str, List[str]]:
        """Get topics for question generation."""
        
        topics = {
            'beginner': [],
            'intermediate': [],
            'advanced': [],
            'expert': []
        }
        
        # Basic queries (beginner)
        for table in self.schema.tables:
            topics['beginner'].append(f"SELECT * FROM {table.name}")
            topics['beginner'].append(f"SELECT specific columns FROM {table.name}")
            topics['beginner'].append(f"WHERE filters on {table.name}")
            topics['beginner'].append(f"ORDER BY on {table.name}")
        
        # Joins (intermediate)
        for rel in self.schema.relationships:
            topics['intermediate'].append(
                f"JOIN {rel.source_table} with {rel.target_table}"
            )
        
        # Aggregates (intermediate)
        for table in self.schema.tables:
            for col in table.columns:
                if col.data_type in ['integer', 'numeric', 'decimal']:
                    if not col.primary_key and not col.foreign_key:
                        topics['intermediate'].append(
                            f"COUNT, SUM, AVG on {table.name}.{col.name}"
                        )
                        break
        
        # Window functions (advanced)
        for table in self.schema.tables:
            has_timestamp = False
            for col in table.columns:
                if 'timestamp' in col.data_type.lower():
                    has_timestamp = True
                    break
            if has_timestamp:
                topics['advanced'].append(
                    f"Window functions on {table.name} with timestamps"
                )
        
        # JSONB (expert)
        for table in self.schema.tables:
            for col in table.columns:
                if 'json' in col.data_type.lower():
                    topics['expert'].append(
                        f"JSONB queries on {table.name}.{col.name}"
                    )
                    break
        
        # Recursive CTE (expert)
        for rel in self.schema.relationships:
            if rel.source_table.lower() == rel.target_table.lower():
                topics['expert'].append(
                    f"Recursive CTE on {rel.source_table}"
                )
                break
        
        return topics
