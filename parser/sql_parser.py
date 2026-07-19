"""
parser/sql_parser.py

Parses SQL files and builds schema models.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict

from models.table import Table
from models.column import Column
from models.relationship import Relationship
from models.schema import Schema


class SQLParser:
    """Parses SQL files and builds a complete schema model."""

    def __init__(self, sql_file: str):
        self.sql_file = Path(sql_file)
        self.schema = Schema()
        self.current_table: Optional[Table] = None
        self.foreign_keys: List[Dict] = []

    def parse(self) -> Schema:
        """Parse the SQL file and return a Schema object."""
        
        if not self.sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {self.sql_file}")
        
        with open(self.sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove comments
        content = self._remove_comments(content)
        
        # Parse CREATE TABLE statements
        self._parse_create_tables(content)
        
        # Parse foreign keys (both inline and constraint)
        self._parse_foreign_keys(content)
        
        # Parse primary key constraints
        self._parse_constraint_primary_keys(content)
        
        # Parse indexes
        self._parse_indexes(content)
        
        # Build relationships
        self._build_relationships()
        
        return self.schema

    def _remove_comments(self, sql: str) -> str:
        """Remove SQL comments."""
        # Remove -- single line comments
        sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)
        # Remove /* */ multi-line comments
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        return sql

    def _parse_create_tables(self, sql: str):
        """Parse all CREATE TABLE statements."""
        
        # Pattern for CREATE TABLE
        pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\);'
        
        matches = re.findall(pattern, sql, re.IGNORECASE | re.DOTALL)
        
        for table_name, columns_sql in matches:
            table = Table(name=table_name.lower())
            
            # Parse columns
            self._parse_columns(table, columns_sql)
            
            self.schema.tables.append(table)

    def _parse_columns(self, table: Table, columns_sql: str):
        """Parse column definitions within a CREATE TABLE."""
        
        # Split by commas, respecting parentheses
        column_defs = self._split_columns(columns_sql)
        
        for col_def in column_defs:
            col_def = col_def.strip()
            
            # Skip constraint definitions
            if self._is_constraint(col_def):
                continue
            
            # Parse column
            column = self._parse_column_definition(col_def)
            
            if column:
                table.columns.append(column)

    def _split_columns(self, columns_sql: str) -> List[str]:
        """Split column definitions by comma, respecting parentheses."""
        
        parts = []
        current = []
        paren_count = 0
        
        for char in columns_sql:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                parts.append(''.join(current).strip())
                current = []
                continue
            
            current.append(char)
        
        if current:
            parts.append(''.join(current).strip())
        
        return parts

    def _is_constraint(self, text: str) -> bool:
        """Check if text is a constraint definition."""
        text_upper = text.upper().strip()
        constraints = [
            'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 
            'CHECK', 'CONSTRAINT', 'REFERENCES'
        ]
        return any(text_upper.startswith(c) for c in constraints)

    def _parse_column_definition(self, col_def: str) -> Optional[Column]:
        """Parse a single column definition."""
        
        col_def = col_def.strip()
        
        # Match column name and data type
        pattern = r'^(\w+)\s+([A-Za-z_]+(?:\([^)]*\))?)'
        match = re.match(pattern, col_def, re.IGNORECASE)
        
        if not match:
            return None
        
        col_name = match.group(1).lower()
        data_type = match.group(2).lower()
        
        # Check constraints
        col_upper = col_def.upper()
        is_primary_key = 'PRIMARY KEY' in col_upper
        is_nullable = 'NOT NULL' not in col_upper
        is_unique = 'UNIQUE' in col_upper
        
        # Check for default
        default_match = re.search(r'DEFAULT\s+([^,]+?)(?:\s+NOT\s+NULL|\s+NULL|,|$)', 
                                  col_def, re.IGNORECASE)
        default_value = default_match.group(1).strip() if default_match else None
        
        return Column(
            name=col_name,
            data_type=data_type,
            nullable=is_nullable,
            default=default_value,
            primary_key=is_primary_key,
            foreign_key=False,
            unique=is_unique
        )

    def _parse_foreign_keys(self, sql: str):
        """Parse FOREIGN KEY constraints."""
        
        # Pattern for inline foreign key
        inline_pattern = r'(\w+)\s+\w+(?:\([^)]*\))?\s+REFERENCES\s+(\w+)\s*\((\w+)\)'
        
        for match in re.finditer(inline_pattern, sql, re.IGNORECASE):
            source_col = match.group(1).lower()
            target_table = match.group(2).lower()
            target_col = match.group(3).lower()
            
            # Find the table that contains this column
            for table in self.schema.tables:
                for col in table.columns:
                    if col.name == source_col:
                        col.foreign_key = True
                        break
            
            self.foreign_keys.append({
                'source_column': source_col,
                'target_table': target_table,
                'target_column': target_col
            })
        
        # Pattern for constraint foreign key
        constraint_pattern = r'FOREIGN\s+KEY\s*\((\w+)\)\s+REFERENCES\s+(\w+)\s*\((\w+)\)'
        
        for match in re.finditer(constraint_pattern, sql, re.IGNORECASE):
            source_col = match.group(1).lower()
            target_table = match.group(2).lower()
            target_col = match.group(3).lower()
            
            for table in self.schema.tables:
                for col in table.columns:
                    if col.name == source_col:
                        col.foreign_key = True
                        break
            
            self.foreign_keys.append({
                'source_column': source_col,
                'target_table': target_table,
                'target_column': target_col
            })

    def _parse_constraint_primary_keys(self, sql: str):
        """Parse PRIMARY KEY constraints."""
        
        pattern = r'PRIMARY\s+KEY\s*\(([^)]+)\)'
        
        for match in re.finditer(pattern, sql, re.IGNORECASE):
            columns = [c.strip().lower() for c in match.group(1).split(',')]
            
            # Find tables that have these columns
            for table in self.schema.tables:
                for col_name in columns:
                    for col in table.columns:
                        if col.name == col_name:
                            col.primary_key = True

    def _parse_indexes(self, sql: str):
        """Parse CREATE INDEX statements."""
        
        pattern = r'CREATE\s+INDEX\s+(\w+)\s+ON\s+(\w+)\s*\(([^)]+)\)'
        
        for match in re.finditer(pattern, sql, re.IGNORECASE):
            index_name = match.group(1)
            table_name = match.group(2).lower()
            columns = [c.strip().lower() for c in match.group(3).split(',')]
            
            # Store index info on the table
            table = self.schema.get_table(table_name)
            if table:
                if not hasattr(table, 'indexes'):
                    table.indexes = []
                table.indexes.append({
                    'name': index_name,
                    'columns': columns
                })

    def _build_relationships(self):
        """Build relationship objects from parsed foreign keys."""
        
        for fk in self.foreign_keys:
            source_table = self._find_source_table(fk['source_column'])
            
            self.schema.relationships.append(
                Relationship(
                    source_table=source_table,
                    source_column=fk['source_column'],
                    target_table=fk['target_table'],
                    target_column=fk['target_column']
                )
            )

    def _find_source_table(self, column_name: str) -> str:
        """Find which table a column belongs to."""
        for table in self.schema.tables:
            for col in table.columns:
                if col.name == column_name:
                    return table.name
        return "unknown"
