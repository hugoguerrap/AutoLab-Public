#!/bin/bash
# autolab SessionStart hook
# Injects lab state into new sessions: backlog summary, recent journal, scoreboard, active worktrees
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CONTEXT=""

# Backlog summary
if [ -f "$PROJECT_DIR/backlog/BACKLOG.md" ]; then
    TOTAL=$(grep -c "^|" "$PROJECT_DIR/backlog/BACKLOG.md" 2>/dev/null || echo 0)
    TOTAL=$((TOTAL > 0 ? TOTAL - 1 : 0))  # subtract header row
    READY=$(grep -c "| ready |" "$PROJECT_DIR/backlog/BACKLOG.md" 2>/dev/null || echo 0)
    IN_PROGRESS=$(grep -c "| in-progress |" "$PROJECT_DIR/backlog/BACKLOG.md" 2>/dev/null || echo 0)
    DONE=$(grep -c "| done |" "$PROJECT_DIR/backlog/BACKLOG.md" 2>/dev/null || echo 0)
    CONTEXT="## Lab Backlog\n$READY ready | $IN_PROGRESS in-progress | $DONE done | $TOTAL total"

    # Show in-progress ideas
    IN_PROG_ITEMS=$(grep "| in-progress |" "$PROJECT_DIR/backlog/BACKLOG.md" 2>/dev/null || true)
    if [ -n "$IN_PROG_ITEMS" ]; then
        CONTEXT="$CONTEXT\n\n### Currently Active:\n$IN_PROG_ITEMS"
    fi
fi

# Recent journal (last 15 entries)
if [ -f "$PROJECT_DIR/lab/journal.md" ]; then
    JOURNAL=$(grep "^\[" "$PROJECT_DIR/lab/journal.md" 2>/dev/null | tail -15 || true)
    if [ -n "$JOURNAL" ]; then
        CONTEXT="$CONTEXT\n\n## Recent Lab Activity\n$JOURNAL"
    fi
fi

# Scoreboard
if [ -f "$PROJECT_DIR/lab/scoreboard.md" ]; then
    SCORES=$(cat "$PROJECT_DIR/lab/scoreboard.md" 2>/dev/null || true)
    if [ -n "$SCORES" ] && [ "$(echo "$SCORES" | wc -l)" -gt 2 ]; then
        CONTEXT="$CONTEXT\n\n## Scoreboard\n$SCORES"
    fi
fi

# Active worktrees (exclude main)
WORKTREES=$(git -C "$PROJECT_DIR" worktree list 2>/dev/null | grep -v "main\|master" || true)
if [ -n "$WORKTREES" ]; then
    CONTEXT="$CONTEXT\n\n## Active Worktrees\n$WORKTREES"
fi

# Metrics summary (last 5 entries)
if [ -f "$PROJECT_DIR/lab/metrics.tsv" ]; then
    METRICS=$(tail -5 "$PROJECT_DIR/lab/metrics.tsv" 2>/dev/null || true)
    if [ -n "$METRICS" ]; then
        CONTEXT="$CONTEXT\n\n## Recent Metrics\n$METRICS"
    fi
fi

# Log session start
echo "[$(date '+%Y-%m-%d %H:%M:%S')] SESSION_START" >> "$PROJECT_DIR/lab/journal.md"

# Output for Claude Code
if command -v jq &> /dev/null; then
    jq -n --arg ctx "$CONTEXT" '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$ctx}}'
else
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\"Lab state loaded. Check backlog/BACKLOG.md and lab/journal.md for details.\"}}"
fi
