# Session Workflow Guide

## Overview

This guide documents the optimal workflow for maintaining efficient context across AI sessions.

## Session Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Lifecycle                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  START SESSION                                               │
│  │                                                          │
│  ├── 1. Load status.md + todo-list.md                      │
│  ├── 2. Check for blockers                                 │
│  ├── 3. MCP search if cross-session context needed         │
│  └── 4. Begin work                                         │
│                                                              │
│  DURING SESSION                                              │
│  │                                                          │
│  ├── Update status.md as work progresses                   │
│  ├── Monitor context usage (target: <70%)                  │
│  ├── Compress if hitting 70% threshold                     │
│  └── Log decisions in context.md                           │
│                                                              │
│  END SESSION                                                 │
│  │                                                          │
│  ├── 1. Update status.md with final state                  │
│  ├── 2. Log completed work in progress.md                  │
│  ├── 3. Save reusable lessons to MCP                       │
│  └── 4. Update todo-list.md priorities                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Starting a Session

### Step 1: Load Core Context

```bash
# Always read these first
cat .claude/status.md
cat .claude/todo-list.md
```

The AI should automatically do this on project open.

### Step 2: Check Blockers

Look at the Blockers section in status.md:

```markdown
## Blockers
| ID | Domain | Severity | Status |
|----|--------|----------|--------|
| B1 | API | High | Active |
```

If there are active blockers, address them first.

### Step 3: Load Additional Context (If Needed)

```
Need architecture info?    → Load context.md
Need API specs?            → Load contracts/
Need cross-session memory? → MCP search
```

### Step 4: Begin Work

Start with the highest priority task from todo-list.md.

## During a Session

### Monitor Context Usage

Run `/context` periodically to check usage:

```
Context Usage
Messages: 112.2k tokens (56.1%)
Free space: 20k (10.2%)
```

### Context Compression Triggers

**Compress when:**
- Messages exceed 70% of context
- Conversation becomes repetitive
- Switching to unrelated task

### How to Compress

1. **Summarize current state to context.md:**

```markdown
## Session Recovery
**Last Working On**: Authentication flow refactor
**Next Steps**:
- Complete JWT refresh logic
- Add rate limiting
**Blockers**: None
```

2. **Update status.md:**

```markdown
## Event Log
| Time | Event | Details |
|------|-------|---------|
| 14:30 | COMPRESS | Auth module 80% complete |
```

3. **Save key decisions to MCP (if reusable):**

```bash
mcp-cli call memory/create_entities '{"entities": [{
  "name": "project:MyApp:decision:003",
  "entityType": "decision",
  "observations": [
    "Decision: Use short-lived access tokens (15min) + refresh tokens (7d)",
    "Rationale: Better security, manageable UX"
  ]
}]}'
```

4. **Clear conversation and continue with context**

## Ending a Session

### Step 1: Update status.md

```markdown
## Kanban
| Todo | In Progress | Done |
|------|-------------|------|
| Rate limiting | - | Auth module |

## Event Log
| Time | Event | Details |
|------|-------|---------|
| 17:00 | SESSION_END | Auth complete, starting payments next |
```

### Step 2: Log Progress

Update progress.md with completed work:

```markdown
### 2024-01-15
**Focus**: Authentication module
**Completed**:
- JWT implementation
- Refresh token logic
- Protected route middleware

**Next**:
- Rate limiting
- Payment integration
```

### Step 3: Save Reusable Lessons

If you learned something applicable to future projects:

```bash
mcp-cli call memory/create_entities '{"entities": [{
  "name": "lesson:jwt-refresh-pattern",
  "entityType": "lesson",
  "observations": [
    "Pattern: Short access tokens (15min) + long refresh tokens (7d)",
    "Implementation: Store refresh tokens in httpOnly cookies",
    "Security: Rotate refresh tokens on each use"
  ]
}]}'
```

### Step 4: Prioritize Tomorrow's Tasks

Update todo-list.md priorities based on current state.

## Context Recovery After Auto-Compact

When Claude auto-compacts, it creates a summary. To recover:

1. **Read the summary provided**
2. **Load status.md for current state**
3. **Load context.md for architecture**
4. **MCP search if needed for historical context**

## Parallel Work Sessions

When using /pm with parallel agents:

### Agent Communication

Use `handoffs/*.md` for agent-to-agent communication:

```markdown
# handoffs/frontend-to-backend.md

## From: @frontend
## To: @backend
## Status: PENDING

### Request
Need the `/api/users` endpoint to return `lastLoginAt` field.

### Context
Implementing user profile page, need to show last login.

### Priority
P1 - Blocking profile page completion
```

### Status Sync

All agents update the shared status.md:

```markdown
## Agent Status
| Agent | Wave | Status | Output |
|-------|------|--------|--------|
| @frontend | 1 | Working | Profile page 60% |
| @backend | 1 | Blocked | Waiting on DB schema |
| @testing | 2 | Pending | - |
```

## Troubleshooting

### Context Growing Too Fast

- Check for repeated file reads
- Use SERENA symbolic tools instead of full file reads
- Compress more frequently
- Archive completed tasks from todo-list.md

### Lost Context After Restart

- status.md should have current state
- context.md has architecture
- MCP has cross-session lessons
- If truly lost, reconstruct from git history + MCP

### MCP Not Finding Entities

- Check entity naming convention
- Use broader search terms
- Verify entity was actually saved (check for errors)
