# MCP Integration Guide

## What is MCP?

MCP (Model Context Protocol) is a standard for AI models to interact with external tools and data sources. The Memory server provides persistent, semantic storage that survives across sessions.

## Why Use MCP Memory?

### The Problem

AI sessions are ephemeral. When you start a new conversation:
- Previous context is lost
- You re-explain the same things
- Lessons learned are forgotten
- Architecture decisions need re-discovery

### The Solution

MCP Memory provides:
- **Persistent storage** - Survives across sessions
- **Semantic search** - Find by meaning, not just keywords
- **Structured knowledge** - Entities, relations, observations
- **Lazy retrieval** - Load only what you need

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Memory System                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Entities   │────│  Relations   │────│ Observations │  │
│  │              │    │              │    │              │  │
│  │ project:App  │    │ has_arch     │    │ "Uses React" │  │
│  │ lesson:001   │    │ applies_to   │    │ "Started..." │  │
│  │ decision:001 │    │ depends_on   │    │ "Rationale.."│  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  Query Layer                                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ search_nodes → find by semantic meaning              │  │
│  │ open_nodes   → get full entity details               │  │
│  │ read_graph   → get entire knowledge graph            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Entity Types

### Project Entity

Main container for project knowledge:

```json
{
  "name": "project:MyApp",
  "entityType": "project",
  "observations": [
    "E-commerce platform with React frontend",
    "Supabase backend with PostgreSQL",
    "Stripe integration for payments",
    "Started: 2024-01-15"
  ]
}
```

### Architecture Entity

Technical decisions and structure:

```json
{
  "name": "project:MyApp:arch",
  "entityType": "architecture",
  "observations": [
    "Frontend: Next.js 14, TypeScript, TailwindCSS",
    "Backend: Supabase Edge Functions",
    "Database: PostgreSQL with RLS",
    "Auth: Supabase Auth with social providers"
  ]
}
```

### Lesson Entity

Learnings applicable to future work:

```json
{
  "name": "project:MyApp:lesson:001",
  "entityType": "lesson",
  "observations": [
    "Issue: Race condition in cart updates",
    "Solution: Use database transactions",
    "Prevention: Always lock rows during multi-step writes"
  ]
}
```

### Decision Entity

Key choices and their rationale:

```json
{
  "name": "project:MyApp:decision:001",
  "entityType": "decision",
  "observations": [
    "Decision: Use Supabase over Firebase",
    "Rationale: Better PostgreSQL support, RLS policies",
    "Trade-off: Smaller community",
    "Date: 2024-01-10"
  ]
}
```

## Naming Convention

```
project:{name}              # Main project
project:{name}:arch         # Architecture
project:{name}:lesson:{id}  # Lesson learned
project:{name}:decision:{id}# Key decision
project:{name}:pattern:{id} # Reusable pattern

# Global (not project-specific)
lesson:{topic}:{id}         # General lesson
pattern:{name}              # Reusable pattern
```

## Lazy Calling Strategy

### When to Call MCP

```
CALL MCP:
├── Session start (search for project context)
├── Before major architecture decision
├── When encountering familiar problem
├── When completing work worth remembering
└── When switching between projects
```

### When NOT to Call MCP

```
DON'T CALL MCP:
├── Simple file edits
├── Context already in local .claude/
├── Routine tasks
├── Every small question
└── Information already in conversation
```

### Cost-Benefit Analysis

Each MCP call costs:
- ~500-1000 tokens for request/response
- Network latency
- Context switching

Only call when benefit > cost.

## Integration with Local Context

### Separation of Concerns

```
Local .claude/ Files          MCP Memory
├── Current session state     ├── Cross-session knowledge
├── Active todos              ├── Lessons learned
├── Today's progress          ├── Architecture decisions
├── Current blockers          ├── Reusable patterns
└── Ephemeral context         └── Permanent knowledge
```

### Sync Strategy

```
Session Start:
1. Load local status.md
2. MCP search for project
3. Load additional MCP entities if needed

Session End:
1. Update local status.md
2. Save NEW lessons to MCP
3. Don't duplicate - reference local files
```

## Example Workflows

### New Project Setup

```bash
# 1. Initialize local context
~/.claude/scripts/init-project.sh . "MyApp"

# 2. Create MCP entity
mcp-cli call memory/create_entities '{"entities": [{
  "name": "project:MyApp",
  "entityType": "project",
  "observations": [
    "Project initialized: 2024-01-15",
    "Type: Web application",
    "Tech: Next.js, Supabase"
  ]
}]}'
```

### Resuming After Break

```bash
# 1. Read local status
cat .claude/status.md

# 2. Search MCP for context
mcp-cli call memory/search_nodes '{"query": "project:MyApp"}'

# 3. Load specific entities if needed
mcp-cli call memory/open_nodes '{"names": ["project:MyApp:arch"]}'
```

### After Solving Hard Problem

```bash
# Save the lesson
mcp-cli call memory/create_entities '{"entities": [{
  "name": "project:MyApp:lesson:002",
  "entityType": "lesson",
  "observations": [
    "Problem: Supabase RLS blocked service role",
    "Root cause: Forgot to set service_role in edge function",
    "Solution: Use createClient with service_role key for admin ops"
  ]
}]}'
```

## Best Practices

### Entity Design

1. **One concept per entity** - Don't mix unrelated info
2. **Atomic observations** - One fact per observation
3. **Consistent naming** - Follow the convention
4. **Link with relations** - Build a knowledge graph

### Observation Quality

Good:
```
"Use database transactions for multi-step writes to prevent race conditions"
```

Bad:
```
"Fixed the bug" (too vague)
"The entire authentication module code is..." (too long)
```

### Search Effectiveness

Good searches:
```
"project:MyApp"           # All project context
"lesson authentication"   # Lessons about auth
"decision database"       # Database decisions
```

Bad searches:
```
"stuff"                   # Too vague
"the thing from last week" # Not semantic
```

## Troubleshooting

### Entity Not Found

1. Check naming convention
2. Try broader search terms
3. Verify entity was created (no errors)
4. Check for typos in entity name

### Too Much Data Returned

1. Use more specific search terms
2. Use `open_nodes` for specific entities
3. Don't use `read_graph` unless necessary

### Stale Information

1. Use `add_observations` to update
2. Use `delete_observations` to remove old info
3. Consider archiving old projects
