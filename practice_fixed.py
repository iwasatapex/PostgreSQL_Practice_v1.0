"""
Practice Server - Fixed Version
Simple, working save & resume functionality
"""

import os
import json
import hashlib
import random
import re
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ============================================================
# DATA
# ============================================================

SAVE_DIR = Path("sessions")
SAVE_DIR.mkdir(exist_ok=True)

# Sample questions
SAMPLE_QUESTIONS = [
    {
        'id': 1,
        'topic': 'SELECT',
        'difficulty': 'Beginner',
        'question': 'List all records from the users table.',
        'answer': 'SELECT * FROM users;',
        'explanation': 'SELECT * returns all columns and rows.',
        'tip': 'Use specific columns in production.',
        'hint': 'Use SELECT * FROM users'
    },
    {
        'id': 2,
        'topic': 'WHERE',
        'difficulty': 'Beginner',
        'question': 'Find all users where email is NULL.',
        'answer': 'SELECT * FROM users WHERE email IS NULL;',
        'explanation': 'IS NULL checks for NULL values.',
        'tip': 'Use IS NULL not = NULL.',
        'hint': 'Use WHERE email IS NULL'
    },
    {
        'id': 3,
        'topic': 'ORDER BY',
        'difficulty': 'Beginner',
        'question': 'List all products ordered by price from highest to lowest.',
        'answer': 'SELECT * FROM products ORDER BY price DESC;',
        'explanation': 'ORDER BY sorts results.',
        'tip': 'DESC for descending order.',
        'hint': 'Use ORDER BY price DESC'
    },
    {
        'id': 4,
        'topic': 'JOIN',
        'difficulty': 'Intermediate',
        'question': 'Show orders with customer names.',
        'answer': 'SELECT o.*, u.name FROM orders o JOIN users u ON o.user_id = u.id;',
        'explanation': 'JOIN connects tables.',
        'tip': 'Use aliases for readability.',
        'hint': 'Use JOIN with ON condition'
    },
    {
        'id': 5,
        'topic': 'GROUP BY',
        'difficulty': 'Intermediate',
        'question': 'Count orders per user.',
        'answer': 'SELECT user_id, COUNT(*) FROM orders GROUP BY user_id;',
        'explanation': 'GROUP BY groups records.',
        'tip': 'Use COUNT for counting.',
        'hint': 'Use GROUP BY user_id'
    }
]

# ============================================================
# SESSION MANAGER
# ============================================================

class SessionManager:
    def __init__(self):
        self.current_session = None
        self.current_questions = []
        self.current_index = 0
        self.results = []
        self.hint_used = False
    
    def create_session(self, user_name):
        """Create a new session."""
        session_id = hashlib.md5(f"{user_name}_{datetime.now()}".encode()).hexdigest()[:16]
        
        # Use sample questions
        questions = SAMPLE_QUESTIONS.copy()
        
        # Add some random variations
        for i in range(10):
            q = SAMPLE_QUESTIONS[i % len(SAMPLE_QUESTIONS)].copy()
            q['id'] = 1000 + i
            q['question'] = q['question'].replace('users', random.choice(['users', 'products', 'orders']))
            questions.append(q)
        
        session_data = {
            'session_id': session_id,
            'user_name': user_name,
            'start_time': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'questions': questions,
            'current_index': 0,
            'results': [],
            'correct_answers': 0,
            'total_hints_used': 0
        }
        
        # Save to file
        with open(SAVE_DIR / f"{session_id}.json", 'w') as f:
            json.dump(session_data, f, indent=2)
        
        self.current_session = session_data
        self.current_questions = questions
        self.current_index = 0
        self.results = []
        self.hint_used = False
        
        return session_data
    
    def resume_session(self, session_id):
        """Resume an existing session."""
        session_file = SAVE_DIR / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        self.current_session = session_data
        self.current_questions = session_data['questions']
        self.current_index = session_data['current_index']
        self.results = session_data['results']
        self.hint_used = False
        
        return session_data
    
    def save_session(self):
        """Save current session."""
        if not self.current_session:
            return False
        
        self.current_session['last_updated'] = datetime.now().isoformat()
        self.current_session['current_index'] = self.current_index
        self.current_session['results'] = self.results
        self.current_session['correct_answers'] = sum(1 for r in self.results if r.get('is_correct', False))
        
        session_file = SAVE_DIR / f"{self.current_session['session_id']}.json"
        with open(session_file, 'w') as f:
            json.dump(self.current_session, f, indent=2)
        
        return True
    
    def get_current_question(self):
        """Get current question."""
        if self.current_index < len(self.current_questions):
            return self.current_questions[self.current_index]
        return None
    
    def get_hint(self):
        """Get hint for current question."""
        q = self.get_current_question()
        if q:
            self.hint_used = True
            return q.get('hint', 'Think about the SQL syntax!')
        return None
    
    def submit_answer(self, user_answer):
        """Submit and grade answer."""
        q = self.get_current_question()
        if not q:
            return {'error': 'No question'}
        
        # Simple grading
        correct = q['answer'].strip().lower() == user_answer.strip().lower()
        
        # Calculate score
        if correct:
            total_score = 100
        else:
            total_score = 50
        
        # Apply hint penalty
        if self.hint_used:
            total_score -= 20
        
        total_score = max(0, total_score)
        
        result = {
            'question_id': q['id'],
            'user_answer': user_answer,
            'correct_answer': q['answer'],
            'is_correct': correct,
            'total_score': total_score,
            'used_hint': self.hint_used,
            'feedback': []
        }
        
        if correct and self.hint_used:
            result['feedback'].append("✅ Correct! (Hint penalty: -20)")
        elif correct:
            result['feedback'].append("✅ Perfect! Full score!")
        elif self.hint_used:
            result['feedback'].append("❌ Incorrect. Hint used: -20 penalty.")
        else:
            result['feedback'].append("❌ Incorrect. Review the correct answer.")
        
        self.results.append(result)
        
        # Move to next
        self.current_index += 1
        self.hint_used = False
        
        # Auto save
        self.save_session()
        
        return {
            'grade': result,
            'next_question': self.get_current_question()
        }
    
    def get_stats(self):
        """Get session statistics."""
        total = len(self.results)
        correct = sum(1 for r in self.results if r.get('is_correct', False))
        
        return {
            'total_questions': len(self.current_questions),
            'answered': total,
            'correct': correct,
            'accuracy': f"{(correct / total * 100):.1f}%" if total > 0 else "0%",
            'total_hints_used': self.current_session.get('total_hints_used', 0) if self.current_session else 0,
            'session_id': self.current_session['session_id'] if self.current_session else None,
            'user_name': self.current_session['user_name'] if self.current_session else None,
            'start_time': self.current_session['start_time'] if self.current_session else None,
            'last_updated': self.current_session['last_updated'] if self.current_session else None
        }

# ============================================================
# FLASK ROUTES
# ============================================================

manager = SessionManager()

@app.route('/')
def index():
    return render_template('practice_fixed.html')

@app.route('/api/practice/start', methods=['POST'])
def start_practice():
    try:
        data = request.get_json()
        user_name = data.get('user_name', 'Anonymous')
        session = manager.create_session(user_name)
        return jsonify({
            'success': True,
            'session_id': session['session_id']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/sessions', methods=['GET'])
def list_sessions():
    try:
        sessions = []
        for f in SAVE_DIR.glob("*.json"):
            with open(f, 'r') as file:
                data = json.load(file)
                sessions.append({
                    'session_id': data['session_id'],
                    'user_name': data['user_name'],
                    'start_time': data['start_time'],
                    'last_updated': data['last_updated'],
                    'answered_questions': len(data['results']),
                    'total_questions': len(data['questions']),
                    'correct_answers': data.get('correct_answers', 0),
                    'total_hints_used': data.get('total_hints_used', 0)
                })
        return jsonify({'sessions': sessions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/resume', methods=['POST'])
def resume_session():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        session = manager.resume_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session_id': session['session_id']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/delete/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        session_file = SAVE_DIR / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            return jsonify({'success': True})
        return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/save/<session_id>', methods=['POST'])
def save_session(session_id):
    try:
        if manager.save_session():
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to save'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/question/<session_id>', methods=['GET'])
def get_question(session_id):
    try:
        # Resume session if needed
        if not manager.current_session or manager.current_session['session_id'] != session_id:
            session = manager.resume_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404
        
        question = manager.get_current_question()
        if not question:
            return jsonify({'error': 'No question available'}), 404
        
        stats = manager.get_stats()
        
        return jsonify({
            'question': {
                'id': question['id'],
                'topic': question['topic'],
                'difficulty': question['difficulty'],
                'question': question['question']
            },
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/hint/<session_id>', methods=['GET'])
def get_hint(session_id):
    try:
        if not manager.current_session or manager.current_session['session_id'] != session_id:
            session = manager.resume_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404
        
        hint = manager.get_hint()
        if not hint:
            return jsonify({'error': 'No hint available'}), 404
        
        return jsonify({
            'hint': hint,
            'penalty': 20
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/answer/<session_id>', methods=['POST'])
def submit_answer(session_id):
    try:
        data = request.get_json()
        user_answer = data.get('answer', '')
        
        result = manager.submit_answer(user_answer)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'grade': result['grade'],
            'stats': manager.get_stats()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/next/<session_id>', methods=['POST'])
def next_question(session_id):
    try:
        if not manager.current_session or manager.current_session['session_id'] != session_id:
            session = manager.resume_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404
        
        manager.current_index += 1
        
        question = manager.get_current_question()
        if not question:
            return jsonify({'error': 'No more questions'}), 404
        
        stats = manager.get_stats()
        
        return jsonify({
            'question': {
                'id': question['id'],
                'topic': question['topic'],
                'difficulty': question['difficulty'],
                'question': question['question']
            },
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/skip/<session_id>', methods=['POST'])
def skip_question(session_id):
    try:
        if not manager.current_session or manager.current_session['session_id'] != session_id:
            session = manager.resume_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404
        
        manager.current_index += 1
        
        question = manager.get_current_question()
        if not question:
            return jsonify({'error': 'No more questions'}), 404
        
        stats = manager.get_stats()
        
        return jsonify({
            'question': {
                'id': question['id'],
                'topic': question['topic'],
                'difficulty': question['difficulty'],
                'question': question['question']
            },
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/stats/<session_id>', methods=['GET'])
def get_stats(session_id):
    try:
        if not manager.current_session or manager.current_session['session_id'] != session_id:
            session = manager.resume_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404
        
        stats = manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/reset/<session_id>', methods=['POST'])
def reset_session(session_id):
    try:
        if manager.current_session and manager.current_session['session_id'] == session_id:
            manager.current_index = 0
            manager.results = []
            manager.current_session['correct_answers'] = 0
            manager.current_session['total_hints_used'] = 0
            manager.hint_used = False
            
            question = manager.get_current_question()
            if not question:
                return jsonify({'error': 'No question'}), 404
            
            stats = manager.get_stats()
            return jsonify({
                'question': {
                    'id': question['id'],
                    'topic': question['topic'],
                    'difficulty': question['difficulty'],
                    'question': question['question']
                },
                'stats': stats
            })
        return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    SAVE_DIR.mkdir(exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5003)
