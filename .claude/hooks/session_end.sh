#!/bin/bash
# autolab SessionEnd hook — log session duration
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Find last SESSION_START timestamp
LAST_START=$(grep "SESSION_START" "$PROJECT_DIR/lab/journal.md" 2>/dev/null | tail -1 | grep -oP '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' || true)

if [ -n "$LAST_START" ]; then
    START_EPOCH=$(date -d "$LAST_START" +%s 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S" "$LAST_START" +%s 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    if [ "$START_EPOCH" -gt 0 ]; then
        DURATION=$(( (NOW_EPOCH - START_EPOCH) / 60 ))
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] SESSION_END | duration=${DURATION}m" >> "$PROJECT_DIR/lab/journal.md"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] SESSION_END" >> "$PROJECT_DIR/lab/journal.md"
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SESSION_END" >> "$PROJECT_DIR/lab/journal.md"
fi
