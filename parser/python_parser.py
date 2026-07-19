"""
parser/python_parser.py

Parses Python files to extract SQL schema information.
Supports SQLAlchemy models, Django models, and raw SQL strings.
"""

import re
import ast
from pathlib import Path
from typing import List, Optional, Dict

from models.table import Table
from models.column import Column
from models.relationship import Relationship
from models.schema import Schema


class PythonParser:
    """Parses Python files and extracts SQL schema."""
    
    def __init__(self, python_file: str):
        self.python_file = Path(python_file)
        self.schema = Schema()
        self.tables: Dict[str, Table] = {}
        self.relationships: List[Dict] = []
    
    def parse(self) -> Schema:
        """Parse the Python file and return a Schema object."""
        
        if not self.python_file.exists():
            raise FileNotFoundError(f"Python file not found: {self.python_file}")
        
        with open(self.python_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as AST
        try:
            tree = ast.parse(content)
            self._parse_ast(tree)
        except SyntaxError:
            # If AST fails, try regex-based parsing
            self._parse_with_regex(content)
        
        # Build relationships
        self._build_relationships()
        
        return self.schema
    
    def _parse_ast(self, tree: ast.AST):
        """Parse Python AST to find SQLAlchemy/Django models."""
        
        for node in ast.walk(tree):
            # SQLAlchemy Model
            if isinstance(node, ast.ClassDef):
                # Check if it's a SQLAlchemy model
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id == 'Base' or 'Model' in base.id:
                            self._parse_sqlalchemy_model(node)
                            break
                
                # Check if it's a Django model
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        if 'models.Model' in ast.unparse(base):
                            self._parse_django_model(node)
                            break
    
    def _parse_sqlalchemy_model(self, node: ast.ClassDef):
        """Parse SQLAlchemy model class."""
        
        table_name = node.name.lower()
        table = Table(name=table_name)
        
        # Look for __tablename__
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == '__tablename__':
                        if isinstance(item.value, ast.Constant):
                            table.name = item.value.value
                            break
        
        # Parse columns
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        col_name = target.id
                        # Check if it's a Column
                        if isinstance(item.value, ast.Call):
                            # Check if it's a Column
                            if isinstance(item.value.func, ast.Name):
                                if item.value.func.id == 'Column':
                                    col = self._parse_sqlalchemy_column(col_name, item.value)
                                    table.columns.append(col)
        
        # Parse relationships
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        # Check for relationship
                        if isinstance(item.value, ast.Call):
                            if isinstance(item.value.func, ast.Name):
                                if item.value.func.id == 'relationship':
                                    self._parse_relationship(target.id, item.value)
        
        self.schema.tables.append(table)
        self.tables[table.name] = table
    
    def _parse_sqlalchemy_column(self, name: str, call: ast.Call) -> Column:
        """Parse SQLAlchemy Column definition."""
        
        data_type = "VARCHAR"  # Default
        primary_key = False
        nullable = True
        default = None
        
        # Get the column type
        if call.args:
            arg = call.args[0]
            if isinstance(arg, ast.Name):
                data_type = arg.id.upper()
            elif isinstance(arg, ast.Attribute):
                data_type = arg.attr.upper()
        
        # Check keyword arguments
        for kw in call.keywords:
            if kw.arg == 'primary_key':
                if isinstance(kw.value, ast.Constant):
                    primary_key = kw.value.value
            elif kw.arg == 'nullable':
                if isinstance(kw.value, ast.Constant):
                    nullable = kw.value.value
            elif kw.arg == 'default':
                if isinstance(kw.value, ast.Constant):
                    default = str(kw.value.value)
        
        return Column(
            name=name,
            data_type=data_type,
            nullable=nullable,
            default=default,
            primary_key=primary_key,
            foreign_key=False
        )
    
    def _parse_django_model(self, node: ast.ClassDef):
        """Parse Django model class."""
        
        table_name = node.name.lower()
        table = Table(name=table_name)
        
        # Parse fields
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        col_name = target.id
                        # Check if it's a Django field
                        if isinstance(item.value, ast.Call):
                            if isinstance(item.value.func, ast.Attribute):
                                if 'models.' in ast.unparse(item.value.func):
                                    field_type = item.value.func.attr
                                    col = self._parse_django_field(col_name, field_type, item.value)
                                    table.columns.append(col)
        
        self.schema.tables.append(table)
        self.tables[table.name] = table
    
    def _parse_django_field(self, name: str, field_type: str, call: ast.Call) -> Column:
        """Parse Django field definition."""
        
        primary_key = False
        nullable = True
        default = None
        
        # Map Django field types to SQL types
        type_mapping = {
            'CharField': 'VARCHAR',
            'TextField': 'TEXT',
            'IntegerField': 'INTEGER',
            'BigIntegerField': 'BIGINT',
            'FloatField': 'FLOAT',
            'DecimalField': 'DECIMAL',
            'BooleanField': 'BOOLEAN',
            'DateField': 'DATE',
            'DateTimeField': 'TIMESTAMP',
            'EmailField': 'VARCHAR',
            'URLField': 'VARCHAR',
            'JSONField': 'JSONB',
            'ForeignKey': 'INTEGER',
            'ManyToManyField': 'INTEGER'
        }
        
        data_type = type_mapping.get(field_type, 'VARCHAR')
        
        # Check keyword arguments
        for kw in call.keywords:
            if kw.arg == 'primary_key':
                if isinstance(kw.value, ast.Constant):
                    primary_key = kw.value.value
            elif kw.arg == 'null':
                if isinstance(kw.value, ast.Constant):
                    nullable = kw.value.value
            elif kw.arg == 'blank':
                if isinstance(kw.value, ast.Constant):
                    if kw.value.value:
                        nullable = True
            elif kw.arg == 'default':
                if isinstance(kw.value, ast.Constant):
                    default = str(kw.value.value)
        
        return Column(
            name=name,
            data_type=data_type,
            nullable=nullable,
            default=default,
            primary_key=primary_key,
            foreign_key=False
        )
    
    def _parse_relationship(self, name: str, call: ast.Call):
        """Parse SQLAlchemy relationship."""
        
        # Extract target table
        target_table = None
        for arg in call.args:
            if isinstance(arg, ast.Constant):
                target_table = str(arg.value)
                break
            elif isinstance(arg, ast.Name):
                target_table = arg.id.lower()
                break
        
        if target_table:
            self.relationships.append({
                'source_column': name + '_id',
                'target_table': target_table,
                'target_column': 'id'
            })
    
    def _parse_with_regex(self, content: str):
        """Fallback: Parse Python with regex."""
        
        # Find SQLAlchemy models
        model_pattern = r'class\s+(\w+)\s*\(.*?Base.*?\):'
        models = re.findall(model_pattern, content, re.IGNORECASE)
        
        for model_name in models:
            table = Table(name=model_name.lower())
            
            # Find columns
            column_pattern = r'(\w+)\s*=\s*Column\(([^)]+)\)'
            matches = re.findall(column_pattern, content)
            
            for col_name, col_def in matches:
                data_type = 'VARCHAR'
                primary_key = False
                nullable = True
                
                if 'primary_key=True' in col_def:
                    primary_key = True
                if 'nullable=False' in col_def:
                    nullable = False
                
                # Try to extract type
                type_match = re.search(r'(\w+)\(', col_def)
                if type_match:
                    data_type = type_match.group(1).upper()
                
                table.columns.append(Column(
                    name=col_name,
                    data_type=data_type,
                    nullable=nullable,
                    primary_key=primary_key
                ))
            
            self.schema.tables.append(table)
            self.tables[table.name] = table
    
    def _build_relationships(self):
        """Build relationship objects."""
        
        for rel in self.relationships:
            self.schema.relationships.append(
                Relationship(
                    source_table=self._find_source_table(rel['source_column']),
                    source_column=rel['source_column'],
                    target_table=rel['target_table'],
                    target_column=rel['target_column']
                )
            )
    
    def _find_source_table(self, column_name: str) -> str:
        """Find which table a column belongs to."""
        for table in self.schema.tables:
            for col in table.columns:
                if col.name == column_name:
                    return table.name
        return "unknown"
