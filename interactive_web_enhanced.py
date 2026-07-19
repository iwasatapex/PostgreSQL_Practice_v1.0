"""
Enhanced Interactive SQL Practice - Web Application
Features:
- Stay on question until user clicks "Next"
- Multiple alternative answers
- Syntax and grammar scoring
- Detailed feedback with marks
"""

import os
import re
import json
import random
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

from parser.sql_parser import SQLParser
from parser.python_parser import PythonParser
from question_generator.format_generator import FormatQuestionGenerator

app = Flask(__name__)
app.secret_key = os.urandom(24)


class SQLScorer:
    """Advanced SQL answer scorer with syntax and grammar checking."""
    
    @staticmethod
    def score_answer(user_answer: str, correct_answer: str) -> dict:
        """Score the user's answer based on multiple criteria."""
        
        user_answer = user_answer.strip()
        correct_answer = correct_answer.strip()
        
        # Normalize for comparison
        def normalize(sql):
            sql = sql.strip()
            if sql.endswith(';'):
                sql = sql[:-1]
            sql = ' '.join(sql.split())
            return sql.lower()
        
        user_norm = normalize(user_answer)
        correct_norm = normalize(correct_answer)
        
        # Initialize scores
        scores = {
            'syntax_score': 0,
            'grammar_score': 0,
            'keyword_score': 0,
            'structure_score': 0,
            'total_score': 0,
            'is_correct': False,
            'feedback': []
        }
        
        # 1. Syntax Check (40%)
        syntax_checks = 0
        syntax_passed = 0
        
        # Check for semicolon
        if user_answer.endswith(';'):
            syntax_passed += 1
        else:
            scores['feedback'].append("⚠️ Missing semicolon at the end (minor)")
        syntax_checks += 1
        
        # Check for SQL keywords
        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING']
        user_upper = user_answer.upper()
        for keyword in sql_keywords:
            if keyword in user_upper:
                syntax_passed += 1
                break
        syntax_checks += 1
        
        # Check for balanced parentheses
        if user_answer.count('(') == user_answer.count(')'):
            syntax_passed += 1
        else:
            scores['feedback'].append("⚠️ Unbalanced parentheses (syntax error)")
        syntax_checks += 1
        
        # Check for quotes
        if user_answer.count("'") % 2 == 0:
            syntax_passed += 1
        else:
            scores['feedback'].append("⚠️ Unbalanced quotes (syntax error)")
        syntax_checks += 1
        
        scores['syntax_score'] = int((syntax_passed / syntax_checks) * 40)
        
        # 2. Grammar Check (30%)
        grammar_checks = 0
        grammar_passed = 0
        
        # Check for SELECT (must have)
        if 'SELECT' in user_upper:
            grammar_passed += 1
        else:
            scores['feedback'].append("❌ Missing SELECT keyword")
        grammar_checks += 1
        
        # Check for FROM (must have)
        if 'FROM' in user_upper:
            grammar_passed += 1
        else:
            scores['feedback'].append("❌ Missing FROM keyword")
        grammar_checks += 1
        
        # Check for column specification (not just *)
        if 'SELECT *' in user_upper:
            scores['feedback'].append("ℹ️ Using SELECT * (okay for learning, but specify columns in production)")
            grammar_passed += 1
        elif 'SELECT' in user_upper:
            grammar_passed += 1
        grammar_checks += 1
        
        # Check WHERE if it's in correct answer
        if 'WHERE' in correct_norm:
            if 'WHERE' in user_norm:
                grammar_passed += 1
            else:
                scores['feedback'].append("ℹ️ Missing WHERE clause (expected)")
        grammar_checks += 1
        
        # Check JOIN if it's in correct answer
        if 'JOIN' in correct_norm:
            if 'JOIN' in user_norm:
                grammar_passed += 1
            else:
                scores['feedback'].append("ℹ️ Missing JOIN clause (expected)")
        grammar_checks += 1
        
        scores['grammar_score'] = int((grammar_passed / grammar_checks) * 30) if grammar_checks > 0 else 0
        
        # 3. Keyword Score (20%)
        keyword_checks = 0
        keyword_passed = 0
        
        # Extract keywords from correct answer
        correct_keywords = set(re.findall(r'\b[A-Z_]+\b', correct_answer.upper()))
        user_keywords = set(re.findall(r'\b[A-Z_]+\b', user_answer.upper()))
        
        if correct_keywords:
            matches = len(correct_keywords & user_keywords)
            keyword_passed = matches / len(correct_keywords)
            scores['keyword_score'] = int(keyword_passed * 20)
        else:
            scores['keyword_score'] = 10
        
        # 4. Structure Score (10%)
        # Check if query structure matches (SELECT/FROM/WHERE order)
        structure_score = 0
        
        # Extract main clauses
        clauses = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING']
        correct_positions = []
        user_positions = []
        
        for clause in clauses:
            if clause in correct_norm.upper():
                correct_positions.append(clause)
            if clause in user_norm.upper():
                user_positions.append(clause)
        
        # Check if order matches
        if correct_positions and user_positions:
            # Check if user has all required clauses in correct order
            if all(c in user_positions for c in correct_positions):
                # Check order
                if user_positions == correct_positions:
                    structure_score = 10
                else:
                    structure_score = 7
            else:
                structure_score = 3
        else:
            structure_score = 5
        
        scores['structure_score'] = structure_score
        
        # Calculate total score
        scores['total_score'] = (
            scores['syntax_score'] + 
            scores['grammar_score'] + 
            scores['keyword_score'] + 
            scores['structure_score']
        )
        
        # Determine if correct (threshold: 70%)
        scores['is_correct'] = scores['total_score'] >= 70
        
        # Add final feedback
        if scores['is_correct']:
            if scores['total_score'] >= 90:
                scores['feedback'].append("🌟 Excellent! Perfect solution!")
            elif scores['total_score'] >= 80:
                scores['feedback'].append("👍 Good job! Minor improvements possible.")
            else:
                scores['feedback'].append("✅ Correct! Review the tips for improvement.")
        else:
            if scores['total_score'] >= 50:
                scores['feedback'].append("🔧 Close! Review the feedback below.")
            else:
                scores['feedback'].append("📚 Review the correct answer and explanation carefully.")
        
        return scores
    
    @staticmethod
    def get_alternative_answers(correct_answer: str) -> list:
        """Generate alternative correct answers."""
        alternatives = []
        
        # Original
        alternatives.append({
            'type': 'Standard',
            'query': correct_answer,
            'description': 'Standard SQL query'
        })
        
        # Check for different JOIN types
        if 'JOIN' in correct_answer.upper():
            if 'LEFT JOIN' not in correct_answer.upper():
                alt = correct_answer.replace('JOIN', 'LEFT JOIN')
                alternatives.append({
                    'type': 'Alternative',
                    'query': alt,
                    'description': 'Using LEFT JOIN (includes unmatched rows)'
                })
            
            if 'INNER JOIN' not in correct_answer.upper():
                alt = correct_answer.replace('JOIN', 'INNER JOIN')
                alternatives.append({
                    'type': 'Alternative',
                    'query': alt,
                    'description': 'Explicit INNER JOIN syntax'
                })
        
        # Check for different filter approaches
        if 'WHERE' in correct_answer.upper():
            # Try different filter style
            if 'IN' in correct_answer.upper():
                alt = correct_answer.replace('IN', '= ANY')
                if alt != correct_answer:
                    alternatives.append({
                        'type': 'Alternative',
                        'query': alt,
                        'description': 'Using = ANY instead of IN'
                    })
        
        # Check for column aliases
        if 'AS' not in correct_answer.upper():
            alt = correct_answer.replace('SELECT', 'SELECT')
            # Add AS to first column
            alt = re.sub(r'SELECT\s+(\w+)', r'SELECT \1 AS col1', alt)
            if alt != correct_answer:
                alternatives.append({
                    'type': 'Alternative',
                    'query': alt,
                    'description': 'With column aliases for clarity'
                })
        
        # Check for different aggregation approaches
        if 'GROUP BY' in correct_answer.upper():
            # Try using DISTINCT instead of GROUP BY (if applicable)
            if 'COUNT' not in correct_answer.upper():
                alt = correct_answer.replace('GROUP BY', '')
                alt = alt.replace('SELECT', 'SELECT DISTINCT')
                if alt != correct_answer:
                    alternatives.append({
                        'type': 'Alternative',
                        'query': alt,
                        'description': 'Using DISTINCT instead of GROUP BY'
                    })
        
        # Check for CTE alternative
        if 'JOIN' in correct_answer.upper() or 'GROUP BY' in correct_answer.upper():
            parts = correct_answer.split('FROM')
            if len(parts) >= 2:
                select_part = parts[0].replace('SELECT', '').strip()
                from_part = parts[1].strip() if len(parts) > 1 else ''
                if from_part:
                    alt = f"WITH cte AS (SELECT * FROM {from_part}) SELECT {select_part} FROM cte;"
                    alternatives.append({
                        'type': 'Alternative',
                        'query': alt,
                        'description': 'Using Common Table Expression (CTE)'
                    })
        
        # Add subquery alternative
        if 'JOIN' in correct_answer.upper():
            # Simple subquery conversion
            alt = correct_answer.replace('JOIN', 'WHERE EXISTS (SELECT 1 FROM')
            alt = alt.replace(' ON ', ' WHERE ')
            if alt != correct_answer:
                alternatives.append({
                    'type': 'Alternative',
                    'query': alt,
                    'description': 'Using EXISTS subquery'
                })
        
        # Deduplicate alternatives (simple)
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            # Simple deduplication
            key = alt['query'].strip()
            if key not in seen:
                seen.add(key)
                unique_alternatives.append(alt)
        
        # Limit to 5 alternatives
        return unique_alternatives[:5]


class SQLPracticeSession:
    """Manages a practice session with enhanced features."""
    
    def __init__(self):
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.answered = 0
        self.total_questions = 0
        self.difficulty_counts = {}
        self.start_time = None
        self.results = []
        self.session_complete = False
        self.current_question_answered = False
    
    def load_questions(self, file_path: str, counts: dict) -> bool:
        """Load questions with specific difficulty counts."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            
            # Parse file
            if file_path.suffix.lower() == '.sql':
                parser = SQLParser(file_path)
            elif file_path.suffix.lower() == '.py':
                parser = PythonParser(file_path)
            else:
                return False
            
            schema = parser.parse()
            
            # Generate all questions
            generator = FormatQuestionGenerator(schema)
            all_questions = generator.generate_all(sum(counts.values()))
            
            # Filter by difficulty
            selected_questions = []
            for difficulty, count in counts.items():
                filtered = [q for q in all_questions if q.difficulty == difficulty]
                if filtered:
                    take = min(count, len(filtered))
                    selected_questions.extend(random.sample(filtered, take))
            
            # Shuffle to mix difficulties
            random.shuffle(selected_questions)
            
            self.questions = selected_questions
            self.total_questions = len(selected_questions)
            self.difficulty_counts = counts
            self.current_index = 0
            self.score = 0
            self.answered = 0
            self.results = []
            self.session_complete = False
            self.current_question_answered = False
            self.start_time = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error loading questions: {e}")
            return False
    
    def get_current_question(self):
        """Get the current question with enhanced data."""
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            
            # Generate alternative answers for this question
            alternatives = SQLScorer.get_alternative_answers(q.answer)
            
            return {
                'id': self.current_index + 1,
                'total': len(self.questions),
                'question': q.question,
                'topic': q.topic,
                'difficulty': q.difficulty,
                'correct_answer': q.answer,
                'alternatives': alternatives,
                'explanation': q.explanation,
                'tip': q.tip,
                'answered': self.current_question_answered,
                'progress': {
                    'answered': self.answered,
                    'total': self.total_questions,
                    'score': self.score
                }
            }
        return None
    
    def check_answer(self, user_answer: str) -> dict:
        """Check the user's answer with advanced scoring."""
        if self.current_index >= len(self.questions):
            return {'error': 'No more questions'}
        
        q = self.questions[self.current_index]
        
        # Score the answer
        scorer = SQLScorer()
        result = scorer.score_answer(user_answer, q.answer)
        
        # Record result
        result_data = {
            'question_id': self.current_index + 1,
            'question': q.question,
            'user_answer': user_answer,
            'correct_answer': q.answer,
            'alternatives': scorer.get_alternative_answers(q.answer),
            'scores': result,
            'difficulty': q.difficulty,
            'topic': q.topic,
            'explanation': q.explanation,
            'tip': q.tip
        }
        self.results.append(result_data)
        
        # Update stats
        self.answered += 1
        if result['is_correct']:
            self.score += 1
        
        self.current_question_answered = True
        
        return {
            'scores': result,
            'score': self.score,
            'answered': self.answered,
            'total': self.total_questions,
            'is_last': self.current_index >= len(self.questions) - 1
        }
    
    def next_question(self):
        """Move to the next question."""
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.current_question_answered = False
            return self.get_current_question()
        else:
            self.session_complete = True
            return None
    
    def get_stats(self):
        """Get session statistics."""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        return {
            'total_questions': self.total_questions,
            'answered': self.answered,
            'score': self.score,
            'accuracy': f"{(self.score / self.answered * 100):.1f}%" if self.answered > 0 else "0%",
            'time': f"{minutes}m {seconds}s",
            'difficulty_counts': self.difficulty_counts,
            'results': self.results
        }

# Global session store
practice_sessions = {}

@app.route('/')
def index():
    """Home page."""
    return render_template('practice_enhanced.html')

@app.route('/start', methods=['POST'])
def start_session():
    """Start a new practice session."""
    data = request.json
    file_path = data.get('file_path', 'examples/ecommerce.sql')
    
    counts = {
        'Beginner': int(data.get('beginner_count', 3)),
        'Intermediate': int(data.get('intermediate_count', 3)),
        'Advanced': int(data.get('advanced_count', 2)),
        'Expert': int(data.get('expert_count', 2))
    }
    
    counts = {k: v for k, v in counts.items() if v > 0}
    
    session_id = str(len(practice_sessions) + 1)
    practice_session = SQLPracticeSession()
    
    if not practice_session.load_questions(file_path, counts):
        return jsonify({'error': 'Failed to load questions'}), 400
    
    practice_sessions[session_id] = practice_session
    
    question = practice_session.get_current_question()
    if question:
        return jsonify({
            'session_id': session_id,
            'question': question,
            'stats': practice_session.get_stats()
        })
    else:
        return jsonify({'error': 'No questions available'}), 400

@app.route('/question/<session_id>', methods=['GET'])
def get_question(session_id):
    """Get current question."""
    if session_id not in practice_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = practice_sessions[session_id]
    question = session.get_current_question()
    
    if question:
        return jsonify({
            'question': question,
            'stats': session.get_stats()
        })
    else:
        return jsonify({
            'complete': True,
            'stats': session.get_stats()
        })

@app.route('/answer/<session_id>', methods=['POST'])
def submit_answer(session_id):
    """Submit an answer for current question."""
    if session_id not in practice_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = practice_sessions[session_id]
    data = request.json
    user_answer = data.get('answer', '')
    
    result = session.check_answer(user_answer)
    
    return jsonify({
        'result': result,
        'stats': session.get_stats()
    })

@app.route('/next/<session_id>', methods=['POST'])
def next_question(session_id):
    """Move to the next question."""
    if session_id not in practice_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = practice_sessions[session_id]
    next_q = session.next_question()
    
    if next_q:
        return jsonify({
            'question': next_q,
            'stats': session.get_stats(),
            'complete': False
        })
    else:
        return jsonify({
            'complete': True,
            'stats': session.get_stats()
        })

@app.route('/stats/<session_id>', methods=['GET'])
def get_stats(session_id):
    """Get session statistics."""
    if session_id not in practice_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = practice_sessions[session_id]
    return jsonify(session.get_stats())

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)
