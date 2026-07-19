#!/usr/bin/env python3
"""
PostgreSQL Practice - Complete Portal
All features: Generate Database, Interactive Practice, Generate Workbook, Upload Schema
"""

import os, json, subprocess, socket, sys, random, psycopg2
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
UPLOAD_DIR = BASE_DIR / "uploads"
EXAMPLES_DIR = BASE_DIR / "examples"
SESSIONS_DIR = BASE_DIR / "sessions"

for dir_path in [OUTPUT_DIR, UPLOAD_DIR, SESSIONS_DIR]:
    dir_path.mkdir(exist_ok=True)

EXAMPLE_FILES = []
if EXAMPLES_DIR.exists():
    EXAMPLE_FILES = [f.name for f in EXAMPLES_DIR.glob("*.sql")] + [f.name for f in EXAMPLES_DIR.glob("*.py")]

DB_SETTINGS = {"dbname": "postgres", "user": "postgres", "password": "4m4teur", "host": "localhost", "port": "5432"}

def get_db_connection():
    try: return psycopg2.connect(**DB_SETTINGS)
    except: return None

def get_tables():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close(); conn.close()
    return tables

def get_table_data(table_name, limit=100):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    result = [dict(zip(columns, row)) for row in rows]
    cursor.close(); conn.close()
    return result

def get_table_schema(table_name):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name, data_type, is_nullable = 'YES' as nullable,
        (SELECT COUNT(*) FROM information_schema.key_column_usage WHERE table_name = %s AND column_name = c.column_name AND constraint_name LIKE '%pkey%') as primary_key,
        (SELECT COUNT(*) FROM information_schema.key_column_usage WHERE table_name = %s AND column_name = c.column_name AND constraint_name LIKE '%fkey%') as foreign_key
        FROM information_schema.columns c WHERE table_schema='public' AND table_name = %s ORDER BY ordinal_position;
    """, (table_name, table_name, table_name))
    columns = [{'name': row[0], 'data_type': row[1], 'nullable': row[2], 'primary_key': row[3] > 0, 'foreign_key': row[4] > 0} for row in cursor.fetchall()]
    cursor.close(); conn.close()
    return columns

def get_table_count(table_name):
    conn = get_db_connection()
    if not conn: return 0
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    cursor.close(); conn.close()
    return count

def get_db_stats():
    conn = get_db_connection()
    if not conn: return {'total_tables': 0, 'total_rows': 0, 'db_size': '0 MB'}
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
    total_tables = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(reltuples) FROM pg_class WHERE relkind = 'r' AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');")
    total_rows = int(cursor.fetchone()[0] or 0)
    cursor.execute("SELECT pg_database_size('postgres');")
    db_size_bytes = cursor.fetchone()[0]
    db_size_mb = round(db_size_bytes / 1024 / 1024, 2)
    db_size = f"{db_size_mb} MB" if db_size_mb < 1024 else f"{round(db_size_mb/1024, 2)} GB"
    cursor.close(); conn.close()
    return {'total_tables': total_tables, 'total_rows': total_rows, 'db_size': db_size, 'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')}

SAMPLE_QUESTIONS = [
    {'id': 1, 'topic': 'SELECT', 'difficulty': 'Beginner', 'question': 'List all records from the users table.', 'answer': 'SELECT * FROM users;', 'explanation': 'SELECT * returns every column and row.', 'tip': 'Use specific columns instead of SELECT *.', 'hint': 'Use SELECT * FROM users'},
    {'id': 2, 'topic': 'WHERE', 'difficulty': 'Beginner', 'question': 'Find all users where email is NULL.', 'answer': 'SELECT * FROM users WHERE email IS NULL;', 'explanation': 'IS NULL checks for NULL values.', 'tip': 'Use IS NULL instead of = NULL.', 'hint': 'Use WHERE email IS NULL'},
    {'id': 3, 'topic': 'ORDER BY', 'difficulty': 'Beginner', 'question': 'List products ordered by price highest to lowest.', 'answer': 'SELECT * FROM products ORDER BY price DESC;', 'explanation': 'ORDER BY price DESC sorts highest to lowest.', 'tip': 'DESC shows largest numbers first.', 'hint': 'Use ORDER BY price DESC'},
    {'id': 4, 'topic': 'JOIN', 'difficulty': 'Intermediate', 'question': 'Show orders with customer usernames.', 'answer': 'SELECT o.order_id, u.username FROM orders o JOIN users u ON o.user_id = u.user_id;', 'explanation': 'JOIN connects orders to users.', 'tip': 'Use table aliases (o, u).', 'hint': 'Use JOIN with ON condition'},
    {'id': 5, 'topic': 'GROUP BY', 'difficulty': 'Intermediate', 'question': 'Count orders per user.', 'answer': 'SELECT user_id, COUNT(*) AS order_count FROM orders GROUP BY user_id;', 'explanation': 'GROUP BY creates one row per user.', 'tip': 'All non-aggregated columns must be in GROUP BY.', 'hint': 'Use GROUP BY user_id'}
]

practice_sessions = {}

class PracticeSession:
    def __init__(self, user_name, questions):
        self.user_name = user_name
        self.questions = questions
        self.current_index = 0
        self.results = []
        self.correct_answers = 0
        self.total_hints_used = 0
        self.hint_used_for_current = False

    def get_current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def get_hint(self):
        q = self.get_current_question()
        if q:
            self.hint_used_for_current = True
            self.total_hints_used += 1
            return q.get('hint', 'Think about the SQL syntax!')
        return None

    def submit_answer(self, user_answer):
        q = self.get_current_question()
        if not q: return {'error': 'No question'}
        correct = q['answer'].strip().lower().replace(';', '').strip() == user_answer.strip().lower().replace(';', '').strip()
        total_score = 100 if correct else 50
        if self.hint_used_for_current: total_score -= 20
        total_score = max(0, total_score)
        result = {
            'is_correct': correct,
            'total_score': total_score,
            'used_hint': self.hint_used_for_current,
            'correct_answer': q['answer'],
            'explanation': q.get('explanation', ''),
            'tip': q.get('tip', ''),
            'feedback': []
        }
        if correct and self.hint_used_for_current:
            result['feedback'].append("✅ Correct! (Hint penalty: -20)")
        elif correct:
            result['feedback'].append("✅ Perfect! Full score!")
        elif self.hint_used_for_current:
            result['feedback'].append("❌ Incorrect. Hint used: -20 penalty.")
        else:
            result['feedback'].append("❌ Incorrect. Review the correct answer.")
        self.results.append(result)
        if correct: self.correct_answers += 1
        self.hint_used_for_current = False
        self.current_index += 1
        return result

    def get_stats(self):
        total = len(self.results)
        correct = self.correct_answers
        accuracy = (correct / total * 100) if total > 0 else 0
        return {
            'total_questions': len(self.questions),
            'answered': total,
            'correct': correct,
            'accuracy': f"{accuracy:.1f}%",
            'total_hints_used': self.total_hints_used,
            'user_name': self.user_name,
            'remaining': len(self.questions) - self.current_index
        }

@app.route('/')
def index():
    return render_template('portal_complete.html', examples=EXAMPLE_FILES)


# ============================================================
# PRACTICE API
# ============================================================


@app.route('/practice')
def practice():
    return render_template('practice_interactive.html')
@app.route('/api/practice/start', methods=['POST'])
def start_practice():
    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'No data received'}), 400
        user_name = data.get('user_name', 'Anonymous')
        beginner = int(data.get('beginner', 2))
        intermediate = int(data.get('intermediate', 2))
        advanced = int(data.get('advanced', 1))
        expert = int(data.get('expert', 0))
        questions = []
        for diff, count in [('Beginner', beginner), ('Intermediate', intermediate), ('Advanced', advanced), ('Expert', expert)]:
            for i in range(min(count, len(SAMPLE_QUESTIONS))):
                q = SAMPLE_QUESTIONS[i % len(SAMPLE_QUESTIONS)].copy()
                q['id'] = len(questions) + 1
                q['difficulty'] = diff
                questions.append(q)
        if not questions: return jsonify({'error': 'No questions generated'}), 400
        session_id = f"session_{int(datetime.now().timestamp())}"
        practice_sessions[session_id] = PracticeSession(user_name, questions)
        return jsonify({'success': True, 'session_id': session_id, 'total_questions': len(questions)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/question/<session_id>', methods=['GET'])
def get_practice_question(session_id):
    try:
        if session_id not in practice_sessions: return jsonify({'error': 'Session not found'}), 404
        session = practice_sessions[session_id]
        question = session.get_current_question()
        if not question: return jsonify({'complete': True, 'stats': session.get_stats()})
        return jsonify({
            'question': {
                'id': question.get('id', session.current_index + 1),
                'topic': question.get('topic', 'SQL'),
                'difficulty': question.get('difficulty', 'Beginner'),
                'question': question.get('question', ''),
                'explanation': question.get('explanation', ''),
                'tip': question.get('tip', '')
            },
            'stats': session.get_stats()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/hint/<session_id>', methods=['GET'])
def get_practice_hint(session_id):
    try:
        if session_id not in practice_sessions: return jsonify({'error': 'Session not found'}), 404
        session = practice_sessions[session_id]
        hint = session.get_hint()
        if not hint: return jsonify({'error': 'No hint available'}), 404
        return jsonify({'hint': hint, 'penalty': 20})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/answer/<session_id>', methods=['POST'])
def submit_practice_answer(session_id):
    try:
        if session_id not in practice_sessions: return jsonify({'error': 'Session not found'}), 404
        data = request.get_json()
        user_answer = data.get('answer', '')
        session = practice_sessions[session_id]
        result = session.submit_answer(user_answer)
        if 'error' in result: return jsonify({'error': result['error']}), 400
        return jsonify({'result': result, 'stats': session.get_stats(), 'complete': session.current_index >= len(session.questions)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/next/<session_id>', methods=['POST'])
def next_practice_question(session_id):
    try:
        if session_id not in practice_sessions: return jsonify({'error': 'Session not found'}), 404
        session = practice_sessions[session_id]
        session.current_index += 1
        question = session.get_current_question()
        if not question: return jsonify({'complete': True, 'stats': session.get_stats()})
        return jsonify({
            'question': {'id': session.current_index + 1, 'topic': question.get('topic', 'SQL'), 'difficulty': question.get('difficulty', 'Beginner'), 'question': question.get('question', '')},
            'stats': session.get_stats()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice/stats/<session_id>', methods=['GET'])
def get_practice_stats(session_id):
    try:
        if session_id not in practice_sessions: return jsonify({'error': 'Session not found'}), 404
        return jsonify(practice_sessions[session_id].get_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# GENERATE DATABASE
# ============================================================

@app.route('/api/database/generate', methods=['POST'])
def generate_database():
    try:
        data = request.get_json()
        domain = data.get('domain', 'ecommerce')
        rows = int(data.get('rows', 100))
        cmd = f"python database_generator.py --domain {domain} --rows {rows}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=BASE_DIR)
        if result.returncode != 0:
            return jsonify({'error': 'Database failed', 'output': result.stdout + result.stderr}), 500
        return jsonify({'success': True, 'output': result.stdout, 'domain': domain, 'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# GENERATE WORKBOOK
# ============================================================

@app.route('/api/generate', methods=['POST'])
def generate_workbook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        file_path = data.get('file_path', 'examples/ecommerce.sql')
        question_count = int(data.get('question_count', 100))
        
        if not Path(file_path).exists():
            return jsonify({'error': f'File not found: {file_path}'}), 400
        
        cmd = f"python main.py {file_path} {question_count}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=BASE_DIR)
        
        if result.returncode != 0:
            return jsonify({'error': 'Generation failed', 'output': result.stdout + result.stderr}), 500
        
        # Generate PDF directly from questions
        try:
            # Parse the output to get questions (this is a simplification)
            # In production, you'd parse the actual questions from the output
            from models.question import Question
            import json
            # Look for the generated JSON file
            json_files = list(OUTPUT_DIR.glob("*.json"))
            if json_files:
                with open(json_files[-1], 'r') as f:
                    questions_data = json.load(f)
                questions = [Question(**q) for q in questions_data]
                pdf_gen = PDFGenerator(questions)
                pdf_gen.generate()
        except Exception as e:
            print(f"PDF generation error: {e}")
        
        generated_files = []
        for ext in ['pdf', 'sql', 'json']:
            for f in OUTPUT_DIR.glob(f"*.{ext}"):
                if f.stat().st_size > 0:
                    generated_files.append({
                        'name': f.name,
                        'size': f.stat().st_size,
                        'modified': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'path': str(f)
                    })
        
        return jsonify({
            'success': True,
            'output': result.stdout,
            'files': generated_files,
            'question_count': question_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# FILE MANAGEMENT
# ============================================================

@app.route('/api/files', methods=['GET'])
def list_files():
    files = {
        'examples': EXAMPLE_FILES,
        'output': [f.name for f in OUTPUT_DIR.glob("*") if f.is_file()],
        'uploads': [f.name for f in UPLOAD_DIR.glob("*") if f.is_file()]
    }
    return jsonify(files)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    ext = Path(file.filename).suffix.lower()
    if ext not in ['.sql', '.py', '.txt']:
        return jsonify({'error': 'Only .sql, .py, .txt files allowed'}), 400
    filename = secure_filename(file.filename)
    filepath = UPLOAD_DIR / filename
    file.save(filepath)
    return jsonify({'success': True, 'filename': filename, 'path': str(filepath), 'message': f'File {filename} uploaded'})

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True)

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        filepath.unlink()
        return jsonify({'success': True, 'message': f'Deleted {filename}'})
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/clear_output', methods=['POST'])
def clear_output():
    for f in OUTPUT_DIR.glob("*"):
        if f.is_file():
            f.unlink()
    return jsonify({'success': True, 'message': 'Output directory cleared'})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': 'running',
        'version': '1.0',
        'output_files': len(list(OUTPUT_DIR.glob("*"))),
        'examples': len(EXAMPLE_FILES),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/db_viewer')
def db_viewer():
    return render_template('db_viewer.html')

@app.route('/api/db/tables', methods=['GET'])
def get_db_tables():
    response = jsonify({'tables': get_tables()})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/db/view/<table_name>', methods=['GET'])
def view_table(table_name):
    data = get_table_data(table_name)
    response = jsonify({'rows': data, 'count': len(data)})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/db/schema/<table_name>', methods=['GET'])
def get_table_schema_api(table_name):
    response = jsonify({'columns': get_table_schema(table_name)})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/db/stats', methods=['GET'])
def get_db_stats_api():
    response = jsonify(get_db_stats())
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def find_free_port():
    for port in range(5002, 5010):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            continue
    return None

if __name__ == '__main__':
    port = find_free_port()
    if port is None:
        print("❌ No free ports available")
        sys.exit(1)
    if port != 5002:
        print(f"⚠️  Port 5002 is busy. Using port {port} instead.")
    print(f"\n🚀 PostgreSQL Practice - Complete Portal")
    print(f"🌐 Open: http://localhost:{port}")
    print("=" * 50)
    print("📄 Generate Workbook  - Create SQL practice workbooks")
    print("🎯 Interactive Practice - Practice SQL with feedback")
    print("🗄️ Generate Database   - Create practice databases")
    print("📤 Upload Schema      - Upload SQL/Python files")
    print("📂 File Management    - Download, delete files")
    print("🔍 Database Viewer    - View tables and data")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print("")
    app.run(debug=True, host='0.0.0.0', port=port)

