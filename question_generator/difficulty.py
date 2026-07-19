"""
question_generator/difficulty.py

Difficulty scoring and classification.
"""

def calculate_difficulty(question_type: str, tables_count: int, 
                         joins_count: int, features: list) -> str:
    """Calculate difficulty level based on complexity."""
    
    score = 0
    
    # Base score by question type
    type_scores = {
        'SELECT': 1,
        'WHERE': 1,
        'ORDER BY': 1,
        'LIMIT': 1,
        'AGGREGATION': 2,
        'GROUP BY': 2,
        'HAVING': 2,
        'JOIN': 3,
        'SELF JOIN': 4,
        'CTE': 4,
        'WINDOW': 4,
        'JSONB': 4,
        'RECURSIVE': 5,
    }
    
    score += type_scores.get(question_type, 1)
    
    # Add complexity for multiple tables
    if tables_count > 3:
        score += 1
    
    # Add complexity for joins
    if joins_count > 1:
        score += 1
    
    # Check for advanced features
    advanced_features = {'jsonb', 'window', 'recursive', 'cte'}
    if any(feature in features for feature in advanced_features):
        score += 1
    
    # Map score to difficulty level
    if score <= 2:
        return "Beginner"
    elif score <= 3:
        return "Intermediate"
    elif score <= 4:
        return "Advanced"
    else:
        return "Expert"
