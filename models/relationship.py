from dataclasses import dataclass


@dataclass
class Relationship:
    """Represents a foreign key relationship."""
    
    source_table: str
    source_column: str
    target_table: str
    target_column: str
