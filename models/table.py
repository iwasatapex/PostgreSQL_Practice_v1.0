from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.column import Column
from models.relationship import Relationship


@dataclass
class Table:
    """Represents a database table."""
    
    name: str
    columns: List[Column] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    indexes: List[Dict] = field(default_factory=list)
    comment: Optional[str] = None
    table_type: str = "base"  # base, lookup, audit, fact
