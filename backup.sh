#!/bin/bash
# Exyra Technologies — MySQL Backup Script
# Usage: ./backup.sh              (manual backup)
#        ./backup.sh auto         (called by start.sh)
#        ./backup.sh restore      (list + restore from backup)

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$ROOT/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="exyra_meet_$TIMESTAMP.sql"
KEEP_LAST=14   # keep last 14 backups

DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_NAME="exyra_meet"
DB_USER="exyra"
DB_PASS="exyra_pass_2024"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'

mkdir -p "$BACKUP_DIR"

# ─── RESTORE MODE ──────────────────────────────────────────────────────────────
if [ "$1" = "restore" ]; then
  echo -e "${YELLOW}Available backups:${NC}"
  ls -1t "$BACKUP_DIR"/*.sql 2>/dev/null | head -20 | nl
  echo ""
  read -p "Enter backup number to restore (or q to quit): " choice
  [ "$choice" = "q" ] && exit 0

  FILE=$(ls -1t "$BACKUP_DIR"/*.sql 2>/dev/null | sed -n "${choice}p")
  if [ -z "$FILE" ]; then
    echo -e "${RED}Invalid selection${NC}"
    exit 1
  fi

  echo -e "${YELLOW}Restoring from: $(basename $FILE)${NC}"
  docker exec -i exyra_mysql mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$FILE"
  echo -e "${GREEN}✓ Restore complete${NC}"
  exit 0
fi

# ─── BACKUP ────────────────────────────────────────────────────────────────────
docker exec exyra_mysql mysqldump \
  -u "$DB_USER" -p"$DB_PASS" \
  --single-transaction \
  --routines \
  --triggers \
  "$DB_NAME" > "$BACKUP_DIR/$FILENAME" 2>/dev/null

if [ $? -eq 0 ] && [ -s "$BACKUP_DIR/$FILENAME" ]; then
  SIZE=$(du -sh "$BACKUP_DIR/$FILENAME" | cut -f1)

  # Remove old backups beyond KEEP_LAST
  ls -1t "$BACKUP_DIR"/*.sql 2>/dev/null | tail -n +$((KEEP_LAST + 1)) | xargs rm -f 2>/dev/null

  TOTAL=$(ls "$BACKUP_DIR"/*.sql 2>/dev/null | wc -l | tr -d ' ')

  if [ "$1" != "silent" ]; then
    echo -e "${GREEN}✓ Backup saved:${NC} backups/$FILENAME (${SIZE}) — ${TOTAL} backups kept"
  fi

  # Write latest backup path for reference
  echo "$BACKUP_DIR/$FILENAME" > /tmp/exyra_last_backup
  exit 0
else
  rm -f "$BACKUP_DIR/$FILENAME"
  if [ "$1" != "silent" ]; then
    echo -e "${RED}✗ Backup failed — is MySQL running? (docker ps | grep mysql)${NC}"
  fi
  exit 1
fi
