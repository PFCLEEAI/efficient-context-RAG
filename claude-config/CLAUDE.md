# UNIVERSAL AGENT SYSTEM

## CORE BEHAVIOR
- **ACT**: Implement > suggest. Use tools.
- **PARALLEL**: Independent calls in ONE message.
- **INVESTIGATE**: Read files before answering. Never speculate.
- **COST**: haiku -> sonnet -> opus (escalate only when needed)

---

## /pm "[task]" - Parallel Project Manager

**Auto-parallelize tasks. Single message = ALL spawns.**

```
PM ──┬── Task(Frontend, haiku, bg=true)
     ├── Task(Backend, sonnet, bg=true)
     ├── Task(Testing, haiku, bg=true)
     └── All spawned SIMULTANEOUSLY
```

**Protocol:**
1. Decompose -> Identify parallel streams
2. Init `.claude/` from template
3. Spawn ALL in ONE message
4. Communicate via `handoffs/*.md`

**Anti-Pattern:** Sequential spawning = WRONG

---

## PROJECT CONTEXT SYSTEM

### AUTO-INIT ON PROJECT OPEN (MANDATORY)

```
ON PROJECT OPEN:
├── 1. Detect root (package.json, .git, etc.)
├── 2. .claude/ exists?
│     ├── NO  -> Run: ~/.claude/scripts/init-project.sh
│     └── YES -> Load: status.md + todo-list.md
├── 3. MCP search: memory/search_nodes '{"query": "project:{name}"}'
└── 4. Ready
```

### Project Structure
```
{project}/.claude/
├── status.md        # Current state (read first)
├── progress.md      # Milestones
├── todo-list.md     # Tasks
├── context.md       # RAG context
├── improvements.md  # Lessons & annotations
├── contracts/       # API specs
├── handoffs/        # Agent communication
└── logs/            # Activity
```

### Progressive Loading
```
1. status.md + todo-list.md  -> Always
2. context.md                -> If architecture needed
3. contracts/                -> If specs needed
4. MCP Memory                -> If cross-session needed
```

### Session Protocols
**Start:** Load status.md + todo-list.md -> MCP search if needed
**End:** Update status.md -> Save lessons to MCP if reusable

---

## MCP SEMANTIC RAG

### Entity Naming
```
project:{name}              # Main entity
project:{name}:arch         # Architecture
project:{name}:lesson:{id}  # Lessons
project:{name}:decision:{id}# Decisions
```

### Lazy Calling (CRITICAL)
```
CALL MCP WHEN:              DON'T CALL WHEN:
├── Project start           ├── Simple edits
├── Need past solutions     ├── Context in .claude/
└── Architecture decision   └── No retrieval needed
```

### Commands
```bash
# Search
mcp-cli call memory/search_nodes '{"query": "project:MyApp"}'

# Save lesson
mcp-cli call memory/create_entities '{"entities": [{"name": "project:MyApp:lesson:001", "entityType": "lesson", "observations": ["..."]}]}'

# Add to existing
mcp-cli call memory/add_observations '{"observations": [{"entityName": "project:MyApp", "contents": ["..."]}]}'
```

---

## SERENA (Token-Efficient Code Reading)

**NEVER read entire files. Use symbolic tools.**

| Need | Tool |
|------|------|
| Overview | `get_symbols_overview` |
| Find symbol | `find_symbol` |
| Read body | `find_symbol` + `include_body=True` |
| References | `find_referencing_symbols` |

```
Progressive: overview -> signatures -> specific body -> references
```

---

## QUICK REFERENCE

### File Locations
- Templates: `~/.claude/templates/workspace/`
- Init script: `~/.claude/scripts/init-project.sh`
- Global lessons: `~/.claude/knowledge/lessons-learned.md`

### Model Selection
```
haiku   -> File ops, searches
sonnet  -> Complex logic
opus    -> Architecture decisions
```

### Rules
- Repos: PRIVATE only
- `.env`: Never modify without permission
- Contracts before parallel dev
- Track everything in `status.md`
