# Contributing to Efficient Context RAG

Thank you for your interest in improving this system!

## Ways to Contribute

### 1. Share Your Benchmarks

The most valuable contribution is real-world data.

**How:**
1. Use the system for a session
2. Record your metrics (see `docs/benchmarks.md`)
3. Add your data to the benchmarks file
4. Submit a PR

**What to include:**
- Project type and complexity
- Session duration
- Context usage patterns
- Compress events
- Any issues or insights

### 2. Improve Templates

Found a better way to structure context?

**How:**
1. Fork the repo
2. Modify templates in `claude-config/templates/workspace/`
3. Test with real projects
4. Submit a PR with before/after comparison

**Guidelines:**
- Keep templates minimal (every token counts!)
- Maintain placeholder format: `{VARIABLE_NAME}`
- Include comments explaining non-obvious sections

### 3. Add Documentation

Help others understand the system better.

**Ideas:**
- Integration guides for specific tools (Cursor, VS Code, etc.)
- Language-specific examples
- Video tutorials
- Translations

### 4. Report Issues

Found a bug or have a suggestion?

**Open an issue with:**
- Clear description of the problem/suggestion
- Steps to reproduce (if bug)
- Expected vs actual behavior
- Your environment (OS, Claude Code version)

### 5. Fix Bugs

Check the Issues tab for bugs to fix.

**Process:**
1. Comment on the issue to claim it
2. Fork and create a branch
3. Fix the issue
4. Test thoroughly
5. Submit a PR referencing the issue

---

## Pull Request Process

### Before Submitting

- [ ] Test your changes with a real project
- [ ] Update relevant documentation
- [ ] Follow existing code/doc style
- [ ] Keep commits focused and atomic

### PR Title Format

```
type: Short description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- refactor: Code change that doesn't add feature or fix bug
- benchmark: Adding benchmark data
```

### PR Description Template

```markdown
## What

[Brief description of changes]

## Why

[Why this change is needed]

## Testing

[How you tested this]

## Benchmarks (if applicable)

| Metric | Before | After |
|--------|--------|-------|
| ... | ... | ... |
```

---

## Code Style

### Markdown Files

- Use ATX-style headers (`#`, `##`, etc.)
- One sentence per line (easier diffs)
- Use fenced code blocks with language hints
- Tables for structured data
- Keep lines under 100 characters when possible

### Shell Scripts

- Use `#!/bin/bash` shebang
- Include `set -e` for error handling
- Comment non-obvious logic
- Use meaningful variable names
- Quote variables: `"$VAR"` not `$VAR`

### Template Placeholders

- Use `{UPPER_SNAKE_CASE}` for placeholders
- Common placeholders:
  - `{PROJECT_NAME}` - Project name
  - `{TIMESTAMP}` - Full datetime
  - `{DATE}` - Date only
  - `{MILESTONE_NAME}` - Milestone identifier

---

## Commit Messages

### Format

```
type: Subject line (max 50 chars)

Body explaining what and why (not how).
Wrap at 72 characters.

Refs: #123 (if applicable)
```

### Good Examples

```
feat: Add quick reference card for daily use

A single-page cheat sheet with essential commands
and checklists for efficient context management.

docs: Add security guide for MCP storage

Explains what should/shouldn't be stored in MCP
to prevent accidental secret exposure.

benchmark: Add OpenWhispr session data

Real session showing 67% context usage and
successful compression to messages.md.
```

### Bad Examples

```
❌ "update readme"
❌ "fix stuff"
❌ "WIP"
❌ "asdfasdf"
```

---

## Development Setup

### Prerequisites

- Claude Code CLI installed
- MCP Memory server configured
- Bash shell

### Testing Changes

1. **Templates:**
   ```bash
   # Test init script
   mkdir /tmp/test-project
   ~/.claude/scripts/init-project.sh /tmp/test-project "TestProject"
   ls -la /tmp/test-project/.claude/
   ```

2. **Documentation:**
   - Read through for clarity
   - Check all code blocks for accuracy
   - Verify links work

3. **MCP Commands:**
   - Test commands actually work
   - Verify output format is correct

---

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Benchmark credits for data contributions

---

## Questions?

- Open a Discussion for general questions
- Open an Issue for bugs/features
- Check existing Issues/Discussions first

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make AI development more efficient!**
