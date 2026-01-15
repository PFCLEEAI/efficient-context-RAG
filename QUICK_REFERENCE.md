# Quick Reference Card

> Print this or pin it. Your daily cheat sheet for efficient AI context.

---

## Context Targets

```
🟢 0-50%   Perfect - Keep working
🟡 50-70%  Good - Monitor usage
🟠 70-80%  COMPRESS NOW
🔴 80%+    Degraded - Should have compressed earlier
```

---

## Session Start Checklist

```
□ Read .claude/status.md
□ Read .claude/todo-list.md
□ MCP search (if resuming): mcp-cli call memory/search_nodes '{"query": "project:NAME"}'
□ Check blockers in status.md
□ Start with highest priority task
```

---

## Session End Checklist

```
□ Update .claude/status.md with current state
□ Update .claude/todo-list.md priorities
□ Save lessons to MCP (if reusable)
□ Log progress in .claude/progress.md
```

---

## Compression Checklist (at 70%)

```
□ Summarize current work → status.md
□ Save architecture decisions → context.md
□ Save reusable lessons → MCP Memory
□ Clear/compact conversation
□ Continue with fresh context
```

---

## MCP Commands

```bash
# Search
mcp-cli call memory/search_nodes '{"query": "project:NAME"}'

# Save lesson
mcp-cli call memory/create_entities '{"entities": [{
  "name": "project:NAME:lesson:001",
  "entityType": "lesson",
  "observations": ["What you learned"]
}]}'

# Add to existing
mcp-cli call memory/add_observations '{"observations": [{
  "entityName": "project:NAME",
  "contents": ["New info"]
}]}'
```

---

## Entity Naming

```
project:{name}              → Main project
project:{name}:arch         → Architecture
project:{name}:lesson:{id}  → Lessons
project:{name}:decision:{id}→ Decisions
```

---

## Progressive Loading Order

```
1. ALWAYS:    status.md + todo-list.md
2. ON DEMAND: context.md (architecture)
3. ON DEMAND: contracts/ (API specs)
4. ON DEMAND: MCP Memory (cross-session)
```

---

## Model Selection

```
haiku  → Simple tasks, searches, file ops
sonnet → Complex logic, multi-step
opus   → Architecture, difficult problems
```

---

## File Purposes

| File | Purpose | When to Update |
|------|---------|----------------|
| `status.md` | Current state | Every session |
| `todo-list.md` | Tasks | As you work |
| `context.md` | Architecture | On decisions |
| `progress.md` | History | End of session |
| `improvements.md` | Lessons | When learned |

---

## DO / DON'T

### DO
- ✅ Read status.md first
- ✅ Compress at 70%
- ✅ Use MCP for cross-session
- ✅ Use SERENA for code (not cat)
- ✅ Update status.md before ending

### DON'T
- ❌ Load all files at once
- ❌ Re-read same files repeatedly
- ❌ Let context exceed 80%
- ❌ Store secrets in MCP
- ❌ Skip status.md update

---

## Emergency Recovery

**Lost context after auto-compact?**
```
1. cat .claude/status.md
2. cat .claude/context.md
3. mcp-cli call memory/search_nodes '{"query": "project:NAME"}'
4. Reconstruct from these sources
```

**Context filling too fast?**
```
1. Stop reading full files (use SERENA)
2. Compress immediately
3. Check for repeated file reads
4. Remove verbose conversation
```

---

## Initialize New Project

```bash
~/.claude/scripts/init-project.sh . "ProjectName"
```

---

## Daily Workflow

```
┌─────────────────────────────────────────┐
│  START                                  │
│  ├─ Load status.md + todo-list.md      │
│  ├─ MCP search if needed               │
│  └─ Begin highest priority task        │
│                                         │
│  WORK (stay under 70%)                  │
│  ├─ Update todos as you go             │
│  ├─ Monitor context with /context      │
│  └─ Compress when hitting 70%          │
│                                         │
│  END                                    │
│  ├─ Update status.md                   │
│  ├─ Save lessons to MCP                │
│  └─ Prioritize tomorrow's tasks        │
└─────────────────────────────────────────┘
```

---

**Target: 70% max context. Compress early. Ship faster.**
