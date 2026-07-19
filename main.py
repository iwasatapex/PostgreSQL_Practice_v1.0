#!/usr/bin/env python3
import sys, json
from pathlib import Path
from datetime import datetime

from parser.sql_parser import SQLParser
from parser.python_parser import PythonParser
from question_generator.format_generator import FormatQuestionGenerator
from generators.sql_generator import SQLGenerator
from generators.pdf_generator import PDFGenerator

def generate_from_file(file_path, question_count=100):
    ext = Path(file_path).suffix.lower()
    print(f"📄 Reading file: {file_path}")
    
    if ext == '.sql':
        parser = SQLParser(file_path)
    elif ext == '.py':
        parser = PythonParser(file_path)
    else:
        print(f"❌ Unsupported file type: {ext}")
        return
    
    schema = parser.parse()
    print(f"✅ Found {len(schema.tables)} tables")
    
    generator = FormatQuestionGenerator(schema.tables)
    questions = generator.generate_all(question_count)
    print(f"✅ Generated {len(questions)} questions")
    
    # Export SQL
    sql_gen = SQLGenerator(questions)
    sql_file = sql_gen.generate()
    print(f"💾 SQL: {sql_file}")
    
    # Export PDF
    pdf_gen = PDFGenerator(questions)
    pdf_file = pdf_gen.generate()
    print(f"📄 PDF: {pdf_file}")
    
    print("✅ Done!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <file> [question_count]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    generate_from_file(file_path, count)
