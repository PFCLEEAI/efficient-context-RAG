# Automatic Context Compression

> Keep your context at 20-40% free space automatically.

---

## The Problem

```
WITHOUT AUTO-COMPRESSION:
┌──────────────────────────────────────────────────────────┐
│                                                           │
│  Context fills → Autocompact triggers → Data LOST         │
│                                                           │
│  "Fixed bug in auth.ts:47 by changing..."                │
│                    ↓                                      │
│  "Fixed authentication bug"  ← Details gone forever      │
│                                                           │
└──────────────────────────────────────────────────────────┘

WITH AUTO-COMPRESSION (This System):
┌──────────────────────────────────────────────────────────┐
│                                                           │
│  Context fills → AUTO-ARCHIVE to RAG → THEN compact      │
│                                                           │
│  "Fixed bug in auth.ts:47 by changing..."                │
│                    ↓                                      │
│  Saved to MCP + .claude/messages.md ← Retrievable!       │
│                    ↓                                      │
│  Compact proceeds, details preserved in RAG              │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Setup

### 1. Install the Script

```bash
# Copy to your Claude scripts
cp claude-config/scripts/auto-archive.py ~/.claude/scripts/

# Make executable
chmod +x ~/.claude/scripts/auto-archive.py
```

### 2. Check Context Level

```bash
python ~/.claude/scripts/auto-archive.py check
```

Output:
```
╔══════════════════════════════════════════════════════════╗
║                  Context Usage Check                      ║
╠══════════════════════════════════════════════════════════╣
║                                                           ║
║  [████████████░░░░░░░░] 58%                              ║
║                                                           ║
║  Estimated tokens: 116,000                                ║
║  Free space: 42%                                          ║
║  Threshold: 60%                                           ║
║                                                           ║
║  Status: 🟡 Monitor                                       ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
```

### 3. Archive When Needed

```bash
# Archive current session
python ~/.claude/scripts/auto-archive.py archive

# Or auto-archive only if threshold exceeded
python ~/.claude/scripts/auto-archive.py auto
```

---

## How It Works

### Archive Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Auto-Archive Flow                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. CHECK: Read session file, estimate token usage      │
│                         ↓                                │
│  2. EXTRACT: Pull decisions, lessons, state from chat   │
│                         ↓                                │
│  3. SAVE: Archive to MCP Memory + local files           │
│     ├── MCP: session:{project}:{timestamp}              │
│     ├── .claude/archives/session-{timestamp}.md         │
│     └── .claude/messages.md (append)                    │
│                         ↓                                │
│  4. COMPACT: User runs /compact with confidence         │
│                         ↓                                │
│  5. RETRIEVE: Context available via MCP search          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### What Gets Archived

| Content | How Detected | Where Saved |
|---------|--------------|-------------|
| Decisions | "decided", "chose", "decision:" | MCP + files |
| Lessons | "learned", "lesson:", "realized" | MCP + files |
| Tasks completed | "completed", "done", "finished" | Files |
| Current state | Last assistant message | Both |

---

## Usage Options

### Manual Check + Archive

```bash
# Check current level
python ~/.claude/scripts/auto-archive.py check

# If high, archive
python ~/.claude/scripts/auto-archive.py archive

# Then in Claude Code
/compact
```

### Automatic (Threshold-Based)

```bash
# Only archives if > 60%
python ~/.claude/scripts/auto-archive.py auto
```

### Preview Before Saving

```bash
# See what would be archived without saving
python ~/.claude/scripts/auto-archive.py archive --dry
```

---

## Setting Up Hooks (Advanced)

### Option 1: Bash Alias

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Check context before starting work
alias claude-check='python ~/.claude/scripts/auto-archive.py check'

# Quick archive
alias claude-archive='python ~/.claude/scripts/auto-archive.py archive'

# Auto-archive if needed
alias claude-auto='python ~/.claude/scripts/auto-archive.py auto'
```

Usage:
```bash
claude-check    # Before starting
claude-auto     # When context feels high
claude-archive  # Before /compact
```

### Option 2: Claude Code Hook (settings.json)

Add to your Claude Code settings:

```json
{
  "hooks": {
    "preCompact": {
      "command": "python ~/.claude/scripts/auto-archive.py archive",
      "description": "Auto-archive before compact"
    }
  }
}
```

*Note: Check Claude Code docs for current hook syntax.*

### Option 3: Periodic Reminder

Add a cron job to remind you:

```bash
# Check every 30 minutes during work hours
*/30 9-18 * * 1-5 python ~/.claude/scripts/auto-archive.py auto >> ~/.claude/archive.log 2>&1
```

---

## Retrieving Archived Context

### From MCP Memory

```bash
# Search for archived sessions
mcp-cli call memory/search_nodes '{"query": "session:MyProject"}'

# Get specific session
mcp-cli call memory/open_nodes '{"names": ["session:MyProject:20240115-1430"]}'
```

### From Local Files

```bash
# View all archives
ls -la .claude/archives/

# Read compressed messages
cat .claude/messages.md

# Search archives
grep -r "authentication" .claude/archives/
```

### In Claude Code

Just ask:
- "What did we decide about authentication?"
- "Search MCP for lessons about auth"
- "Read .claude/messages.md for previous context"

---

## Configuration

Edit the script to change thresholds:

```python
# In auto-archive.py

CONTEXT_THRESHOLD = 60  # Archive when context exceeds this %
TARGET_FREE_SPACE = 30  # Target free space after archive (%)
```

### Recommended Settings

| Work Style | Threshold | Target Free |
|------------|-----------|-------------|
| Conservative | 50% | 40% |
| Balanced | 60% | 30% |
| Aggressive | 70% | 20% |

---

## Workflow Integration

### Daily Workflow with Auto-Archive

```
START SESSION:
├── claude-check                    # See current level
├── Load .claude/messages.md if resuming
└── MCP search for relevant context

DURING WORK:
├── Monitor context (target: < 60%)
├── Run claude-auto periodically
└── Archive hits to messages.md

BEFORE COMPACT:
├── claude-archive                  # Save everything
├── /compact                        # Clear conversation
└── Continue with archived context

END SESSION:
├── claude-archive                  # Final save
└── Update status.md
```

### The 20-40% Free Space Rule

```
┌─────────────────────────────────────────────────────────┐
│                 Optimal Context Usage                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  0%        20%        40%        60%        80%    100% │
│  ├─────────┼──────────┼──────────┼──────────┼─────────┤ │
│  │         │          │          │          │         │ │
│  │  IDEAL  │  IDEAL   │   OK     │ ARCHIVE  │ DANGER  │ │
│  │  FREE   │  FREE    │          │   NOW    │         │ │
│  │         │          │          │          │         │ │
│  └─────────┴──────────┴──────────┴──────────┴─────────┘ │
│                                                          │
│  Target: Keep free space between 20-40%                 │
│  Action: Archive when free space drops below 40%        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### "Could not find project directory"

The script looks for your Claude session files. Make sure you're in a project directory that has an active Claude Code session.

### "MCP save failed"

MCP Memory server might not be running. The script will still save to local files.

```bash
# Check MCP status
mcp-cli servers

# Files are saved regardless
ls .claude/archives/
```

### "No content extracted"

The extraction looks for specific patterns. If your conversation doesn't have explicit "decided", "learned" markers, add them:

- "Decision: We'll use PostgreSQL for..."
- "Lesson learned: Always validate..."

---

## Files Created

| File | Purpose | Retrieval |
|------|---------|-----------|
| `.claude/archives/session-*.md` | Full session snapshots | `cat` or search |
| `.claude/messages.md` | Compressed rolling history | Load into context |
| MCP `session:{project}:*` | Cross-session memory | `mcp-cli search` |

---

**Archive early. Archive often. Never lose context.**
