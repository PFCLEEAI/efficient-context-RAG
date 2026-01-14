# Efficient Context RAG

> A comprehensive system for maintaining efficient AI context windows through progressive loading, semantic RAG, and MCP integration.

```
   _____ _____ _____ _____    _____         _           _
  | ____|  ___|  ___|_   _|  / ____|       | |         | |
  |  _| | |_  | |_    | |   | |     ___  __| | ___  ___| |_
  | |___|  _| |  _|   | |   | |    / _ \/ _` |/ _ \/ __| __|
  |_____|_|   |_|     |_|   | |___| (_) | (_| |  __/ (__| |_
                             \_____\___/ \__,_|\___|\___|\__|
                                     RAG System
```

## The Problem

AI assistants have limited context windows (200k tokens for Claude). Long conversations quickly fill this space with:
- Redundant conversation history
- Full file contents repeatedly read
- Unstructured information retrieval

**Result**: AI performance degrades, forgets context, makes repeated mistakes.

## The Solution

This system maintains **optimal context efficiency** through:

1. **Progressive Loading** - Load only what's needed, when needed
2. **Semantic RAG via MCP** - Cross-session memory with intelligent retrieval
3. **Structured Templates** - Consistent, token-efficient context storage
4. **Lazy Calling** - Call external systems only when truly necessary

## Quick Start

### 1. Install the System

```bash
# Clone this repo
git clone https://github.com/YOUR_USERNAME/efficient-context-RAG.git

# Copy to your Claude config
cp -r efficient-context-RAG/claude-config/* ~/.claude/
chmod +x ~/.claude/scripts/*.sh
```

### 2. Initialize a Project

```bash
# In any project directory
~/.claude/scripts/init-project.sh . "MyProject"
```

### 3. Add CLAUDE.md to Your Global Config

```bash
# Copy the universal agent system config
cp efficient-context-RAG/claude-config/CLAUDE.md ~/.claude/CLAUDE.md
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Context Efficiency System                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Project    │    │     MCP      │    │    Skills    │  │
│  │   .claude/   │    │   Memory     │    │   System     │  │
│  │              │    │              │    │              │  │
│  │ status.md    │◄──►│ Entities     │◄──►│ /pm          │  │
│  │ context.md   │    │ Relations    │    │ /ralph-loop  │  │
│  │ todo-list.md │    │ Observations │    │ Custom...    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         └───────────────────┴───────────────────┘           │
│                            │                                 │
│                    ┌───────▼───────┐                        │
│                    │  Progressive  │                        │
│                    │    Loader     │                        │
│                    │               │                        │
│                    │ Load on demand│                        │
│                    │ Compress old  │                        │
│                    │ Lazy retrieve │                        │
│                    └───────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Core Concepts

### 1. Progressive Loading

```
Load Order (by need):
├── 1. status.md + todo-list.md  → ALWAYS (current state)
├── 2. context.md                → If architecture needed
├── 3. contracts/                → If API specs needed
└── 4. MCP Memory                → If cross-session needed
```

**Never load everything at once.** Only load what the current task requires.

### 2. Project Context Structure

Every project gets a `.claude/` directory:

```
{project}/.claude/
├── status.md        # Current state (always read first)
├── progress.md      # Milestones & completion tracking
├── todo-list.md     # Prioritized task list
├── context.md       # Architecture & decisions (RAG)
├── improvements.md  # Lessons learned & tech debt
├── contracts/       # API specs between components
│   ├── api.md
│   └── types.md
├── handoffs/        # Agent-to-agent communication
└── logs/            # Activity tracking
```

### 3. MCP Semantic RAG

Use MCP Memory for cross-session persistence:

```bash
# Entity naming convention
project:{name}              # Main project entity
project:{name}:arch         # Architecture decisions
project:{name}:lesson:{id}  # Lessons learned
project:{name}:decision:{id}# Key decisions

# Search for context
mcp-cli call memory/search_nodes '{"query": "project:MyApp"}'

# Save a lesson
mcp-cli call memory/create_entities '{"entities": [{"name": "project:MyApp:lesson:001", "entityType": "lesson", "observations": ["Always validate input at API boundary"]}]}'

# Add to existing entity
mcp-cli call memory/add_observations '{"observations": [{"entityName": "project:MyApp", "contents": ["Added auth module 2024-01-15"]}]}'
```

### 4. Lazy Calling (Critical!)

```
CALL MCP/External WHEN:        DON'T CALL WHEN:
├── Project start              ├── Simple file edits
├── Need past solutions        ├── Context already in .claude/
├── Architecture decisions     └── No retrieval benefit
└── Cross-session context
```

**Every MCP call costs tokens.** Only call when the benefit exceeds the cost.

## Templates

### status.md - Current State

```markdown
# Project Status

## Meta
- **Project**: MyApp
- **Goal Score**: 90/100
- **Current Score**: 75/100
- **Iteration**: 3/5

## Kanban
| Todo | In Progress | Done |
|------|-------------|------|
| Auth | API | Setup |

## Blockers
| ID | Domain | Severity | Status |
|----|--------|----------|--------|
| B1 | Auth | High | Active |
```

### context.md - RAG Context

```markdown
# Project Context (RAG)

## Quick Context
**What**: E-commerce platform
**Why**: Replace legacy system
**Tech Stack**: Next.js, Supabase, Stripe

## Key Files
| File | Purpose |
|------|---------|
| src/lib/auth.ts | Authentication |
| src/api/orders.ts | Order processing |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2024-01-10 | Use Supabase | Real-time + Auth built-in |
```

## Session Protocols

### Starting a Session

```
1. Read status.md + todo-list.md
2. Check for blockers
3. MCP search if cross-session context needed
4. Begin work
```

### Ending a Session

```
1. Update status.md with current state
2. Log completed work in progress.md
3. Save reusable lessons to MCP
4. Update todo-list.md priorities
```

### Context Getting Full (>70%)

```
1. Compress conversation into context.md
2. Save key decisions to MCP
3. Update status.md with summary
4. Clear conversation, continue with context
```

## Model Selection Strategy

```
haiku   → File operations, searches, simple tasks
sonnet  → Complex logic, multi-step reasoning
opus    → Architecture decisions, difficult problems
```

**Escalate only when needed.** Start with haiku, move up if task fails.

## Best Practices

### DO

- Read status.md before any work
- Update todo-list.md as you progress
- Compress context at 70% window usage
- Use MCP for cross-session memory
- Keep templates minimal and focused

### DON'T

- Load all context at once
- Call MCP for every small task
- Store conversation history verbatim
- Ignore the progressive loading order
- Let context window exceed 80%

## Integration Examples

### With Claude Code

Add to `~/.claude/CLAUDE.md`:

```markdown
## AUTO-INIT ON PROJECT OPEN

ON PROJECT OPEN:
├── 1. Detect root (package.json, .git, etc.)
├── 2. .claude/ exists?
│     ├── NO  → Run: ~/.claude/scripts/init-project.sh
│     └── YES → Load: status.md + todo-list.md
├── 3. MCP search: memory/search_nodes '{"query": "project:{name}"}'
└── 4. Ready
```

### With Parallel Agents

```markdown
## /pm "[task]" - Parallel Project Manager

PM ──┬── Task(Frontend, haiku, bg=true)
     ├── Task(Backend, sonnet, bg=true)
     └── All spawned SIMULTANEOUSLY

Communication via handoffs/*.md
```

## Directory Structure

```
efficient-context-RAG/
├── README.md                    # This file
├── claude-config/
│   ├── CLAUDE.md               # Universal agent config
│   ├── scripts/
│   │   └── init-project.sh     # Project initializer
│   └── templates/
│       └── workspace/
│           ├── status.md
│           ├── progress.md
│           ├── todo-list.md
│           ├── context.md
│           ├── improvements.md
│           ├── contracts/
│           │   ├── api.md
│           │   └── types.md
│           └── logs/
│               └── agent-log.md
├── examples/
│   ├── mcp-commands.md         # MCP usage examples
│   └── session-workflow.md     # Session protocols
└── docs/
    ├── progressive-loading.md
    ├── mcp-integration.md
    └── troubleshooting.md
```

## License

MIT License - Use freely, contribute back!

## Contributing

1. Fork the repo
2. Create a feature branch
3. Add your improvements
4. Submit a PR

---

**Maintain 70% context. Stay efficient. Ship faster.**
