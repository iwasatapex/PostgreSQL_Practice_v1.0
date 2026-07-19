"""
SQL Workbook Generator - CLI Entry Point
"""

import sys
from pathlib import Path

from parser.sql_parser import SQLParser
from parser.python_parser import PythonParser
from question_generator.format_generator import FormatQuestionGenerator
from generators.sql_generator import SQLGenerator
from generators.docx_generator import DOCXGenerator


def generate_from_sql_file(sql_file: str, question_count: int = 100):
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


def generate_from_python_file(python_file: str, question_count: int = 100):
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


def generate_workbook(schema, question_count: int = 100):
    """Generate workbook from schema."""
    
    # Generate questions
    print(f"\n🧠 Generating {question_count} questions...")
    generator = FormatQuestionGenerator(schema.tables)
    questions = generator.generate_all(question_count)
    print(f"✅ Generated {len(questions)} questions")
    
    # Export
    _export_workbook(questions)
    
    return questions


def _export_workbook(questions):
    """Export questions to all formats."""
    # Export to SQL
    print("\n💾 Exporting SQL answers...")
    sql_gen = SQLGenerator(questions)
    sql_file = sql_gen.generate()
    print(f"✅ SQL file: {sql_file}")
    
    # Export to DOCX
    print("\n📝 Exporting DOCX workbook...")
    docx_gen = DOCXGenerator(questions)
    docx_file = docx_gen.generate()
    print(f"✅ DOCX file: {docx_file}")
    
    print("\n" + "=" * 70)
    print("✅ Workbook generation complete!")
    print(f"📁 Output directory: output/")
    print("=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <sql_file> [question_count]")
        print("Example: python main.py examples/ecommerce.sql 100")
        return
    
    file_path = Path(sys.argv[1])
    question_count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    if file_path.suffix.lower() == '.sql':
        generate_from_sql_file(str(file_path), question_count)
    elif file_path.suffix.lower() == '.py':
        generate_from_python_file(str(file_path), question_count)
    else:
        print(f"❌ Unsupported file type: {file_path.suffix}")


if __name__ == "__main__":
    main()
