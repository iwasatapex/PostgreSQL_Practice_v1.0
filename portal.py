"""
SQL Workbook Generator - Unified Web Portal
Everything in one place: Generate, Practice, Manage Databases
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Configuration
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
UPLOAD_DIR = BASE_DIR / "uploads"
EXAMPLES_DIR = BASE_DIR / "examples"

# Create directories
for dir_path in [OUTPUT_DIR, UPLOAD_DIR]:
    dir_path.mkdir(exist_ok=True)

# Store session data
sessions = {}

# Available example files
EXAMPLE_FILES = []
if EXAMPLES_DIR.exists():
    EXAMPLE_FILES = [f.name for f in EXAMPLES_DIR.glob("*.sql")] + [f.name for f in EXAMPLES_DIR.glob("*.py")]


@app.route('/')
def index():
    """Home page - Unified Dashboard."""
    return render_template('portal.html', 
                         examples=EXAMPLE_FILES,
                         output_files=list(OUTPUT_DIR.glob("*")))


@app.route('/api/generate', methods=['POST'])
def generate_workbook():
    """Generate workbook with specified parameters."""
    data = request.json
    file_path = data.get('file_path', 'examples/ecommerce.sql')
    question_count = int(data.get('question_count', 100))
    
    # Validate file exists
    if not Path(file_path).exists():
        return jsonify({'error': f'File not found: {file_path}'}), 400
    
    # Generate command
    cmd = f"python main.py {file_path} {question_count}"
    
    try:
        # Run the generation
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=BASE_DIR
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Generation failed',
                'output': result.stdout + result.stderr
            }), 500
        
        # Find generated files
        generated_files = []
        for ext in ['docx', 'sql', 'txt', 'pdf']:
            for f in OUTPUT_DIR.glob(f"*.{ext}"):
                if f.stat().st_size > 0:  # Only non-empty files
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


@app.route('/api/database/generate', methods=['POST'])
def generate_database():
    """Generate practice database."""
    data = request.json
    rows = int(data.get('rows', 100))
    
    try:
        # Update database_generator.py with custom rows
        # Read the file
        with open('database_generator.py', 'r') as f:
            content = f.read()
        
        # Update ROWS_PER_TABLE
        import re
        content = re.sub(r'ROWS_PER_TABLE = \d+', f'ROWS_PER_TABLE = {rows}', content)
        
        with open('database_generator.py', 'w') as f:
            f.write(content)
        
        # Run database generator
        cmd = f"python database_generator.py"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Database generation failed',
                'output': result.stdout + result.stderr
            }), 500
        
        return jsonify({
            'success': True,
            'output': result.stdout,
            'rows': rows
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/practice/session', methods=['POST'])
def create_practice_session():
    """Create an interactive practice session."""
    data = request.json
    file_path = data.get('file_path', 'examples/ecommerce.sql')
    
    # Start interactive web app as subprocess
    # For simplicity, we'll redirect to the practice app
    return jsonify({
        'success': True,
        'url': '/practice',
        'message': 'Redirecting to practice session...'
    })


@app.route('/practice')
def practice():
    """Interactive practice page."""
    return render_template('practice_enhanced.html')


@app.route('/api/files', methods=['GET'])
def list_files():
    """List all available files."""
    files = {
        'examples': EXAMPLE_FILES,
        'output': [f.name for f in OUTPUT_DIR.glob("*") if f.is_file()],
        'uploads': [f.name for f in UPLOAD_DIR.glob("*") if f.is_file()]
    }
    return jsonify(files)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a SQL or Python file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ['.sql', '.py', '.txt']:
        return jsonify({'error': 'Only .sql, .py, .txt files allowed'}), 400
    
    # Save file
    filename = file.filename
    filepath = UPLOAD_DIR / filename
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'path': str(filepath),
        'message': f'File {filename} uploaded successfully'
    })


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a generated file."""
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)


@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file."""
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        filepath.unlink()
        return jsonify({'success': True, 'message': f'Deleted {filename}'})
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/practice/start', methods=['POST'])
def start_practice():
    """Start interactive practice session."""
    data = request.json
    file_path = data.get('file_path', 'examples/ecommerce.sql')
    beginner = int(data.get('beginner', 3))
    intermediate = int(data.get('intermediate', 3))
    advanced = int(data.get('advanced', 2))
    expert = int(data.get('expert', 2))
    
    # Store session data
    session_id = str(len(sessions) + 1)
    sessions[session_id] = {
        'file_path': file_path,
        'counts': {
            'beginner': beginner,
            'intermediate': intermediate,
            'advanced': advanced,
            'expert': expert
        },
        'created': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'redirect': '/practice'
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status."""
    return jsonify({
        'status': 'running',
        'version': '1.0',
        'output_files': len(list(OUTPUT_DIR.glob("*"))),
        'examples': len(EXAMPLE_FILES),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/clear_output', methods=['POST'])
def clear_output():
    """Clear all output files."""
    for f in OUTPUT_DIR.glob("*"):
        if f.is_file():
            f.unlink()
    return jsonify({'success': True, 'message': 'Output directory cleared'})


if __name__ == '__main__':
    # Ensure templates exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=51861)
