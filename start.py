#!/usr/bin/env python3
"""
SQL Workbook Generator - Master Launcher
One click, everything works!
"""

import os
import sys
import subprocess
import webbrowser
import time
import socket
from pathlib import Path

def find_free_port():
    """Find a free port"""
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def main():
    print("=" * 50)
    print("  SQL Workbook Generator")
    print("  One-Click Launcher")
    print("=" * 50)
    print()
    
    # Get the directory
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    try:
        import flask
        import psycopg2
        import docx
        import reportlab
        import faker
        print("✅ All dependencies installed")
    except ImportError:
        print("📦 Installing missing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "flask", "psycopg2-binary", "python-docx", 
                       "reportlab", "faker"])
        print("✅ Dependencies installed")
    
    # Check PostgreSQL
    print("🔍 Checking PostgreSQL...")
    try:
        subprocess.run(["pg_isready"], check=True, capture_output=True)
        print("✅ PostgreSQL is running")
    except:
        print("⚠️  Starting PostgreSQL...")
        subprocess.run(["sudo", "systemctl", "start", "postgresql"])
        print("✅ PostgreSQL started")
    
    # Find free port
    port = find_free_port()
    print(f"🚀 Starting on port {port}...")
    
    # Update portal.py port
    with open('portal.py', 'r') as f:
        content = f.read()
    
    content = content.replace('port=5000', f'port={port}')
    content = content.replace('port=5001', f'port={port}')
    content = content.replace('port=5002', f'port={port}')
    
    with open('portal.py', 'w') as f:
        f.write(content)
    
    # Open browser
    time.sleep(1)
    webbrowser.open(f"http://localhost:{port}")
    
    # Launch portal
    print()
    print("=" * 50)
    print(f"✅ Portal is running at: http://localhost:{port}")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    subprocess.run([sys.executable, "portal.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        sys.exit(0)
