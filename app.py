"""
SQL Workbook Generator - Web Interface
Upload SQL or Python files to generate workbooks.
"""

import os
from pathlib import Path
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename

from parser.sql_parser import SQLParser
from parser.python_parser import PythonParser
from parser.schema_analyzer import SchemaAnalyzer
from question_generator.mega_generator import MegaQuestionGenerator
from generators.sql_generator import SQLGenerator
from generators.docx_generator import DOCXGenerator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'sql', 'txt', 'py'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload .sql, .py, or .txt files'}), 400
    
    # Get question count
    question_count = request.form.get('count', 1000)
    try:
        question_count = int(question_count)
    except ValueError:
        question_count = 1000
    
    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        ext = Path(filename).suffix.lower()
        
        if ext in ['.sql', '.txt']:
            parser = SQLParser(filepath)
        elif ext == '.py':
            parser = PythonParser(filepath)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        
        schema = parser.parse()
        
        analyzer = SchemaAnalyzer(schema)
        features = analyzer.detect_features()
        
        generator = MegaQuestionGenerator(schema)
        questions = generator.generate_all(question_count)
        
        sql_gen = SQLGenerator(questions)
        sql_file = sql_gen.generate()
        
        docx_gen = DOCXGenerator(questions)
        docx_file = docx_gen.generate()
        
        # Count by difficulty
        difficulty_counts = {}
        for q in questions:
            difficulty_counts[q.difficulty] = difficulty_counts.get(q.difficulty, 0) + 1
        
        result = {
            'success': True,
            'filename': filename,
            'file_type': ext,
            'tables': len(schema.tables),
            'relationships': len(schema.relationships),
            'questions': len(questions),
            'difficulty_counts': difficulty_counts,
            'features': features,
            'sql_file': str(sql_file),
            'docx_file': str(docx_file)
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filetype>/<filename>')
def download_file(filetype, filename):
    if filetype == 'sql':
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], 'Answers.sql')
    elif filetype == 'docx':
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], 'SQL_Workbook.docx')
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
