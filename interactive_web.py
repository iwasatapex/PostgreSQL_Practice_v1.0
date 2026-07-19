"""
Interactive SQL Practice - Web Application
Users can practice SQL questions with instant feedback.
"""

import os
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

class SQLPracticeSession:
    """Manages a practice session."""
    
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
                    # Take requested count or all if less available
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
            self.start_time = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error loading questions: {e}")
            return False
    
    def get_current_question(self):
        """Get the current question."""
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            return {
                'id': self.current_index + 1,
                'total': len(self.questions),
                'question': q.question,
                'topic': q.topic,
                'difficulty': q.difficulty,
                'answer': q.answer,  # We'll send this to check later
                'explanation': q.explanation,
                'tip': q.tip,
                'progress': {
                    'answered': self.answered,
                    'total': self.total_questions,
                    'score': self.score
                }
            }
        return None
    
    def check_answer(self, user_answer: str) -> dict:
        """Check if the user's answer is correct."""
        if self.current_index >= len(self.questions):
            return {'error': 'No more questions'}
        
        q = self.questions[self.current_index]
        correct_answer = q.answer.strip()
        user_answer = user_answer.strip()
        
        # Normalize for comparison (remove extra spaces, semicolons, etc.)
        def normalize(sql):
            sql = sql.strip()
            if sql.endswith(';'):
                sql = sql[:-1]
            # Remove extra whitespace
            sql = ' '.join(sql.split())
            return sql.lower()
        
        is_correct = normalize(user_answer) == normalize(correct_answer)
        
        # Record result
        result = {
            'question_id': self.current_index + 1,
            'question': q.question,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': q.explanation,
            'tip': q.tip,
            'difficulty': q.difficulty,
            'topic': q.topic
        }
        self.results.append(result)
        
        # Update stats
        self.answered += 1
        if is_correct:
            self.score += 1
        
        is_last = self.current_index >= len(self.questions) - 1
        
        # Move to next question
        self.current_index += 1
        if is_last:
            self.session_complete = True
        
        return {
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'explanation': q.explanation,
            'tip': q.tip,
            'score': self.score,
            'answered': self.answered,
            'total': self.total_questions,
            'is_last': is_last,
            'session_complete': self.session_complete
        }
    
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
    return render_template('practice.html')

@app.route('/start', methods=['POST'])
def start_session():
    """Start a new practice session."""
    data = request.json
    file_path = data.get('file_path', 'examples/ecommerce.sql')
    
    # Get question counts for each difficulty
    counts = {
        'Beginner': int(data.get('beginner_count', 5)),
        'Intermediate': int(data.get('intermediate_count', 5)),
        'Advanced': int(data.get('advanced_count', 3)),
        'Expert': int(data.get('expert_count', 2))
    }
    
    # Remove zero counts
    counts = {k: v for k, v in counts.items() if v > 0}
    
    # Create session
    session_id = str(len(practice_sessions) + 1)
    practice_session = SQLPracticeSession()
    
    if not practice_session.load_questions(file_path, counts):
        return jsonify({'error': 'Failed to load questions'}), 400
    
    practice_sessions[session_id] = practice_session
    
    # Get first question
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
    
    # Get next question if available
    next_question = session.get_current_question() if not session.session_complete else None
    
    return jsonify({
        'result': result,
        'next_question': next_question,
        'stats': session.get_stats(),
        'complete': session.session_complete
    })

@app.route('/stats/<session_id>', methods=['GET'])
def get_stats(session_id):
    """Get session statistics."""
    if session_id not in practice_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = practice_sessions[session_id]
    return jsonify(session.get_stats())

@app.route('/reset/<session_id>', methods=['POST'])
def reset_session(session_id):
    """Reset a session."""
    if session_id in practice_sessions:
        # Keep the questions but reset progress
        session = practice_sessions[session_id]
        session.current_index = 0
        session.score = 0
        session.answered = 0
        session.results = []
        session.session_complete = False
        session.start_time = datetime.now()
        
        question = session.get_current_question()
        return jsonify({
            'question': question,
            'stats': session.get_stats()
        })
    return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    # Ensure templates folder exists
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)
