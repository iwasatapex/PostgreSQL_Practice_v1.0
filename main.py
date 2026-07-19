"""
SQL Workbook Generator

Generates SQL practice questions from:
1. SQL files (.sql) - CREATE TABLE statements
2. Python files (.py) - SQLAlchemy/Django models
3. Live PostgreSQL database (optional)
"""

import sys
from pathlib import Path

from parser.sql_parser import SQLParser
from parser.python_parser import PythonParser
from question_generator.format_generator import FormatQuestionGenerator
from generators.sql_generator import SQLGenerator
from generators.text_answers_generator import TextAnswersGenerator
from generators.docx_generator import DOCXGenerator


def generate_from_sql_file(sql_file: str, question_count: int = 1000):
    """Generate workbook from a SQL file."""
    
    print("=" * 70)
    print("SQL Workbook Generator - SQL File Mode")
    print("=" * 70)
    
    print(f"\n📄 Reading SQL file: {sql_file}")
    
    parser = SQLParser(sql_file)
    schema = parser.parse()
    
    print(f"✅ Found {len(schema.tables)} tables")
    print(f"✅ Found {len(schema.relationships)} relationships")
    
    return generate_workbook(schema, question_count)


def generate_from_python_file(python_file: str, question_count: int = 1000):
    """Generate workbook from a Python file."""
    
    print("=" * 70)
    print("SQL Workbook Generator - Python File Mode")
    print("=" * 70)
    
    print(f"\n🐍 Reading Python file: {python_file}")
    
    parser = PythonParser(python_file)
    schema = parser.parse()
    
    print(f"✅ Found {len(schema.tables)} tables")
    print(f"✅ Found {len(schema.relationships)} relationships")
    
    return generate_workbook(schema, question_count)


def generate_from_database(question_count: int = 1000):
    """Generate workbook from a live PostgreSQL database."""
    
    print("=" * 70)
    print("SQL Workbook Generator - Database Mode")
    print("=" * 70)
    
    from database.schema_reader import SchemaReader
    
    print("\n📊 Reading database schema...")
    reader = SchemaReader()
    tables = reader.read_schema()
    
    from models.schema import Schema
    schema = Schema()
    schema.tables = tables
    
    print(f"✅ Found {len(schema.tables)} tables")
    
    return generate_workbook(schema, question_count)


def generate_workbook(schema, question_count: int = 1000):
    """Generate workbook from schema."""
    
    # Analyze schema
    from parser.schema_analyzer import SchemaAnalyzer
    analyzer = SchemaAnalyzer(schema)
    features = analyzer.detect_features()
    
    print(f"\n📊 Schema Features:")
    print(f"  - JSONB columns: {'✅' if features['has_jsonb'] else '❌'}")
    print(f"  - Timestamps: {'✅' if features['has_timestamps'] else '❌'}")
    print(f"  - Recursive tables: {'✅' if features['has_recursive'] else '❌'}")
    print(f"  - JOIN candidates: {len(features['join_candidates'])}")
    
    # Generate questions
    print(f"\n🧠 Generating {question_count} questions...")
    generator = FormatQuestionGenerator(schema)
    questions = generator.generate_all(question_count)
    print(f"✅ Generated {len(questions)} questions")
    
    # Export
    _export_workbook(questions)
    
    return questions


def _export_workbook(questions):
    """Export questions to all formats."""
    
    # Export to SQL (basic answers)
    print("\n💾 Exporting SQL answers...")
    sql_gen = SQLGenerator(questions)
    sql_file = sql_gen.generate()
    print(f"✅ SQL file: {sql_file}")
    
    # Export comprehensive text answers
    print("\n📝 Exporting comprehensive text answers with explanations...")
    text_gen = TextAnswersGenerator(questions)
    text_file = text_gen.generate()
    print(f"✅ Text answers file: {text_file}")
    
    # Export to DOCX
    print("\n📝 Exporting DOCX workbook...")
    docx_gen = DOCXGenerator(questions)
    docx_file = docx_gen.generate()
    print(f"✅ DOCX file: {docx_file}")
    
    print("\n" + "=" * 70)
    print("✅ Workbook generation complete!")
    print(f"📁 Output directory: output/")
    print("   📄 SQL_Workbook.docx - Questions only (printable)")
    print("   📄 ANSWERS.txt - Comprehensive answers with explanations")
    print("=" * 70)


def show_help():
    """Show usage help."""
    
    print("""
SQL Workbook Generator
======================

Usage:
    python main.py [file.sql] [count]    - Generate from SQL file
    python main.py [file.py] [count]     - Generate from Python file
    python main.py --database [count]    - Generate from live database
    python main.py --help                - Show this help

Examples:
    # Generate 1000 questions from SQL file
    python main.py examples/ecommerce.sql
    
    # Generate 500 questions from SQL file
    python main.py examples/ecommerce.sql 500
    
    # Generate 2000 questions from Python file
    python main.py examples/models.py 2000
    
    # Generate 1000 questions from live database
    python main.py --database
""")


def main():
    """Main entry point."""
    
    if len(sys.argv) == 1:
        show_help()
        return
    
    arg = sys.argv[1]
    
    # Default question count
    question_count = 1000
    
    # Check for question count parameter
    if len(sys.argv) > 2:
        try:
            question_count = int(sys.argv[2])
        except ValueError:
            print(f"❌ Invalid question count: {sys.argv[2]}")
            show_help()
            return
    
    if arg == "--help" or arg == "-h":
        show_help()
    elif arg == "--database":
        generate_from_database(question_count)
    else:
        file_path = Path(arg)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            show_help()
            return
        
        # Check file extension
        if file_path.suffix.lower() == '.sql':
            generate_from_sql_file(arg, question_count)
        elif file_path.suffix.lower() == '.py':
            generate_from_python_file(arg, question_count)
        else:
            print(f"❌ Unsupported file type: {file_path.suffix}")
            print("Supported: .sql, .py")
            show_help()


if __name__ == "__main__":
    main()
