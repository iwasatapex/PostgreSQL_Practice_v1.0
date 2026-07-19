from dataclasses import dataclass


@dataclass
class Question:
    """Represents a SQL practice question."""
    
    id: int
    topic: str
    difficulty: str
    question: str
    answer: str
    explanation: str
    tip: str