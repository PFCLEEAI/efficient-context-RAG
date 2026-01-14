# Progressive Loading Strategy

## Core Principle

**Never load all context at once.** Load only what the current task requires.

## The Problem

AI context windows are finite (200k tokens for Claude). Loading everything wastes precious tokens on irrelevant information, leaving less room for:
- Actual conversation
- Code analysis
- Complex reasoning

## The Solution: Progressive Loading

### Load Order

```
Priority 1: ALWAYS LOAD
├── status.md        → Current project state
└── todo-list.md     → What needs to be done

Priority 2: ON DEMAND
├── context.md       → When architecture understanding needed
├── contracts/       → When API specs needed
└── improvements.md  → When reviewing tech debt

Priority 3: CROSS-SESSION
└── MCP Memory       → When historical context needed
```

### Decision Tree

```
What do I need to know?
│
├── Current state of project?
│   └── Load: status.md + todo-list.md
│
├── How does the architecture work?
│   └── Load: context.md
│
├── What's the API contract?
│   └── Load: contracts/api.md
│
├── What lessons did we learn before?
│   └── MCP search: memory/search_nodes
│
└── What files implement X feature?
    └── Use SERENA symbolic search (not full file reads)
```

## Implementation

### On Project Open

```python
# Pseudo-code for progressive loading
def on_project_open(project_path):
    # Always load
    load_file(f"{project_path}/.claude/status.md")
    load_file(f"{project_path}/.claude/todo-list.md")

    # Check MCP if entity exists
    mcp_search(f"project:{project_name}")

    # DO NOT auto-load:
    # - context.md
    # - contracts/
    # - Full source files
```

### During Work

```python
def before_task(task):
    if task.needs_architecture():
        load_file(".claude/context.md")

    if task.needs_api_specs():
        load_file(".claude/contracts/api.md")

    if task.involves_past_decision():
        mcp_search("project:{name}:decision")
```

## Token Budget Management

### Typical Distribution (200k context)

```
System Prompt:     ~20k tokens (10%)
Tools:             ~15k tokens (7.5%)
Project Context:   ~20k tokens (10%)  ← Progressive loading target
Messages:          ~100k tokens (50%)
Safety Buffer:     ~45k tokens (22.5%)
```

### Progressive Loading Target: 10%

Keep project context under 20k tokens by:
1. Loading only essential files
2. Using references instead of full content
3. Compressing historical context

## Comparison

### Without Progressive Loading

```
Session Start:
├── Load CLAUDE.md (2k tokens)
├── Load status.md (1k tokens)
├── Load context.md (2k tokens)
├── Load todo-list.md (1k tokens)
├── Load progress.md (1k tokens)
├── Load improvements.md (1k tokens)
├── Load contracts/api.md (1k tokens)
├── Load contracts/types.md (1k tokens)
├── MCP full graph (5k tokens)
└── Total: ~15k tokens BEFORE any work

Problem: 7.5% wasted on potentially unused context
```

### With Progressive Loading

```
Session Start:
├── Load status.md (1k tokens)
├── Load todo-list.md (1k tokens)
└── Total: ~2k tokens

On architecture question:
├── Load context.md (2k tokens)
└── Total: ~4k tokens

On API work:
├── Load contracts/api.md (1k tokens)
└── Total: ~5k tokens

Savings: 10k tokens available for actual work
```

## Best Practices

### DO

1. **Check status.md first** - It tells you what context you need
2. **Use references** - "See contracts/api.md" instead of loading
3. **Load on demand** - Only when task requires it
4. **Unload when done** - Mental model: if a long task completes, that context can be "forgotten"

### DON'T

1. **Dump all files at start** - Wasteful
2. **Re-read same files** - Cache the mental model
3. **Load full source files** - Use SERENA symbolic tools
4. **Keep all context forever** - Compress and archive

## Measuring Efficiency

### Good Signs

- Context usage stays under 70%
- You're loading files only when tasks need them
- MCP calls are infrequent but valuable
- Conversations are productive, not repetitive

### Bad Signs

- Context hits 80%+ early in session
- Same files loaded multiple times
- MCP called for every small task
- Conversation rehashes same info repeatedly

## Integration with Other Strategies

### With MCP RAG

```
Progressive Loading + MCP =
├── Local .claude/ for current session
└── MCP for cross-session persistence

Don't duplicate! If it's in MCP, reference it.
```

### With SERENA

```
Progressive Loading + SERENA =
├── Load project context from .claude/
└── Use symbolic tools for code exploration

Never: Read entire files into context
```

### With Compression

```
Progressive Loading + Compression =
├── Load minimal context
├── Work productively
├── Compress when hitting 70%
└── Continue with lean context

Cycle: Load → Work → Compress → Load → ...
```
