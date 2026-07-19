#!/bin/bash
# ============================================
# PostgreSQL Practice - Cleanup Script
# Removes redundant files and organizes project
# ============================================

echo "========================================"
echo "  🧹 PostgreSQL Practice - Cleanup"
echo "========================================"
echo ""

# Backup warning
echo "⚠️  This will remove redundant files."
echo "   Your essential files will be kept."
echo "   Press Enter to continue or Ctrl+C to cancel"
read

# ============================================
# 1. REMOVE OLD TEMPLATES (Keep only essential)
# ============================================
echo "📁 Cleaning templates..."
cd templates
rm -f portal.html portal_magical.html bee_garden.html garden.html
rm -f practice_enhanced.html practice_enhanced_complete.html practice_simple.html
cd ..
echo "   ✅ Templates cleaned"

# ============================================
# 2. REMOVE OLD PYTHON FILES
# ============================================
echo "🐍 Cleaning old Python files..."
rm -f interactive.py
rm -f interactive_web.py
rm -f interactive_web_enhanced.py
rm -f app.py
rm -f practice_server.py
rm -f practice_enhanced_complete.py
rm -f test_server.py
rm -f minimal_portal.py
rm -f convert_commands_to_pdf.py
rm -f portal_complete.py
rm -f test_generator.py
rm -f create_icon.py
echo "   ✅ Old Python files removed"

# ============================================
# 3. REMOVE OLD LAUNCHERS (Keep launch.sh)
# ============================================
echo "🚀 Cleaning old launchers..."
rm -f launch_portal.sh
rm -f launch_portal.bat
rm -f launch_portal.command
rm -f start.py
rm -f learn.sh
rm -f setup.sh
rm -f setup_environment.sh
echo "   ✅ Old launchers removed"

# ============================================
# 4. REMOVE OLD GENERATORS
# ============================================
echo "⚙️  Cleaning old generators..."
rm -f generators/pdf_generator.py
rm -f generators/ai_generator.py
rm -f generators/validator.py
rm -f generators/sql_export.py
echo "   ✅ Old generators removed"

# ============================================
# 5. REMOVE OLD QUESTION GENERATORS
# ============================================
echo "📝 Cleaning old question generators..."
rm -f question_generator/enhanced_generator.py
rm -f question_generator/difficulty.py
rm -f question_generator/templates.py
echo "   ✅ Old question generators removed"

# ============================================
# 6. REMOVE OLD CONFIG FILES
# ============================================
echo "⚙️  Cleaning old config files..."
rm -f config.py.example
rm -f bee_config.py
rm -f bee_world.py
echo "   ✅ Old config files removed"

# ============================================
# 7. REMOVE EMPTY FOLDERS
# ============================================
echo "📂 Cleaning empty folders..."
rmdir prompts 2>/dev/null
rmdir logs 2>/dev/null
rmdir assets 2>/dev/null
rmdir questions 2>/dev/null
rmdir schemas 2>/dev/null
rmdir services 2>/dev/null
rmdir tests 2>/dev/null
rmdir workbook 2>/dev/null
rmdir question 2>/dev/null
echo "   ✅ Empty folders removed"

# ============================================
# 8. REMOVE BUILD ARTIFACTS
# ============================================
echo "🏗️  Cleaning build artifacts..."
rm -rf build/ dist/ release/ *.spec
rm -f PostgreSQL_Practice.spec
rm -f icon.png
rm -f icon.ico
rm -f SQL_Workbook_Generator.desktop
echo "   ✅ Build artifacts removed"

# ============================================
# 9. REMOVE PYTHON CACHE
# ============================================
echo "🗑️  Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "   ✅ Python cache removed"

# ============================================
# 10. REMOVE REDUNDANT DOCS
# ============================================
echo "📄 Cleaning redundant docs..."
rm -f README_USER.txt
rm -f Readme.txt
rm -f Commands.txt
rm -f PostgreSQL_Practice.code-workspace
echo "   ✅ Redundant docs removed"

# ============================================
# 11. REMOVE OLD BUILD SCRIPTS
# ============================================
echo "🔧 Cleaning old build scripts..."
rm -f build.sh
rm -f build_executable.sh
rm -f package.sh
rm -f kill_port.sh
rm -f run.sh
echo "   ✅ Old build scripts removed"

# ============================================
# SUMMARY
# ============================================
echo ""
echo "========================================"
echo "✅ Cleanup Complete!"
echo "========================================"
echo ""
echo "📁 Project cleaned and organized!"
echo ""
echo "📋 Remaining structure:"
ls -la | head -20
echo ""
echo "🚀 To start: python portal.py"
echo "========================================"
