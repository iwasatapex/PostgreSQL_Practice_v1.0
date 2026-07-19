#!/bin/bash
# ============================================================
# PostgreSQL Practice - Simple Backup
# ============================================================

echo "============================================================"
echo "  📦 PostgreSQL Practice - Backup"
echo "============================================================"
echo ""

# Set variables
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="PostgreSQL_Practice_Backup_${TIMESTAMP}"
BACKUP_ROOT="/run/media/amateur/Generations/Backups"
PROJECT_DIR="/run/media/amateur/Generations/PostgreSQL_Practice"

# Create backup directory
mkdir -p "$BACKUP_ROOT"
BACKUP_DIR="${BACKUP_ROOT}/${BACKUP_NAME}"
mkdir -p "$BACKUP_DIR"

echo "📁 Backup directory: $BACKUP_DIR"
echo ""

# Copy files (excluding large/unnecessary folders)
echo "📄 Copying files..."
rsync -av --progress "$PROJECT_DIR/" "$BACKUP_DIR/" \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='output' \
    --exclude='uploads' \
    --exclude='sessions' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='backup.sh' \
    --exclude='Backups' \
    2>&1 | grep -E "sent|received|total|files"

# Get backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "Unknown")

# Create ZIP
echo ""
echo "📦 Creating ZIP archive..."
cd "$BACKUP_ROOT"
zip -r "${BACKUP_NAME}.zip" "$BACKUP_NAME/" > /dev/null 2>&1
ZIP_SIZE=$(du -sh "${BACKUP_NAME}.zip" 2>/dev/null | cut -f1 || echo "Unknown")

echo ""
echo "============================================================"
echo "✅ Backup Complete!"
echo "============================================================"
echo ""
echo "📁 Backup folder: $BACKUP_DIR"
echo "📊 Folder size: $BACKUP_SIZE"
echo "📦 ZIP file: $BACKUP_ROOT/${BACKUP_NAME}.zip"
echo "📊 ZIP size: $ZIP_SIZE"
echo ""
echo "============================================================"
