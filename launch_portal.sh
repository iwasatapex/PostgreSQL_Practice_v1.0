#!/bin/bash
# ============================================
# SQL Workbook Generator - One Click Launcher
# ============================================

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   SQL Workbook Generator Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}📦 Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Check if dependencies are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
pip install --quiet flask psycopg2-binary python-docx reportlab faker
echo -e "${GREEN}✅ Dependencies ready${NC}"

# Check if PostgreSQL is running
echo -e "${BLUE}🔍 Checking PostgreSQL...${NC}"
if ! pg_isready -q; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not running. Starting...${NC}"
    sudo systemctl start postgresql
    echo -e "${GREEN}✅ PostgreSQL started${NC}"
fi

# Check if port is available
PORT=5002
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Port $PORT is busy. Trying port 5003...${NC}"
    PORT=5003
    # Update portal.py to use the new port
    sed -i "s/port=500[0-9]/port=$PORT/g" portal.py
fi

echo -e "${GREEN}🚀 Launching portal on port $PORT...${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Portal is running!${NC}"
echo -e "${BLUE}🌐 Open your browser and go to:${NC}"
echo -e "${GREEN}   http://localhost:$PORT${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Launch the portal
python portal.py
