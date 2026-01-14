# Troubleshooting Guide

## Common Issues

### 1. Context Window Filling Too Fast

**Symptoms:**
- Hitting 70%+ context early in session
- AI responses becoming slower
- Auto-compact triggering frequently

**Causes:**
- Loading too much context at start
- Reading full source files
- Not compressing conversation
- MCP calls returning too much data

**Solutions:**

```markdown
1. Use progressive loading:
   - Only load status.md + todo-list.md at start
   - Load additional files on demand

2. Use SERENA for code:
   - get_symbols_overview instead of reading files
   - find_symbol for specific functions
   - Never cat entire files into context

3. Compress at 70%:
   - Summarize conversation to context.md
   - Update status.md
   - Clear and continue

4. Limit MCP results:
   - Use specific searches
   - open_nodes for specific entities
   - Never read_graph unless necessary
```

### 2. Lost Context After Session

**Symptoms:**
- AI doesn't remember previous work
- Re-explaining same concepts
- Starting from scratch each session

**Causes:**
- Not updating status.md at session end
- Not saving lessons to MCP
- Not using context.md for recovery

**Solutions:**

```markdown
1. Always update status.md before ending:
   ## Session Recovery
   **Last Working On**: [current task]
   **Next Steps**: [what to do next]
   **Blockers**: [any blockers]

2. Save reusable lessons to MCP:
   mcp-cli call memory/create_entities '{"entities": [{
     "name": "project:App:lesson:001",
     "entityType": "lesson",
     "observations": ["What you learned"]
   }]}'

3. Use context.md for architecture:
   Document key decisions and patterns
   Reference this when resuming
```

### 3. MCP Entities Not Found

**Symptoms:**
- Search returns empty results
- "Entity not found" errors
- Can't retrieve saved knowledge

**Causes:**
- Incorrect entity naming
- Entity was never created
- Typos in search/open commands
- Wrong MCP server connected

**Solutions:**

```markdown
1. Check naming convention:
   project:{name}           # Correct
   Project:Name             # Wrong (case matters)
   project-name             # Wrong (use colons)

2. Verify entity exists:
   # List all entities
   mcp-cli call memory/read_graph '{}'

   # Search broadly
   mcp-cli call memory/search_nodes '{"query": "project"}'

3. Check MCP connection:
   mcp-cli servers  # Should show memory server
   mcp-cli tools memory  # Should show memory tools
```

### 4. Parallel Agents Not Communicating

**Symptoms:**
- Agents duplicating work
- Conflicting changes
- Handoffs not being read

**Causes:**
- Not using handoffs/ directory
- Agents not checking status.md
- Race conditions in file updates

**Solutions:**

```markdown
1. Use structured handoffs:
   # handoffs/frontend-to-backend.md
   ## From: @frontend
   ## To: @backend
   ## Status: PENDING

   ### Request
   [What you need]

2. Check status before starting:
   - Read status.md for agent assignments
   - Check handoffs/ for pending requests
   - Update status when starting/completing

3. Use file locking pattern:
   - One agent owns each file
   - Communicate via handoffs
   - Sync via status.md
```

### 5. Templates Not Being Applied

**Symptoms:**
- .claude/ folder empty or missing files
- Template placeholders not replaced
- init-project.sh errors

**Causes:**
- Templates not in correct location
- Script permissions not set
- Path issues

**Solutions:**

```markdown
1. Verify template location:
   ls ~/.claude/templates/workspace/
   # Should show: status.md, context.md, etc.

2. Set script permissions:
   chmod +x ~/.claude/scripts/init-project.sh

3. Run with explicit paths:
   ~/.claude/scripts/init-project.sh /full/path/to/project "ProjectName"

4. Check template syntax:
   - {PROJECT_NAME} for project name
   - {TIMESTAMP} for date/time
   - {DATE} for date only
```

### 6. SERENA Not Working

**Symptoms:**
- Symbol tools returning errors
- Can't find functions/classes
- Wrong results returned

**Causes:**
- Language not supported
- Project not indexed
- Incorrect tool usage

**Solutions:**

```markdown
1. Check language support:
   - TypeScript/JavaScript: Supported
   - Python: Supported
   - Go, Rust, etc.: Check docs

2. Use correct tool for task:
   | Need | Tool |
   |------|------|
   | Overview | get_symbols_overview |
   | Find | find_symbol |
   | Body | find_symbol + include_body=True |
   | Refs | find_referencing_symbols |

3. Fallback to file read if needed:
   - Some files may not parse correctly
   - Use Read tool as last resort
```

## Error Messages

### "Context limit exceeded"

```markdown
Cause: Hit the 200k token limit

Fix:
1. Run /compact or /clear
2. Compress conversation to context.md
3. Use progressive loading going forward
```

### "MCP server not connected"

```markdown
Cause: MCP Memory server not running

Fix:
1. Check MCP configuration
2. Restart Claude Code
3. Verify with: mcp-cli servers
```

### "Entity already exists"

```markdown
Cause: Trying to create duplicate entity

Fix:
1. Use add_observations instead of create_entities
2. Or use unique names (lesson:001, lesson:002)
```

### "Permission denied" (init script)

```markdown
Cause: Script not executable

Fix:
chmod +x ~/.claude/scripts/init-project.sh
```

## Recovery Procedures

### Complete Context Loss

```markdown
1. Don't panic - your work is saved
2. Read .claude/status.md for current state
3. Read .claude/context.md for architecture
4. MCP search for historical context
5. Check git log for recent changes
6. Reconstruct from these sources
```

### Corrupted .claude/ Directory

```markdown
1. Check git for previous version:
   git log -- .claude/
   git checkout HEAD~1 -- .claude/

2. Or re-initialize:
   rm -rf .claude/
   ~/.claude/scripts/init-project.sh . "ProjectName"

3. Restore from MCP:
   mcp-cli call memory/search_nodes '{"query": "project:Name"}'
```

### MCP Data Loss

```markdown
1. Check MCP data location (varies by setup)
2. Restore from backup if available
3. Recreate entities from:
   - .claude/context.md (decisions)
   - .claude/improvements.md (lessons)
   - Git history (changes)
```

## Prevention

### Daily Habits

```markdown
1. Update status.md at end of each session
2. Save important lessons to MCP immediately
3. Compress at 70% context, not 90%
4. Use progressive loading always
```

### Weekly Maintenance

```markdown
1. Review and clean up todo-list.md
2. Archive completed items to progress.md
3. Sync lessons from improvements.md to MCP
4. Check for stale MCP entities
```

### Project Completion

```markdown
1. Final update to status.md (mark complete)
2. Create project summary in MCP
3. Archive lessons for future reference
4. Document patterns in MCP
```
