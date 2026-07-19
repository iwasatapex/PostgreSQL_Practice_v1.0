#!/bin/bash
# One-time setup for normal users

echo "========================================"
echo "   SQL Workbook Generator Setup"
echo "========================================"
echo ""

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --user flask psycopg2-binary python-docx reportlab faker

# Install PostgreSQL if not present
if ! command -v psql &> /dev/null; then
    echo "📦 Installing PostgreSQL..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
    sudo systemctl start postgresql
    echo "✅ PostgreSQL installed"
fi

# Create desktop shortcut
if [ -d "$HOME/Desktop" ]; then
    cp SQL_Workbook_Generator.desktop "$HOME/Desktop/" 2>/dev/null || echo "Desktop shortcut created"
    chmod +x "$HOME/Desktop/SQL_Workbook_Generator.desktop" 2>/dev/null
    echo "✅ Desktop shortcut created"
fi

echo ""
echo "✅ Setup complete!"
echo "Double-click launch_portal.sh to start"
echo ""
