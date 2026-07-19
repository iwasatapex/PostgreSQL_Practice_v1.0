"""
models/schema.py

Complete schema model for a database.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from models.table import Table
from models.relationship import Relationship


@dataclass
class Schema:
    """Complete database schema."""
    
    name: str = "Unknown"
    tables: List[Table] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    
    def get_table(self, name: str) -> Optional[Table]:
        """Get a table by name."""
        for table in self.tables:
            if table.name.lower() == name.lower():
                return table
        return None
    
    def get_relationships_for_table(self, table_name: str) -> List[Relationship]:
        """Get all relationships for a table."""
        return [
            rel for rel in self.relationships 
            if rel.source_table.lower() == table_name.lower()
        ]
    
    def get_tables_with_jsonb(self) -> List[Table]:
        """Get all tables that have JSONB columns."""
        result = []
        for table in self.tables:
            for col in table.columns:
                if 'json' in col.data_type.lower():
                    result.append(table)
                    break
        return result
    
    def get_tables_with_timestamps(self) -> List[Table]:
        """Get all tables that have timestamp columns."""
        result = []
        for table in self.tables:
            for col in table.columns:
                if 'timestamp' in col.data_type.lower():
                    result.append(table)
                    break
        return result
    
    def get_self_referencing_tables(self) -> List[Table]:
        """Get tables that reference themselves."""
        result = []
        for rel in self.relationships:
            if rel.source_table.lower() == rel.target_table.lower():
                table = self.get_table(rel.source_table)
                if table and table not in result:
                    result.append(table)
        return result
