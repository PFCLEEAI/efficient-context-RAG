# Security Guide

> What to store, what NOT to store, and how to keep your data safe.

---

## The Golden Rule

**Never store secrets in MCP or .claude/ files.**

MCP Memory and context files are designed for project knowledge, not credentials.

---

## What NOT to Store

### Never Store These

| Type | Examples | Why |
|------|----------|-----|
| **API Keys** | `sk-...`, `OPENAI_API_KEY` | Credentials leak |
| **Passwords** | Database passwords, admin creds | Security breach |
| **Tokens** | JWT secrets, OAuth tokens | Session hijacking |
| **Private Keys** | SSH keys, SSL certificates | Server compromise |
| **Connection Strings** | `postgres://user:pass@...` | Database access |
| **Environment Variables** | Contents of `.env` files | Multiple secrets |
| **Personal Data** | SSN, credit cards, health info | Privacy/legal |
| **Internal URLs** | Private endpoints, VPN addresses | Network exposure |

### Examples of BAD Storage

```markdown
❌ DON'T DO THIS in context.md:

## API Configuration
- OpenAI Key: sk-1234567890abcdef
- Database: postgres://admin:secretpass@db.internal:5432
- JWT Secret: my-super-secret-jwt-key
```

```bash
❌ DON'T DO THIS in MCP:

mcp-cli call memory/create_entities '{"entities": [{
  "name": "project:MyApp:secrets",
  "entityType": "config",
  "observations": ["API_KEY=sk-12345", "DB_PASS=admin123"]
}]}'
```

---

## What TO Store

### Safe to Store

| Type | Examples | Why It's Safe |
|------|----------|---------------|
| **Architecture** | "Uses PostgreSQL with RLS" | No credentials |
| **Decisions** | "Chose Supabase for auth" | Rationale only |
| **Patterns** | "JWT refresh token flow" | Implementation approach |
| **Lessons** | "Always validate input" | Knowledge |
| **Tech Stack** | "Next.js 14, TypeScript" | Public info |
| **File Structure** | "Auth in src/lib/auth.ts" | Code organization |

### Examples of GOOD Storage

```markdown
✅ SAFE in context.md:

## Architecture
- Auth: Supabase Auth with social providers
- Database: PostgreSQL with Row Level Security
- API: REST with Zod validation

## Decisions
- Chose short-lived access tokens (15 min) for security
- Refresh tokens stored in httpOnly cookies
```

```bash
✅ SAFE in MCP:

mcp-cli call memory/create_entities '{"entities": [{
  "name": "project:MyApp:arch",
  "entityType": "architecture",
  "observations": [
    "Auth: Supabase with social login",
    "Database: PostgreSQL with RLS policies",
    "Pattern: JWT with refresh token rotation"
  ]
}]}'
```

---

## Secure Patterns

### Referencing Secrets

Instead of storing secrets, reference where they live:

```markdown
✅ GOOD - Reference, don't store:

## Environment Setup
- API keys: See `.env.local` (not committed)
- Database: Connection string in Vercel environment variables
- JWT secret: Stored in Supabase dashboard
```

### Documenting Auth Flows

```markdown
✅ GOOD - Document the flow, not the credentials:

## Authentication Flow
1. User submits credentials
2. Server validates against Supabase Auth
3. Returns access token (15 min) + refresh token (7 days)
4. Refresh token stored in httpOnly cookie
5. Access token in memory only

Note: Actual secrets in environment variables
```

---

## .gitignore Checklist

Ensure these are never committed:

```gitignore
# Environment
.env
.env.local
.env.*.local

# Credentials
*.pem
*.key
credentials.json
service-account.json

# Claude logs (may contain sensitive info)
.claude/logs/

# IDE with potential secrets
.idea/
.vscode/settings.json
```

---

## MCP Security Checklist

Before saving to MCP, ask:

```
□ Does this contain any API keys?
□ Does this contain any passwords?
□ Does this contain any tokens or secrets?
□ Does this contain any personal data?
□ Does this contain any internal URLs?
□ Would I be comfortable if this leaked publicly?
```

If any answer is "yes" to the first 5 or "no" to the last one, **don't store it**.

---

## Incident Response

### If You Accidentally Stored Secrets

**In MCP:**
```bash
# Delete the entity immediately
mcp-cli call memory/delete_entities '{"entityNames": ["project:MyApp:secrets"]}'

# Or delete specific observations
mcp-cli call memory/delete_observations '{"deletions": [{
  "entityName": "project:MyApp",
  "observations": ["API_KEY=sk-12345"]
}]}'
```

**In .claude/ files:**
```bash
# Remove from file
# Then rotate the compromised credential immediately!
```

**Critical:** Deleting the stored secret is NOT enough. You must also **rotate the credential** because it may have been cached or logged.

---

## Data Classification

### For Each Piece of Information, Ask:

```
┌─────────────────────────────────────────────────────────┐
│                  Data Classification                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Is it a SECRET (key, password, token)?                 │
│  ├─ YES → Never store. Reference location only.         │
│  └─ NO  ↓                                               │
│                                                          │
│  Is it PERSONAL DATA (PII)?                             │
│  ├─ YES → Never store. May violate privacy laws.        │
│  └─ NO  ↓                                               │
│                                                          │
│  Is it INTERNAL (private URLs, architecture)?           │
│  ├─ YES → Store locally in .claude/ only.               │
│  └─ NO  ↓                                               │
│                                                          │
│  Is it REUSABLE KNOWLEDGE?                              │
│  ├─ YES → Safe for MCP Memory.                          │
│  └─ NO  → Store in local .claude/ files.                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

| Data Type | Local .claude/ | MCP Memory | Git |
|-----------|----------------|------------|-----|
| Secrets/Keys | ❌ Never | ❌ Never | ❌ Never |
| Personal Data | ❌ Never | ❌ Never | ❌ Never |
| Internal URLs | ⚠️ Careful | ❌ No | ❌ No |
| Architecture | ✅ Yes | ✅ Yes | ✅ Yes |
| Decisions | ✅ Yes | ✅ Yes | ✅ Yes |
| Lessons | ✅ Yes | ✅ Yes | ✅ Yes |
| Current State | ✅ Yes | ❌ No need | ✅ Yes |

---

**When in doubt, leave it out.**
