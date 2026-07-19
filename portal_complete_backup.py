"""
PostgreSQL Practice - Complete Integrated Portal
All features in one place: Generate, Practice, Database, Upload

import os
import json
import subprocess
import socket
import sys
import random
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
app = Flask(__name__)
app.secret_key = os.urandom(24)
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
UPLOAD_DIR = BASE_DIR / "uploads"
EXAMPLES_DIR = BASE_DIR / "examples"
for dir_path in [OUTPUT_DIR, UPLOAD_DIR]:
    dir_path.mkdir(exist_ok=True)
EXAMPLE_FILES = []
if EXAMPLES_DIR.exists():
    EXAMPLE_FILES = [f.name for f in EXAMPLES_DIR.glob("*.sql")] + [f.name for f in EXAMPLES_DIR.glob("*.py")]
@app.route('/db_viewer')
def db_viewer():
    return render_template('db_viewer.html')
@app.route('/api/db/tables', methods=['GET'])
def get_db_tables():
        cursor.execute("""
    SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        return jsonify({'tables': tables})
        return jsonify({'rows': result, 'count': len(result)})

# ============================================================
# DATABASE VIEWER
# ============================================================

@app.route('/db_viewer')
def db_viewer():
    return render_template('db_viewer.html')

@app.route('/api/db/tables', methods=['GET'])
def get_db_tables():
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="4m4teur",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({'tables': tables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/view/<table_name>', methods=['GET'])
def view_table(table_name):
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="4m4teur",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100;")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return jsonify({'rows': result, 'count': len(result)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
