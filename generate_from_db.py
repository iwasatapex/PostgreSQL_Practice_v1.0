#!/usr/bin/env python3
import json
import psycopg2
import sys
import os
from datetime import datetime

DB_SETTINGS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "4m4teur",
    "host": "localhost",
    "port": "5432"
}

def generate_questions(count=100):
    conn = psycopg2.connect(**DB_SETTINGS)
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = [row[0] for row in cursor.fetchall()]
    questions = []
    for table in tables:
        questions.append({
            'id': len(questions) + 1,
            'topic': 'SELECT',
            'difficulty': 'Beginner',
            'question': f"List all records from {table}.",
            'answer': f"SELECT * FROM {table};",
            'explanation': f"SELECT * returns all columns from {table}.",
            'tip': "Use specific columns instead of SELECT *."
        })
    cursor.close()
    conn.close()
    os.makedirs('output', exist_ok=True)
    filename = f"output/workbook_from_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(questions[:count], f, indent=2)
    print(f"✅ Generated {len(questions[:count])} questions")
    print(f"📁 Saved to: {filename}")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    generate_questions(count)
