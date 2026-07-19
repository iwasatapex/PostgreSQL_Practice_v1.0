cat > main.py << 'EOF'
from database.schema_reader import SchemaReader
from question_generator.generator import QuestionGenerator
from generators.sql_generator import SQLGenerator
from generators.docx_generator import DOCXGenerator


def main():
    print("=" * 70)
    print("SQL Workbook Generator")
    print("=" * 70)
    
    # 1. Read schema
    print("\n📊 Reading database schema...")
    reader = SchemaReader()
    tables = reader.read_schema()
    print(f"✅ Found {len(tables)} tables")
    
    # 2. Generate questions
    print("\n🧠 Generating questions...")
    generator = QuestionGenerator(tables)
    questions = generator.generate_all()
    print(f"✅ Generated {len(questions)} questions")
    
    # 3. Export to SQL
    print("\n💾 Exporting SQL answers...")
    sql_gen = SQLGenerator(questions)
    sql_file = sql_gen.generate()
    print(f"✅ SQL file: {sql_file}")
    
    # 4. Export to DOCX
    print("\n📝 Exporting DOCX workbook...")
    docx_gen = DOCXGenerator(questions)
    docx_file = docx_gen.generate()
    print(f"✅ DOCX file: {docx_file}")
    
    print("\n" + "=" * 70)
    print("✅ Workbook generation complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
EOF
