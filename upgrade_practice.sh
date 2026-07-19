#!/bin/bash
# ============================================================
# UPGRADE PRACTICE SYSTEM
# Adds: More question types, better scoring, save sessions, export results
# ============================================================

echo "============================================================"
echo "  🚀 Upgrading PostgreSQL Practice System"
echo "============================================================"

# Backup existing files
cp portal_complete.py portal_complete_backup.py
cp templates/practice_interactive.html templates/practice_interactive_backup.html
cp question_generator/format_generator.py question_generator/format_generator_backup.py 2>/dev/null

echo "✅ Backups created"

# ============================================================
# 1. MORE QUESTION TYPES (format_generator.py)
# ============================================================
cat > question_generator/format_generator.py << 'PYEOF'
"""
Format Generator - Generates various SQL questions with different difficulty levels
"""

from typing import List
from models.table import Table
from models.question import Question
import random


class FormatQuestionGenerator:
    """Generates SQL questions with specific format."""
    
    def __init__(self, tables: List[Table]):
        self.tables = tables
        self.questions = []
        self.counter = 0
    
    def generate_all(self, count: int = 100) -> List[Question]:
        """Generate questions of various types."""
        self.questions = []
        self.counter = 0
        
        # Generate different types
        self._generate_select_questions()
        self._generate_where_questions()
        self._generate_order_by_questions()
        self._generate_aggregation_questions()
        self._generate_join_questions()
        self._generate_group_by_questions()
        self._generate_subquery_questions()
        self._generate_cte_questions()
        self._generate_window_function_questions()
        self._generate_case_questions()
        self._generate_date_questions()
        self._generate_string_questions()
        
        # Shuffle and limit
        random.shuffle(self.questions)
        if len(self.questions) > count:
            self.questions = self.questions[:count]
        
        # Reassign IDs
        for i, q in enumerate(self.questions, 1):
            q.id = i
        
        return self.questions
    
    def _add_question(self, topic: str, difficulty: str, question: str,
                      answer: str, explanation: str, tip: str):
        self.counter += 1
        self.questions.append(
            Question(
                id=self.counter,
                topic=topic,
                difficulty=difficulty,
                question=question,
                answer=answer,
                explanation=explanation,
                tip=tip
            )
        )
    
    def _generate_select_questions(self):
        for table in self.tables:
            if len(table.columns) > 0:
                cols = ", ".join([c.name for c in table.columns[:3]])
                self._add_question(
                    topic="SELECT",
                    difficulty="Beginner",
                    question=f"List all records from the {table.name} table.",
                    answer=f"SELECT * FROM {table.name};",
                    explanation=f"SELECT * returns every column and row from {table.name}.",
                    tip="Use specific columns instead of SELECT * in production."
                )
                self._add_question(
                    topic="SELECT",
                    difficulty="Beginner",
                    question=f"Show only {cols} from the {table.name} table.",
                    answer=f"SELECT {cols} FROM {table.name};",
                    explanation=f"SELECT with specific columns returns only those columns.",
                    tip="Specify columns for better performance."
                )
    
    def _generate_where_questions(self):
        for table in self.tables:
            text_cols = [c for c in table.columns if 'char' in c.data_type.lower() or c.data_type == 'text']
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
            if text_cols:
                col = text_cols[0]
                self._add_question(
                    topic="WHERE",
                    difficulty="Beginner",
                    question=f"Find all {table.name} where {col.name} contains 'test'.",
                    answer=f"SELECT * FROM {table.name} WHERE {col.name} LIKE '%test%';",
                    explanation=f"LIKE with % performs a partial match.",
                    tip="Use ILIKE for case-insensitive searches."
                )
            if num_cols:
                col = num_cols[0]
                value = random.randint(1, 100)
                self._add_question(
                    topic="WHERE",
                    difficulty="Beginner",
                    question=f"Find all {table.name} where {col.name} > {value}.",
                    answer=f"SELECT * FROM {table.name} WHERE {col.name} > {value};",
                    explanation=f"Filters rows where {col.name} is greater than {value}.",
                    tip="Use >, <, >=, <=, =, != for numeric comparisons."
                )
    
    def _generate_order_by_questions(self):
        for table in self.tables:
            if table.columns:
                col = table.columns[0]
                self._add_question(
                    topic="ORDER BY",
                    difficulty="Beginner",
                    question=f"List all {table.name} ordered by {col.name} descending.",
                    answer=f"SELECT * FROM {table.name} ORDER BY {col.name} DESC;",
                    explanation=f"ORDER BY {col.name} DESC sorts from highest to lowest.",
                    tip="DESC shows largest numbers or latest dates first."
                )
    
    def _generate_aggregation_questions(self):
        for table in self.tables:
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
            for col in num_cols[:1]:
                self._add_question(
                    topic="Aggregation",
                    difficulty="Intermediate",
                    question=f"Calculate the average {col.name} from {table.name}.",
                    answer=f"SELECT AVG({col.name}) FROM {table.name};",
                    explanation=f"AVG({col.name}) calculates the mean.",
                    tip="Use ROUND(AVG(column), 2) to limit decimals."
                )
                self._add_question(
                    topic="Aggregation",
                    difficulty="Intermediate",
                    question=f"Find the total {col.name} from {table.name}.",
                    answer=f"SELECT SUM({col.name}) FROM {table.name};",
                    explanation=f"SUM({col.name}) adds up all values.",
                    tip="SUM ignores NULL values."
                )
    
    def _generate_join_questions(self):
        if len(self.tables) >= 2:
            # Join first two tables
            t1 = self.tables[0]
            t2 = self.tables[1]
            # Assume a foreign key exists (simplified)
            fk_col = f"{t1.name}_id"  # common pattern
            self._add_question(
                topic="JOIN",
                difficulty="Intermediate",
                question=f"Join the {t1.name} table with the {t2.name} table.",
                answer=f"SELECT * FROM {t1.name} JOIN {t2.name} ON {t1.name}.id = {t2.name}.{fk_col};",
                explanation=f"INNER JOIN connects {t1.name} to {t2.name} on the foreign key.",
                tip="Use table aliases to make queries more readable."
            )
    
    def _generate_group_by_questions(self):
        for table in self.tables:
            group_cols = [c for c in table.columns if c.data_type in ['character varying', 'text', 'integer'] and not c.primary_key]
            if group_cols:
                col = group_cols[0]
                self._add_question(
                    topic="GROUP BY",
                    difficulty="Intermediate",
                    question=f"Count records in {table.name} grouped by {col.name}.",
                    answer=f"SELECT {col.name}, COUNT(*) FROM {table.name} GROUP BY {col.name};",
                    explanation=f"GROUP BY {col.name} creates groups and COUNT counts each group.",
                    tip="All non-aggregated columns in SELECT must be in GROUP BY."
                )
    
    def _generate_subquery_questions(self):
        for table in self.tables:
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
            if num_cols:
                col = num_cols[0]
                self._add_question(
                    topic="Subquery",
                    difficulty="Advanced",
                    question=f"Find records in {table.name} where {col.name} is above average.",
                    answer=f"SELECT * FROM {table.name} WHERE {col.name} > (SELECT AVG({col.name}) FROM {table.name});",
                    explanation=f"Subquery computes the average, main query filters above it.",
                    tip="Subqueries can be slow; consider CTEs for complex queries."
                )
    
    def _generate_cte_questions(self):
        for table in self.tables:
            self._add_question(
                topic="CTE",
                difficulty="Advanced",
                question=f"Write a CTE to filter {table.name} and then query it.",
                answer=f"WITH filtered AS (SELECT * FROM {table.name} WHERE condition) SELECT * FROM filtered;",
                explanation="WITH creates a temporary named result set.",
                tip="CTEs make complex queries more readable and reusable."
            )
    
    def _generate_window_function_questions(self):
        for table in self.tables:
            # Check for timestamp or integer column
            order_cols = [c for c in table.columns if 'timestamp' in c.data_type.lower() or c.data_type in ['integer', 'date']]
            if order_cols:
                col = order_cols[0]
                self._add_question(
                    topic="Window Functions",
                    difficulty="Expert",
                    question=f"Use ROW_NUMBER() to rank records in {table.name} by {col.name}.",
                    answer=f"SELECT *, ROW_NUMBER() OVER (ORDER BY {col.name}) FROM {table.name};",
                    explanation=f"ROW_NUMBER() assigns sequential numbers ordered by {col.name}.",
                    tip="Use PARTITION BY to reset numbering for each group."
                )
    
    def _generate_case_questions(self):
        for table in self.tables:
            num_cols = [c for c in table.columns if c.data_type in ['integer', 'numeric', 'decimal']]
            if num_cols:
                col = num_cols[0]
                self._add_question(
                    topic="CASE",
                    difficulty="Advanced",
                    question=f"Use CASE to categorize {col.name} in {table.name} (e.g., 'High', 'Medium', 'Low').",
                    answer=f"SELECT *, CASE WHEN {col.name} > 100 THEN 'High' WHEN {col.name} > 50 THEN 'Medium' ELSE 'Low' END AS category FROM {table.name};",
                    explanation="CASE creates conditional logic.",
                    tip="CASE is evaluated in order; the first matching condition wins."
                )
    
    def _generate_date_questions(self):
        for table in self.tables:
            date_cols = [c for c in table.columns if 'timestamp' in c.data_type.lower() or c.data_type == 'date']
            if date_cols:
                col = date_cols[0]
                self._add_question(
                    topic="Date Functions",
                    difficulty="Advanced",
                    question=f"Extract the year from {col.name} in {table.name}.",
                    answer=f"SELECT EXTRACT(YEAR FROM {col.name}) FROM {table.name};",
                    explanation="EXTRACT(YEAR FROM ...) gets the year from a date.",
                    tip="Use DATE_TRUNC() for grouping by month, quarter, or year."
                )
    
    def _generate_string_questions(self):
        for table in self.tables:
            text_cols = [c for c in table.columns if 'char' in c.data_type.lower() or c.data_type == 'text']
            if text_cols:
                col = text_cols[0]
                self._add_question(
                    topic="String Functions",
                    difficulty="Advanced",
                    question=f"Convert {col.name} to uppercase in {table.name}.",
                    answer=f"SELECT UPPER({col.name}) FROM {table.name};",
                    explanation="UPPER() converts text to uppercase.",
                    tip="Use LOWER() for case-insensitive comparisons."
                )

PYEOF
echo "✅ More question types added"

# ============================================================
# 2. BETTER SCORING (portal_complete.py)
# ============================================================
# We'll add advanced scoring with syntax, grammar, keyword, structure scores
# Also add session save/load endpoints and export results

cat >> portal_complete.py << 'PYEOF'

# ============================================================
# ENHANCED SCORING
# ============================================================

def score_answer(user_answer, correct_answer):
    """Detailed scoring: syntax, grammar, keywords, structure"""
    import re
    user = user_answer.strip()
    correct = correct_answer.strip()
    
    # Normalize
    def normalize(sql):
        sql = sql.strip()
        if sql.endswith(';'):
            sql = sql[:-1]
        sql = ' '.join(sql.split())
        return sql.lower()
    
    user_norm = normalize(user)
    correct_norm = normalize(correct)
    
    # Syntax (semicolon, parentheses, quotes)
    syntax_score = 0
    if user.endswith(';'): syntax_score += 30
    if user.count('(') == user.count(')'): syntax_score += 30
    if user.count("'") % 2 == 0: syntax_score += 40
    syntax_score = min(100, syntax_score)
    
    # Grammar (presence of SELECT, FROM, WHERE, JOIN)
    grammar_score = 0
    user_upper = user.upper()
    if 'SELECT' in user_upper: grammar_score += 30
    if 'FROM' in user_upper: grammar_score += 30
    if 'WHERE' in correct_norm and 'WHERE' in user_norm: grammar_score += 20
    if 'JOIN' in correct_norm and 'JOIN' in user_norm: grammar_score += 20
    grammar_score = min(100, grammar_score)
    
    # Keywords match
    correct_keywords = set(re.findall(r'\b[A-Z_]+\b', correct.upper()))
    user_keywords = set(re.findall(r'\b[A-Z_]+\b', user.upper()))
    if correct_keywords:
        keyword_score = int(len(correct_keywords & user_keywords) / len(correct_keywords) * 100)
    else:
        keyword_score = 50
    keyword_score = min(100, keyword_score)
    
    # Structure (clause order)
    clauses = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY']
    correct_order = [c for c in clauses if c in correct.upper()]
    user_order = [c for c in clauses if c in user.upper()]
    if correct_order and user_order:
        # Check if all required clauses are present in order
        common = [c for c in user_order if c in correct_order]
        if common == correct_order:
            structure_score = 100
        elif all(c in user_order for c in correct_order):
            structure_score = 70
        else:
            structure_score = 40
    else:
        structure_score = 0
    
    total_score = int((syntax_score * 0.3 + grammar_score * 0.3 + keyword_score * 0.2 + structure_score * 0.2))
    is_correct = total_score >= 70
    
    return {
        'is_correct': is_correct,
        'total_score': total_score,
        'syntax_score': syntax_score,
        'grammar_score': grammar_score,
        'keyword_score': keyword_score,
        'structure_score': structure_score,
        'feedback': []
    }

# ============================================================
# SAVE / LOAD SESSIONS
# ============================================================

import json
from pathlib import Path

SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

@app.route('/api/practice/save/<session_id>', methods=['POST'])
def save_practice_session(session_id):
    try:
        if session_id not in practice_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = practice_sessions[session_id]
        data = {
            'user_name': session.user_name,
            'questions': [q.__dict__ for q in session.questions],
            'current_index': session.current_index,
            'results': session.results,
            'correct_answers': session.correct_answers,
            'total_hints_used': session.total_hints_used,
            'timestamp': datetime.now().isoformat()
        }
        filepath = SESSIONS_DIR / f"{session_id}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True, 'message': 'Session saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/load/<session_id>', methods=['GET'])
def load_practice_session(session_id):
    try:
        filepath = SESSIONS_DIR / f"{session_id}.json"
        if not filepath.exists():
            return jsonify({'error': 'Session not found'}), 404
        with open(filepath, 'r') as f:
            data = json.load(f)
        return jsonify({'session': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# EXPORT RESULTS
# ============================================================

@app.route('/api/practice/export/<session_id>', methods=['GET'])
def export_practice_results(session_id):
    try:
        if session_id not in practice_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = practice_sessions[session_id]
        # Generate CSV
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Question ID', 'User Answer', 'Correct Answer', 'Is Correct', 'Score'])
        for r in session.results:
            writer.writerow([r.get('question_id', ''), r.get('user_answer', ''), r.get('correct_answer', ''), r.get('is_correct', False), r.get('total_score', 0)])
        
        # Add summary
        summary = f"\n\nSummary:\nTotal: {len(session.results)}\nCorrect: {session.correct_answers}\nAccuracy: {session.get_stats()['accuracy']}\n"
        output.write(summary)
        
        return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': f'attachment; filename="practice_results_{session_id}.csv"'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

PYEOF

echo "✅ Enhanced scoring, save/load, export added"

# ============================================================
# 3. UPDATE PRACTICE HTML (frontend)
# ============================================================
cat > templates/practice_interactive.html << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <title>🎯 SQL Practice</title>
    <style>
        body { font-family: Arial; max-width: 900px; margin: 40px auto; padding: 20px; background: #f0f2f5; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }
        .btn { padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 5px; }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #333; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        input, select { padding: 8px; margin: 5px 0; width: 100%; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .question-box { background: #f8f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
        textarea { width: 100%; min-height: 120px; font-family: monospace; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .feedback { padding: 15px; border-radius: 5px; margin: 10px 0; display: none; }
        .feedback.correct { background: #d4edda; border: 1px solid #28a745; display: block; }
        .feedback.incorrect { background: #f8d7da; border: 1px solid #dc3545; display: block; }
        .feedback.partial { background: #fff3cd; border: 1px solid #ffc107; display: block; }
        .hidden { display: none; }
        .score-details { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0; }
        .score-item { background: white; padding: 8px; border-radius: 4px; text-align: center; }
        .score-item .value { font-size: 20px; font-weight: bold; }
        .debug-box { background: #1e1e1e; color: #d4d4d4; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; white-space: pre-wrap; margin-top: 20px; max-height: 200px; overflow-y: auto; }
        .toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0; }
        .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; }
        .badge-beginner { background: #d4edda; color: #155724; }
        .badge-intermediate { background: #fff3cd; color: #856404; }
        .badge-advanced { background: #f8d7da; color: #721c24; }
        .badge-expert { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎯 SQL Practice</h1>
        <a href="/">🏠 Back</a>
    </div>

    <!-- Setup -->
    <div class="card" id="setupCard">
        <h2>Start Practice</h2>
        <label>Your Name</label>
        <input type="text" id="userName" value="Anonymous">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:10px 0;">
            <div><label>⭐ Beginner</label><input type="number" id="beginner" value="2"></div>
            <div><label>⭐⭐ Intermediate</label><input type="number" id="intermediate" value="2"></div>
            <div><label>⭐⭐⭐ Advanced</label><input type="number" id="advanced" value="1"></div>
            <div><label>⭐⭐⭐⭐ Expert</label><input type="number" id="expert" value="0"></div>
        </div>
        <button class="btn btn-primary" id="startBtn" style="width:100%; padding:12px; font-size:18px;">🚀 Start Practice</button>
        <div id="debugLog" class="debug-box">Waiting for action...</div>
    </div>

    <!-- Practice -->
    <div class="card hidden" id="practiceCard">
        <div style="display:flex; justify-content:space-between; flex-wrap:wrap;">
            <h3 id="questionNum">Question 1 of 10</h3>
            <div>
                <span id="scoreDisplay">✅ 0</span>
                <span id="answeredDisplay">📝 0</span>
                <span id="hintDisplay">💡 0</span>
            </div>
        </div>
        <div class="question-box">
            <span id="topicDisplay" style="background:#667eea;color:white;padding:2px 10px;border-radius:10px;">Topic</span>
            <span id="diffDisplay" class="badge badge-beginner">Difficulty</span>
            <h3 id="questionText">Loading...</h3>
        </div>
        <textarea id="answerInput" placeholder="Write your SQL query..."></textarea>
        <div class="toolbar">
            <button class="btn btn-success" id="submitBtn">📤 Submit</button>
            <button class="btn btn-warning" id="hintBtn">💡 Hint (-20)</button>
            <button class="btn btn-danger" id="skipBtn">⏭️ Skip</button>
            <button class="btn btn-secondary" id="saveBtn">💾 Save</button>
            <button class="btn btn-secondary" id="exportBtn">📥 Export</button>
            <button class="btn btn-secondary" id="endBtn">🏁 End</button>
        </div>
        <div class="feedback" id="feedback"></div>
        <div id="scoreDetails" class="score-details" style="display:none;"></div>
    </div>

    <script>
        (function() {
            var debugLog = document.getElementById('debugLog');
            function log(msg) {
                debugLog.textContent += '\n[' + new Date().toLocaleTimeString() + '] ' + msg;
                debugLog.scrollTop = debugLog.scrollHeight;
                console.log(msg);
            }
            log('🟢 Page loaded');

            var setupCard = document.getElementById('setupCard');
            var practiceCard = document.getElementById('practiceCard');
            var startBtn = document.getElementById('startBtn');
            var userName = document.getElementById('userName');
            var beginner = document.getElementById('beginner');
            var intermediate = document.getElementById('intermediate');
            var advanced = document.getElementById('advanced');
            var expert = document.getElementById('expert');
            var questionNum = document.getElementById('questionNum');
            var scoreDisplay = document.getElementById('scoreDisplay');
            var answeredDisplay = document.getElementById('answeredDisplay');
            var hintDisplay = document.getElementById('hintDisplay');
            var topicDisplay = document.getElementById('topicDisplay');
            var diffDisplay = document.getElementById('diffDisplay');
            var questionText = document.getElementById('questionText');
            var answerInput = document.getElementById('answerInput');
            var feedback = document.getElementById('feedback');
            var scoreDetails = document.getElementById('scoreDetails');
            var submitBtn = document.getElementById('submitBtn');
            var hintBtn = document.getElementById('hintBtn');
            var skipBtn = document.getElementById('skipBtn');
            var saveBtn = document.getElementById('saveBtn');
            var exportBtn = document.getElementById('exportBtn');
            var endBtn = document.getElementById('endBtn');

            var sessionId = null;
            var currentQuestion = null;
            var isAnswered = false;

            startBtn.addEventListener('click', function() {
                log('🚀 Start button clicked');
                var name = userName.value || 'Anonymous';
                var b = parseInt(beginner.value) || 0;
                var i = parseInt(intermediate.value) || 0;
                var a = parseInt(advanced.value) || 0;
                var e = parseInt(expert.value) || 0;

                if (b+i+a+e === 0) {
                    alert('Select at least one question!');
                    return;
                }

                startBtn.disabled = true;
                startBtn.textContent = '⏳ Loading...';

                fetch('/api/practice/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_name: name, beginner: b, intermediate: i, advanced: a, expert: e})
                })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.error) { alert(data.error); startBtn.disabled=false; startBtn.textContent='🚀 Start Practice'; return; }
                    sessionId = data.session_id;
                    log('✅ Session: ' + sessionId);
                    setupCard.classList.add('hidden');
                    practiceCard.classList.remove('hidden');
                    loadQuestion();
                })
                .catch(function(e) { alert('Error: '+e.message); startBtn.disabled=false; startBtn.textContent='🚀 Start Practice'; });
            });

            function loadQuestion() {
                log('📥 Loading question');
                fetch('/api/practice/question/' + sessionId)
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.complete) {
                        questionText.textContent = '🎉 Practice Complete!';
                        answerInput.style.display = 'none';
                        submitBtn.disabled = true;
                        hintBtn.disabled = true;
                        return;
                    }
                    currentQuestion = data.question;
                    questionNum.textContent = 'Question ' + data.question.id + ' of ' + data.stats.total_questions;
                    questionText.textContent = currentQuestion.question;
                    topicDisplay.textContent = currentQuestion.topic;
                    diffDisplay.textContent = currentQuestion.difficulty;
                    diffDisplay.className = 'badge badge-' + currentQuestion.difficulty.toLowerCase();
                    answerInput.value = '';
                    feedback.className = 'feedback';
                    feedback.style.display = 'none';
                    scoreDetails.style.display = 'none';
                    isAnswered = false;
                    updateStats(data.stats);
                    log('✅ Question loaded: ' + currentQuestion.id);
                })
                .catch(function(e) { alert('Error loading question: '+e.message); });
            }

            submitBtn.addEventListener('click', function() {
                if (isAnswered) { alert('Already answered!'); return; }
                var answer = answerInput.value.trim();
                if (!answer) { alert('Write your SQL query!'); return; }
                log('📤 Submitting answer');
                fetch('/api/practice/answer/' + sessionId, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({answer: answer})
                })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.error) { alert(data.error); return; }
                    isAnswered = true;
                    var result = data.result;
                    feedback.style.display = 'block';
                    if (result.is_correct) {
                        feedback.className = 'feedback correct';
                        feedback.innerHTML = '<strong>✅ Correct!</strong> Score: ' + result.total_score + '/100';
                    } else {
                        feedback.className = 'feedback incorrect';
                        feedback.innerHTML = '<strong>❌ Incorrect</strong> Score: ' + result.total_score + '/100<br>' +
                            '<strong>Correct Answer:</strong> ' + result.correct_answer;
                    }
                    if (result.explanation) feedback.innerHTML += '<br><strong>Explanation:</strong> ' + result.explanation;
                    if (result.tip) feedback.innerHTML += '<br><strong>Tip:</strong> ' + result.tip;

                    // Show detailed scores
                    if (result.syntax_score !== undefined) {
                        scoreDetails.style.display = 'grid';
                        scoreDetails.innerHTML = `
                            <div class="score-item"><div class="value">${result.syntax_score}</div><div>Syntax</div></div>
                            <div class="score-item"><div class="value">${result.grammar_score}</div><div>Grammar</div></div>
                            <div class="score-item"><div class="value">${result.keyword_score}</div><div>Keywords</div></div>
                            <div class="score-item"><div class="value">${result.structure_score}</div><div>Structure</div></div>
                        `;
                    }
                    updateStats(data.stats);
                    if (data.complete) {
                        questionText.textContent = '🎉 Practice Complete!';
                        answerInput.style.display = 'none';
                        submitBtn.disabled = true;
                        hintBtn.disabled = true;
                    } else {
                        setTimeout(loadQuestion, 2000);
                    }
                })
                .catch(function(e) { alert('Error: '+e.message); });
            });

            hintBtn.addEventListener('click', function() {
                if (isAnswered) { alert('Already answered!'); return; }
                fetch('/api/practice/hint/' + sessionId)
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.error) { alert(data.error); return; }
                    alert('💡 Hint: ' + data.hint + '\n(-20 points penalty)');
                });
            });

            skipBtn.addEventListener('click', function() {
                if (!isAnswered && !confirm('Skip without answering?')) return;
                loadQuestion();
            });

            saveBtn.addEventListener('click', function() {
                if (!sessionId) { alert('No active session'); return; }
                fetch('/api/practice/save/' + sessionId, {method: 'POST'})
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.success) { alert('✅ Session saved!'); log('💾 Session saved'); }
                    else { alert('Error: '+data.error); }
                });
            });

            exportBtn.addEventListener('click', function() {
                if (!sessionId) { alert('No active session'); return; }
                window.open('/api/practice/export/' + sessionId, '_blank');
                log('📥 Exported results');
            });

            endBtn.addEventListener('click', function() {
                if (confirm('End practice?')) {
                    practiceCard.classList.add('hidden');
                    setupCard.classList.remove('hidden');
                    sessionId = null;
                    startBtn.disabled = false;
                    startBtn.textContent = '🚀 Start Practice';
                    log('🏁 Practice ended');
                }
            });

            function updateStats(stats) {
                if (!stats) return;
                scoreDisplay.textContent = '✅ ' + stats.correct;
                answeredDisplay.textContent = '📝 ' + stats.answered;
                hintDisplay.textContent = '💡 ' + (stats.total_hints_used || 0);
            }
        })();
    </script>
</body>
</html>
HTML

echo "✅ Practice HTML updated with new features"

# ============================================================
# FINAL STEPS
# ============================================================
echo "============================================================"
echo "✅ Upgrade complete!"
echo ""
echo "New features added:"
echo "  - More question types (subqueries, CTEs, window functions, etc.)"
echo "  - Enhanced scoring (syntax, grammar, keywords, structure)"
echo "  - Save session (persist to disk)"
echo "  - Export results as CSV"
echo ""
echo "Restart the portal to apply changes:"
echo "  pkill -f portal_complete.py && python portal_complete.py"
echo "============================================================"
