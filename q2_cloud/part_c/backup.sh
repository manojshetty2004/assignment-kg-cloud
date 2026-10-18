#!/usr/bin/env bash
set -euo pipefail
umask 077

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/backups"
LOG_FILE="${BACKUP_DIR}/backup.log"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_FILE="${BACKUP_DIR}/postgres-${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"
log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$LOG_FILE"; }

if [[ ! -f "${SCRIPT_DIR}/.env" ]]; then
  log "ERROR: .env not found; copy .env.example to .env and set secrets"
  exit 1
fi

log "Starting PostgreSQL backup"
if docker compose --project-directory "$SCRIPT_DIR" exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip -c > "$BACKUP_FILE"; then
  log "Created $BACKUP_FILE"
else
  rm -f "$BACKUP_FILE"
  log "ERROR: PostgreSQL backup failed"
  exit 1
fi

find "$BACKUP_DIR" -maxdepth 1 -type f -name 'postgres-*.sql.gz' \
  -printf '%T@ %p\n' | sort -nr | awk 'NR > 7 {sub(/^[^ ]+ /, ""); print}' \
  | while IFS= read -r old_backup; do
      rm -f -- "$old_backup"
      log "Removed old backup $old_backup"
    done
log "Backup finished"

# Restore/test: gunzip -c backups/postgres-TIMESTAMP.sql.gz | docker compose exec -T db
#   psql -U "$POSTGRES_USER" -d "$POSTGRES_DB". Prefer restoring into a separate
#   test database first, then check tables and sample rows before trusting it.
# Example daily cron (run from this file's directory): 15 2 * * * /absolute/path/backup.sh
