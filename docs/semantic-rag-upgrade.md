# Semantic RAG Upgrade Guide

> Add true semantic search to your context management system for larger projects.

---

## When to Upgrade

| Project Size | Recommendation |
|--------------|----------------|
| Small (10-50 entities) | Current system is fine |
| Medium (50-200 entities) | Consider semantic for discovery |
| Large (200+ entities) | Semantic RAG recommended |
| Multi-project (1000+ docs) | Semantic RAG essential |

**Signs you need semantic RAG:**
- Can't remember exact entity names
- Missing relevant context because of naming
- Want "find similar problems" capability
- Knowledge base growing beyond manual management

---

## Choose Your Path

| Option | Cost | Setup | Best For |
|--------|------|-------|----------|
| **Option A: Local** | Free | Medium | Privacy, offline, no API limits |
| **Option B: API** | ~$0.02/1M tokens | Easy | Simplicity, better quality |

---

# Option A: Local Embeddings (Free)

## Overview

```
┌─────────────────────────────────────────────────────────┐
│                Local Semantic RAG Stack                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Your Knowledge ──► Ollama ──► ChromaDB ──► Search      │
│                     (embed)    (store)      (retrieve)  │
│                                                          │
│  Cost: $0                                               │
│  Privacy: 100% local                                    │
│  Speed: Fast (after initial setup)                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.9+
- ~4GB disk space for models
- 8GB+ RAM recommended

## Step 1: Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

Start Ollama:
```bash
ollama serve
```

## Step 2: Pull Embedding Model

```bash
# Recommended: Good balance of speed and quality
ollama pull nomic-embed-text

# Alternative: Higher quality, slower
ollama pull mxbai-embed-large

# Alternative: Fastest, lower quality
ollama pull all-minilm
```

**Model Comparison:**

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `nomic-embed-text` | 274MB | Fast | Good | General use |
| `mxbai-embed-large` | 670MB | Medium | Great | Higher accuracy |
| `all-minilm` | 46MB | Very fast | OK | Speed priority |

## Step 3: Install Python Dependencies

```bash
pip install chromadb ollama
```

## Step 4: Create the Semantic Search System

Create `~/.claude/scripts/semantic_rag.py`:

```python
#!/usr/bin/env python3
"""
Local Semantic RAG for Claude Context Management
Uses Ollama for embeddings and ChromaDB for vector storage
"""

import json
import ollama
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import Optional
import argparse

# Configuration
CHROMA_PATH = Path.home() / ".claude" / "semantic_db"
COLLECTION_NAME = "claude_knowledge"
EMBEDDING_MODEL = "nomic-embed-text"  # Change if using different model

# Initialize ChromaDB
client = chromadb.PersistentClient(
    path=str(CHROMA_PATH),
    settings=Settings(anonymized_telemetry=False)
)

def get_collection():
    """Get or create the knowledge collection."""
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Claude context knowledge base"}
    )

def generate_embedding(text: str) -> list:
    """Generate embedding using Ollama."""
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )
    return response["embedding"]

def add_knowledge(
    entity_id: str,
    content: str,
    metadata: Optional[dict] = None
):
    """Add knowledge to the semantic database."""
    collection = get_collection()

    # Generate embedding
    embedding = generate_embedding(content)

    # Prepare metadata
    meta = metadata or {}
    meta["content_preview"] = content[:200]

    # Add to collection
    collection.add(
        ids=[entity_id],
        embeddings=[embedding],
        documents=[content],
        metadatas=[meta]
    )

    print(f"✓ Added: {entity_id}")

def search_knowledge(
    query: str,
    n_results: int = 5,
    filter_metadata: Optional[dict] = None
) -> list:
    """Search for similar knowledge."""
    collection = get_collection()

    # Generate query embedding
    query_embedding = generate_embedding(query)

    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filter_metadata
    )

    return results

def update_knowledge(entity_id: str, content: str, metadata: Optional[dict] = None):
    """Update existing knowledge."""
    collection = get_collection()

    # Generate new embedding
    embedding = generate_embedding(content)

    # Prepare metadata
    meta = metadata or {}
    meta["content_preview"] = content[:200]

    # Update
    collection.update(
        ids=[entity_id],
        embeddings=[embedding],
        documents=[content],
        metadatas=[meta]
    )

    print(f"✓ Updated: {entity_id}")

def delete_knowledge(entity_id: str):
    """Delete knowledge from database."""
    collection = get_collection()
    collection.delete(ids=[entity_id])
    print(f"✓ Deleted: {entity_id}")

def list_all(limit: int = 100):
    """List all knowledge in database."""
    collection = get_collection()
    results = collection.get(limit=limit)
    return results

def import_from_mcp(mcp_export_file: str):
    """Import entities from MCP memory export."""
    with open(mcp_export_file, 'r') as f:
        data = json.load(f)

    for entity in data.get('entities', []):
        entity_id = entity['name']
        content = f"{entity['entityType']}: {' | '.join(entity.get('observations', []))}"
        metadata = {
            "entity_type": entity.get('entityType', 'unknown'),
            "source": "mcp_import"
        }
        add_knowledge(entity_id, content, metadata)

def main():
    parser = argparse.ArgumentParser(description='Local Semantic RAG for Claude')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add knowledge')
    add_parser.add_argument('id', help='Entity ID')
    add_parser.add_argument('content', help='Content to add')
    add_parser.add_argument('--type', default='knowledge', help='Entity type')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search knowledge')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', type=int, default=5, help='Number of results')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update knowledge')
    update_parser.add_argument('id', help='Entity ID')
    update_parser.add_argument('content', help='New content')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete knowledge')
    delete_parser.add_argument('id', help='Entity ID')

    # List command
    list_parser = subparsers.add_parser('list', help='List all knowledge')
    list_parser.add_argument('-n', type=int, default=100, help='Limit')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import from MCP export')
    import_parser.add_argument('file', help='MCP export JSON file')

    args = parser.parse_args()

    if args.command == 'add':
        add_knowledge(args.id, args.content, {"entity_type": args.type})

    elif args.command == 'search':
        results = search_knowledge(args.query, args.n)
        print(f"\n🔍 Search results for: '{args.query}'\n")
        for i, (id_, doc, dist) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['distances'][0]
        )):
            similarity = 1 - dist  # Convert distance to similarity
            print(f"{i+1}. [{similarity:.2%}] {id_}")
            print(f"   {doc[:100]}...")
            print()

    elif args.command == 'update':
        update_knowledge(args.id, args.content)

    elif args.command == 'delete':
        delete_knowledge(args.id)

    elif args.command == 'list':
        results = list_all(args.n)
        print(f"\n📚 Knowledge base ({len(results['ids'])} items):\n")
        for id_, doc in zip(results['ids'], results['documents']):
            print(f"  • {id_}")
            print(f"    {doc[:80]}...")
            print()

    elif args.command == 'import':
        import_from_mcp(args.file)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

Make it executable:
```bash
chmod +x ~/.claude/scripts/semantic_rag.py
```

## Step 5: Usage

### Add Knowledge

```bash
# Add a lesson
python ~/.claude/scripts/semantic_rag.py add \
  "lesson:auth:001" \
  "Always use httpOnly cookies for refresh tokens to prevent XSS attacks" \
  --type lesson

# Add a decision
python ~/.claude/scripts/semantic_rag.py add \
  "decision:db:001" \
  "Chose PostgreSQL over MongoDB for strong consistency and complex queries" \
  --type decision

# Add a pattern
python ~/.claude/scripts/semantic_rag.py add \
  "pattern:error:001" \
  "Implement exponential backoff for API retries: 1s, 2s, 4s, 8s max" \
  --type pattern
```

### Search Knowledge

```bash
# Find similar concepts (this is the magic!)
python ~/.claude/scripts/semantic_rag.py search "how to handle authentication securely"

# Search for error handling
python ~/.claude/scripts/semantic_rag.py search "retry failed requests"

# Search for database decisions
python ~/.claude/scripts/semantic_rag.py search "which database to use"
```

**Example output:**
```
🔍 Search results for: 'how to handle authentication securely'

1. [94.2%] lesson:auth:001
   Always use httpOnly cookies for refresh tokens to prevent XSS attacks...

2. [87.5%] pattern:jwt:001
   JWT refresh token rotation: issue new refresh token on each use...

3. [82.1%] decision:auth:001
   Chose Supabase Auth for built-in security best practices...
```

### Other Commands

```bash
# List all knowledge
python ~/.claude/scripts/semantic_rag.py list

# Update existing
python ~/.claude/scripts/semantic_rag.py update "lesson:auth:001" "Updated content here"

# Delete
python ~/.claude/scripts/semantic_rag.py delete "lesson:auth:001"

# Import from MCP export
python ~/.claude/scripts/semantic_rag.py import mcp_export.json
```

---

# Option B: API Embeddings (Simple)

## Overview

```
┌─────────────────────────────────────────────────────────┐
│                 API Semantic RAG Stack                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Your Knowledge ──► OpenAI API ──► ChromaDB ──► Search  │
│                     (embed)        (store)     (retrieve)│
│                                                          │
│  Cost: ~$0.02 per 1M tokens                             │
│  Quality: Excellent                                      │
│  Setup: Minimal                                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## API Providers Comparison

| Provider | Model | Cost/1M tokens | Quality | Notes |
|----------|-------|----------------|---------|-------|
| **OpenAI** | text-embedding-3-small | $0.02 | Great | Best value |
| **OpenAI** | text-embedding-3-large | $0.13 | Excellent | Highest quality |
| **Voyage AI** | voyage-3-lite | $0.02 | Great | Good alternative |
| **Voyage AI** | voyage-3 | $0.06 | Excellent | Best for code |
| **Cohere** | embed-english-v3 | Free tier | Good | 100 calls/min free |
| **Google** | text-embedding-004 | $0.025 | Great | Good for GCP users |

## Step 1: Get API Key

### OpenAI (Recommended)
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Save it securely

### Voyage AI (Best for Code)
1. Go to https://www.voyageai.com/
2. Sign up and get API key
3. Good for code-heavy knowledge

### Cohere (Free Tier)
1. Go to https://cohere.com/
2. Sign up for free tier
3. 100 API calls/minute free

## Step 2: Install Dependencies

```bash
pip install chromadb openai
# Or for other providers:
# pip install chromadb voyageai
# pip install chromadb cohere
```

## Step 3: Create the API-based System

Create `~/.claude/scripts/semantic_rag_api.py`:

```python
#!/usr/bin/env python3
"""
API-based Semantic RAG for Claude Context Management
Uses OpenAI/Voyage/Cohere for embeddings and ChromaDB for vector storage
"""

import os
import json
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import Optional
import argparse

# ============================================================
# CONFIGURATION - Choose your provider
# ============================================================

# Option 1: OpenAI (recommended)
PROVIDER = "openai"
EMBEDDING_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large"
API_KEY_ENV = "OPENAI_API_KEY"

# Option 2: Voyage AI (best for code)
# PROVIDER = "voyage"
# EMBEDDING_MODEL = "voyage-3-lite"  # or "voyage-3"
# API_KEY_ENV = "VOYAGE_API_KEY"

# Option 3: Cohere (free tier available)
# PROVIDER = "cohere"
# EMBEDDING_MODEL = "embed-english-v3.0"
# API_KEY_ENV = "COHERE_API_KEY"

# ============================================================

CHROMA_PATH = Path.home() / ".claude" / "semantic_db_api"
COLLECTION_NAME = "claude_knowledge"

# Initialize ChromaDB
client = chromadb.PersistentClient(
    path=str(CHROMA_PATH),
    settings=Settings(anonymized_telemetry=False)
)

def get_api_key():
    """Get API key from environment."""
    key = os.environ.get(API_KEY_ENV)
    if not key:
        raise ValueError(f"Please set {API_KEY_ENV} environment variable")
    return key

def generate_embedding_openai(text: str) -> list:
    """Generate embedding using OpenAI."""
    from openai import OpenAI
    client = OpenAI(api_key=get_api_key())
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def generate_embedding_voyage(text: str) -> list:
    """Generate embedding using Voyage AI."""
    import voyageai
    client = voyageai.Client(api_key=get_api_key())
    result = client.embed([text], model=EMBEDDING_MODEL)
    return result.embeddings[0]

def generate_embedding_cohere(text: str) -> list:
    """Generate embedding using Cohere."""
    import cohere
    client = cohere.Client(get_api_key())
    response = client.embed(
        texts=[text],
        model=EMBEDDING_MODEL,
        input_type="search_document"
    )
    return response.embeddings[0]

def generate_embedding(text: str) -> list:
    """Generate embedding using configured provider."""
    if PROVIDER == "openai":
        return generate_embedding_openai(text)
    elif PROVIDER == "voyage":
        return generate_embedding_voyage(text)
    elif PROVIDER == "cohere":
        return generate_embedding_cohere(text)
    else:
        raise ValueError(f"Unknown provider: {PROVIDER}")

def get_collection():
    """Get or create the knowledge collection."""
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "Claude context knowledge base",
            "provider": PROVIDER,
            "model": EMBEDDING_MODEL
        }
    )

def add_knowledge(
    entity_id: str,
    content: str,
    metadata: Optional[dict] = None
):
    """Add knowledge to the semantic database."""
    collection = get_collection()

    # Generate embedding
    embedding = generate_embedding(content)

    # Prepare metadata
    meta = metadata or {}
    meta["content_preview"] = content[:200]

    # Add to collection
    collection.add(
        ids=[entity_id],
        embeddings=[embedding],
        documents=[content],
        metadatas=[meta]
    )

    print(f"✓ Added: {entity_id}")

def search_knowledge(
    query: str,
    n_results: int = 5,
    filter_metadata: Optional[dict] = None
) -> list:
    """Search for similar knowledge."""
    collection = get_collection()

    # Generate query embedding
    query_embedding = generate_embedding(query)

    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filter_metadata
    )

    return results

def update_knowledge(entity_id: str, content: str, metadata: Optional[dict] = None):
    """Update existing knowledge."""
    collection = get_collection()

    # Generate new embedding
    embedding = generate_embedding(content)

    # Prepare metadata
    meta = metadata or {}
    meta["content_preview"] = content[:200]

    # Update
    collection.update(
        ids=[entity_id],
        embeddings=[embedding],
        documents=[content],
        metadatas=[meta]
    )

    print(f"✓ Updated: {entity_id}")

def delete_knowledge(entity_id: str):
    """Delete knowledge from database."""
    collection = get_collection()
    collection.delete(ids=[entity_id])
    print(f"✓ Deleted: {entity_id}")

def list_all(limit: int = 100):
    """List all knowledge in database."""
    collection = get_collection()
    results = collection.get(limit=limit)
    return results

def import_from_mcp(mcp_export_file: str):
    """Import entities from MCP memory export."""
    with open(mcp_export_file, 'r') as f:
        data = json.load(f)

    for entity in data.get('entities', []):
        entity_id = entity['name']
        content = f"{entity['entityType']}: {' | '.join(entity.get('observations', []))}"
        metadata = {
            "entity_type": entity.get('entityType', 'unknown'),
            "source": "mcp_import"
        }
        add_knowledge(entity_id, content, metadata)

def estimate_cost(text: str) -> dict:
    """Estimate embedding cost for text."""
    # Rough token estimate: ~4 chars per token
    tokens = len(text) / 4

    costs = {
        "openai-small": tokens * 0.02 / 1_000_000,
        "openai-large": tokens * 0.13 / 1_000_000,
        "voyage-lite": tokens * 0.02 / 1_000_000,
        "voyage-3": tokens * 0.06 / 1_000_000,
        "cohere": 0  # Free tier
    }

    return {
        "estimated_tokens": int(tokens),
        "costs": {k: f"${v:.6f}" for k, v in costs.items()}
    }

def main():
    parser = argparse.ArgumentParser(description='API Semantic RAG for Claude')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add knowledge')
    add_parser.add_argument('id', help='Entity ID')
    add_parser.add_argument('content', help='Content to add')
    add_parser.add_argument('--type', default='knowledge', help='Entity type')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search knowledge')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', type=int, default=5, help='Number of results')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update knowledge')
    update_parser.add_argument('id', help='Entity ID')
    update_parser.add_argument('content', help='New content')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete knowledge')
    delete_parser.add_argument('id', help='Entity ID')

    # List command
    list_parser = subparsers.add_parser('list', help='List all knowledge')
    list_parser.add_argument('-n', type=int, default=100, help='Limit')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import from MCP export')
    import_parser.add_argument('file', help='MCP export JSON file')

    # Cost estimate command
    cost_parser = subparsers.add_parser('cost', help='Estimate embedding cost')
    cost_parser.add_argument('text', help='Text to estimate')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show configuration')

    args = parser.parse_args()

    if args.command == 'add':
        add_knowledge(args.id, args.content, {"entity_type": args.type})

    elif args.command == 'search':
        results = search_knowledge(args.query, args.n)
        print(f"\n🔍 Search results for: '{args.query}'\n")
        print(f"   Provider: {PROVIDER} | Model: {EMBEDDING_MODEL}\n")
        for i, (id_, doc, dist) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['distances'][0]
        )):
            similarity = 1 - dist
            print(f"{i+1}. [{similarity:.2%}] {id_}")
            print(f"   {doc[:100]}...")
            print()

    elif args.command == 'update':
        update_knowledge(args.id, args.content)

    elif args.command == 'delete':
        delete_knowledge(args.id)

    elif args.command == 'list':
        results = list_all(args.n)
        print(f"\n📚 Knowledge base ({len(results['ids'])} items):\n")
        for id_, doc in zip(results['ids'], results['documents']):
            print(f"  • {id_}")
            print(f"    {doc[:80]}...")
            print()

    elif args.command == 'import':
        import_from_mcp(args.file)

    elif args.command == 'cost':
        estimate = estimate_cost(args.text)
        print(f"\n💰 Cost Estimate\n")
        print(f"   Estimated tokens: {estimate['estimated_tokens']}")
        print(f"\n   Costs by provider:")
        for provider, cost in estimate['costs'].items():
            print(f"   • {provider}: {cost}")

    elif args.command == 'info':
        print(f"\n⚙️  Configuration\n")
        print(f"   Provider: {PROVIDER}")
        print(f"   Model: {EMBEDDING_MODEL}")
        print(f"   API Key Env: {API_KEY_ENV}")
        print(f"   DB Path: {CHROMA_PATH}")
        key_set = "✓ Set" if os.environ.get(API_KEY_ENV) else "✗ Not set"
        print(f"   API Key: {key_set}")

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

Make it executable:
```bash
chmod +x ~/.claude/scripts/semantic_rag_api.py
```

## Step 4: Set Up API Key

```bash
# For OpenAI
export OPENAI_API_KEY="sk-your-key-here"

# For Voyage AI
export VOYAGE_API_KEY="your-key-here"

# For Cohere
export COHERE_API_KEY="your-key-here"

# Add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
```

## Step 5: Usage

Same commands as local version:

```bash
# Add knowledge
python ~/.claude/scripts/semantic_rag_api.py add \
  "lesson:auth:001" \
  "Always use httpOnly cookies for refresh tokens"

# Search
python ~/.claude/scripts/semantic_rag_api.py search "secure authentication"

# Check cost before bulk import
python ~/.claude/scripts/semantic_rag_api.py cost "your long text here"

# Show current configuration
python ~/.claude/scripts/semantic_rag_api.py info
```

---

# Integration with Current System

## Hybrid Workflow

Use both systems together:

```
┌─────────────────────────────────────────────────────────┐
│                    Hybrid System                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  MCP Memory (Current)          Semantic RAG (New)       │
│  ┌─────────────────┐          ┌─────────────────┐      │
│  │ Quick access    │          │ Discovery       │      │
│  │ Exact matches   │          │ Similar items   │      │
│  │ Entity names    │          │ Natural queries │      │
│  └────────┬────────┘          └────────┬────────┘      │
│           │                            │                │
│           ▼                            ▼                │
│  "project:MyApp:lesson:001"    "auth security best"    │
│  (I know what I want)          (Find me similar)       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## When to Use Which

| Scenario | Use |
|----------|-----|
| Know exact entity name | MCP Memory |
| Looking for "something like..." | Semantic RAG |
| Cross-project discovery | Semantic RAG |
| Quick context load | MCP Memory |
| "Find similar bugs" | Semantic RAG |
| Project-specific state | MCP Memory |

## Sync Between Systems

Export from MCP and import to Semantic:

```bash
# Export MCP memory to JSON
mcp-cli call memory/read_graph '{}' > mcp_export.json

# Import to semantic RAG
python ~/.claude/scripts/semantic_rag.py import mcp_export.json
```

---

# Cost Analysis

## Real-World Example

**Scenario:** 500 lessons/decisions across 10 projects

| Operation | Tokens | OpenAI Small | Voyage Lite | Local |
|-----------|--------|--------------|-------------|-------|
| Initial import | 250k | $0.005 | $0.005 | $0 |
| Daily searches (50) | 25k | $0.0005 | $0.0005 | $0 |
| Monthly total | ~1M | $0.02 | $0.02 | $0 |
| Yearly total | ~12M | $0.24 | $0.24 | $0 |

**Bottom line:** API embeddings cost about **$0.02/month** for typical usage.

## Break-Even Analysis

| Factor | Local | API |
|--------|-------|-----|
| Setup time | 30 mins | 5 mins |
| Maintenance | Updates needed | None |
| Quality | Good | Excellent |
| Privacy | 100% local | Data sent to API |
| Cost | $0 | ~$0.02/month |

**Choose Local if:** Privacy critical, offline needed, or zero cost required
**Choose API if:** Simplicity preferred, best quality wanted

---

# Troubleshooting

## Local (Ollama)

**"Ollama not running"**
```bash
ollama serve  # Start in separate terminal
```

**"Model not found"**
```bash
ollama pull nomic-embed-text
```

**"Slow embeddings"**
- Use smaller model (`all-minilm`)
- Check available RAM
- Consider API option instead

## API

**"API key not found"**
```bash
export OPENAI_API_KEY="your-key"
python script.py info  # Verify
```

**"Rate limited"**
- Add delays between requests
- Use batch operations
- Consider different provider

**"Cost concerns"**
```bash
python script.py cost "your text"  # Estimate before bulk operations
```

---

# Summary

| Aspect | Local (Ollama) | API (OpenAI/etc) |
|--------|----------------|------------------|
| Cost | Free | ~$0.02/month |
| Setup | Medium | Easy |
| Quality | Good | Excellent |
| Speed | Fast | Fast + latency |
| Privacy | 100% local | Data sent externally |
| Offline | Yes | No |
| Maintenance | Some | None |

**Recommendation:**
- Start with **API** for simplicity
- Switch to **Local** if privacy/cost matters
- Both integrate with your current MCP system

---

**Semantic search finds what you forgot you knew.**
