#!/usr/bin/env python3
"""
PostgreSQL Practice - Python Backup Script
"""

import os
import shutil
import zipfile
import datetime
from pathlib import Path

PROJECT_DIR = "/run/media/amateur/Generations/PostgreSQL_Practice"
BACKUP_ROOT = "/run/media/amateur/Generations/Backups"
EXCLUDE_DIRS = ['.venv', '__pycache__', 'output', 'uploads', 'sessions', '.git']
EXCLUDE_EXTENSIONS = ['.pyc', '.pyo', '.log', '.tmp', '.docx', '.pdf', '.zip']

def get_backup_name():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"PostgreSQL_Practice_Backup_{timestamp}"

def should_exclude(path):
    name = path.name
    for exclude in EXCLUDE_DIRS:
        if exclude in str(path):
            return True
    for ext in EXCLUDE_EXTENSIONS:
        if name.endswith(ext):
            return True
    return False

def get_size(path):
    if path.is_file():
        return path.stat().st_size
    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            total += item.stat().st_size
    return total

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def create_backup():
    print("=" * 60)
    print("  📦 PostgreSQL Practice - Backup")
    print("=" * 60)
    print()
    
    backup_name = get_backup_name()
    backup_dir = Path(BACKUP_ROOT) / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Backup: {backup_name}")
    print(f"📂 Location: {backup_dir}")
    print()
    print("📄 Copying files...")
    
    copied = 0
    total = 0
    
    for root, dirs, files in os.walk(PROJECT_DIR):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            total += 1
            file_path = root_path / file
            if should_exclude(file_path):
                continue
            
            rel_path = file_path.relative_to(PROJECT_DIR)
            dest_path = backup_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.copy2(file_path, dest_path)
                copied += 1
            except Exception as e:
                print(f"  ⚠️  Error: {file_path.name}")
    
    print(f"  ✅ Copied {copied} files")
    print()
    
    print("📦 Creating ZIP...")
    zip_path = Path(BACKUP_ROOT) / f"{backup_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(backup_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(backup_dir)
                zipf.write(file_path, arcname)
    
    backup_size = format_size(get_size(backup_dir))
    zip_size = format_size(get_size(zip_path))
    
    print()
    print("=" * 60)
    print("✅ Backup Complete!")
    print("=" * 60)
    print()
    print(f"📁 Backup: {backup_dir}")
    print(f"📊 Size: {backup_size}")
    print(f"📦 ZIP: {zip_path}")
    print(f"📊 ZIP Size: {zip_size}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    create_backup()
