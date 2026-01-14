# MCP Memory Commands Reference

## Overview

MCP (Model Context Protocol) Memory provides persistent, semantic storage for AI context across sessions. This eliminates the need to re-explain project context every time you start a new conversation.

## Entity Naming Convention

```
project:{name}              # Main project entity
project:{name}:arch         # Architecture decisions
project:{name}:lesson:{id}  # Lessons learned
project:{name}:decision:{id}# Key decisions
project:{name}:pattern:{id} # Reusable patterns
```

## Core Commands

### 1. Search for Context

```bash
# Search for all project-related entities
mcp-cli call memory/search_nodes '{"query": "project:MyApp"}'

# Search for specific lessons
mcp-cli call memory/search_nodes '{"query": "lesson authentication"}'

# Search for architecture decisions
mcp-cli call memory/search_nodes '{"query": "project:MyApp:arch"}'
```

### 2. Create New Entities

```bash
# Create a main project entity
mcp-cli call memory/create_entities '{"entities": [
  {
    "name": "project:MyApp",
    "entityType": "project",
    "observations": [
      "E-commerce platform built with Next.js and Supabase",
      "Tech stack: Next.js 14, TypeScript, Supabase, TailwindCSS",
      "Started: 2024-01-15"
    ]
  }
]}'

# Create a lesson learned
mcp-cli call memory/create_entities '{"entities": [
  {
    "name": "project:MyApp:lesson:001",
    "entityType": "lesson",
    "observations": [
      "Always validate API input at the boundary layer",
      "Use Zod schemas for type-safe validation",
      "Return meaningful error messages to clients"
    ]
  }
]}'

# Create an architecture decision
mcp-cli call memory/create_entities '{"entities": [
  {
    "name": "project:MyApp:decision:001",
    "entityType": "decision",
    "observations": [
      "Decision: Use Supabase instead of Firebase",
      "Rationale: Better PostgreSQL support, RLS policies, real-time built-in",
      "Trade-off: Smaller community than Firebase",
      "Date: 2024-01-15"
    ]
  }
]}'
```

### 3. Add Observations to Existing Entities

```bash
# Add new observation to project
mcp-cli call memory/add_observations '{"observations": [
  {
    "entityName": "project:MyApp",
    "contents": [
      "Added authentication module 2024-01-20",
      "Integrated Stripe for payments 2024-01-25"
    ]
  }
]}'

# Add to a lesson
mcp-cli call memory/add_observations '{"observations": [
  {
    "entityName": "project:MyApp:lesson:001",
    "contents": [
      "Also applies to: webhook handlers, cron jobs"
    ]
  }
]}'
```

### 4. Create Relations Between Entities

```bash
# Link a lesson to a project
mcp-cli call memory/create_relations '{"relations": [
  {
    "from": "project:MyApp:lesson:001",
    "to": "project:MyApp",
    "relationType": "applies_to"
  }
]}'

# Link a decision to architecture
mcp-cli call memory/create_relations '{"relations": [
  {
    "from": "project:MyApp:decision:001",
    "to": "project:MyApp:arch",
    "relationType": "defines"
  }
]}'
```

### 5. Open Specific Nodes

```bash
# Open a specific entity with full details
mcp-cli call memory/open_nodes '{"names": ["project:MyApp"]}'

# Open multiple entities
mcp-cli call memory/open_nodes '{"names": [
  "project:MyApp",
  "project:MyApp:arch",
  "project:MyApp:lesson:001"
]}'
```

### 6. Read Full Graph

```bash
# Get the entire knowledge graph (use sparingly - can be large)
mcp-cli call memory/read_graph '{}'
```

### 7. Delete Operations

```bash
# Delete specific observations
mcp-cli call memory/delete_observations '{"deletions": [
  {
    "entityName": "project:MyApp",
    "observations": ["Outdated info to remove"]
  }
]}'

# Delete entities
mcp-cli call memory/delete_entities '{"entityNames": ["project:OldProject"]}'

# Delete relations
mcp-cli call memory/delete_relations '{"relations": [
  {
    "from": "entity1",
    "to": "entity2",
    "relationType": "old_relation"
  }
]}'
```

## Workflow Examples

### Starting a New Project

```bash
# 1. Create main project entity
mcp-cli call memory/create_entities '{"entities": [
  {
    "name": "project:NewApp",
    "entityType": "project",
    "observations": [
      "Description: Task management app",
      "Tech: React, Node.js, PostgreSQL",
      "Started: 2024-01-15"
    ]
  }
]}'

# 2. Create architecture entity
mcp-cli call memory/create_entities '{"entities": [
  {
    "name": "project:NewApp:arch",
    "entityType": "architecture",
    "observations": [
      "Frontend: React 18 with TypeScript",
      "Backend: Express.js REST API",
      "Database: PostgreSQL with Prisma ORM",
      "Auth: JWT with refresh tokens"
    ]
  }
]}'

# 3. Link them
mcp-cli call memory/create_relations '{"relations": [
  {
    "from": "project:NewApp",
    "to": "project:NewApp:arch",
    "relationType": "has_architecture"
  }
]}'
```

### Resuming Work on Existing Project

```bash
# 1. Search for project context
mcp-cli call memory/search_nodes '{"query": "project:MyApp"}'

# 2. Open relevant entities
mcp-cli call memory/open_nodes '{"names": [
  "project:MyApp",
  "project:MyApp:arch"
]}'

# 3. Check for lessons that might apply
mcp-cli call memory/search_nodes '{"query": "lesson authentication"}'
```

### Saving a Lesson After Debugging

```bash
# After fixing a tricky bug, save the lesson
mcp-cli call memory/create_entities '{"entities": [
  {
    "name": "project:MyApp:lesson:002",
    "entityType": "lesson",
    "observations": [
      "Issue: Race condition in cart updates",
      "Root cause: Optimistic updates without proper locking",
      "Solution: Use database transactions with SELECT FOR UPDATE",
      "Prevention: Always use transactions for multi-step writes"
    ]
  }
]}'
```

## Best Practices

### DO
- Use consistent entity naming
- Keep observations atomic and specific
- Link related entities with relations
- Search before creating duplicates
- Save lessons immediately after learning them

### DON'T
- Store entire code files as observations
- Create overly generic entity names
- Forget to link entities
- Let observations grow too long
- Call MCP for every small task (lazy calling!)

## Token Efficiency Tips

1. **Search first, create if needed** - Don't duplicate entities
2. **Keep observations concise** - One fact per observation
3. **Use relations over repetition** - Link entities instead of copying info
4. **Lazy calling** - Only call MCP when cross-session context is needed
