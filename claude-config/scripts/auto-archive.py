#!/usr/bin/env python3
"""
Auto-Archive: Automatic context compression and RAG archiving for Claude Code

This script:
1. Monitors context usage
2. Extracts key information from conversation
3. Archives to MCP Memory and/or local files
4. Helps maintain 20-40% free space

Usage:
  python auto-archive.py check          # Check current context level
  python auto-archive.py archive        # Archive current session
  python auto-archive.py auto           # Auto-archive if > threshold
  python auto-archive.py summary        # Generate summary only (no save)
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration
CONTEXT_THRESHOLD = 60  # Archive when context exceeds this %
TARGET_FREE_SPACE = 30  # Target free space after archive (%)
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
ARCHIVE_DIR = Path(".claude")

def get_current_project_dir() -> Optional[Path]:
    """Find the current project's Claude session directory."""
    cwd = Path.cwd()
    # Convert path to Claude's format
    project_key = str(cwd).replace("/", "-").replace(" ", "-")
    if project_key.startswith("-"):
        project_key = project_key[1:]

    project_dir = CLAUDE_PROJECTS_DIR / project_key
    if project_dir.exists():
        return project_dir

    # Try variations
    for d in CLAUDE_PROJECTS_DIR.iterdir():
        if d.is_dir() and cwd.name.lower() in d.name.lower():
            return d

    return None

def get_latest_session(project_dir: Path) -> Optional[Path]:
    """Get the most recent session file."""
    sessions = list(project_dir.glob("*.jsonl"))
    if not sessions:
        return None
    return max(sessions, key=lambda p: p.stat().st_mtime)

def estimate_context_usage() -> Dict[str, Any]:
    """Estimate current context usage from session file."""
    project_dir = get_current_project_dir()
    if not project_dir:
        return {"error": "Could not find project directory"}

    session_file = get_latest_session(project_dir)
    if not session_file:
        return {"error": "Could not find session file"}

    # Count tokens (rough estimate: 4 chars = 1 token)
    file_size = session_file.stat().st_size
    estimated_tokens = file_size // 4

    # Claude's context is ~200k tokens
    max_tokens = 200000
    usage_percent = (estimated_tokens / max_tokens) * 100

    return {
        "session_file": str(session_file),
        "file_size_kb": file_size // 1024,
        "estimated_tokens": estimated_tokens,
        "usage_percent": round(usage_percent, 1),
        "free_percent": round(100 - usage_percent, 1),
        "threshold": CONTEXT_THRESHOLD,
        "needs_archive": usage_percent > CONTEXT_THRESHOLD
    }

def extract_key_content(session_file: Path, max_messages: int = 50) -> Dict[str, Any]:
    """Extract key decisions, lessons, and context from session."""
    content = {
        "decisions": [],
        "lessons": [],
        "tasks_completed": [],
        "current_state": "",
        "key_files": [],
        "timestamp": datetime.now().isoformat()
    }

    try:
        with open(session_file, 'r') as f:
            messages = []
            for line in f:
                try:
                    msg = json.loads(line)
                    if msg.get("type") in ["user", "assistant"]:
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue

            # Get last N messages
            recent = messages[-max_messages:] if len(messages) > max_messages else messages

            # Extract patterns
            for msg in recent:
                message_content = msg.get("message", {}).get("content", "")
                if isinstance(message_content, str):
                    text = message_content.lower()

                    # Look for decisions
                    if "decided" in text or "chose" in text or "decision:" in text:
                        content["decisions"].append(message_content[:200])

                    # Look for lessons
                    if "learned" in text or "lesson:" in text or "realized" in text:
                        content["lessons"].append(message_content[:200])

                    # Look for completed tasks
                    if "completed" in text or "done" in text or "finished" in text:
                        content["tasks_completed"].append(message_content[:100])

            # Get summary from last assistant message
            for msg in reversed(recent):
                if msg.get("type") == "assistant":
                    msg_content = msg.get("message", {}).get("content", "")
                    if isinstance(msg_content, str) and len(msg_content) > 50:
                        content["current_state"] = msg_content[:500]
                        break

    except Exception as e:
        content["error"] = str(e)

    return content

def save_to_mcp(content: Dict[str, Any], project_name: str) -> bool:
    """Save extracted content to MCP Memory."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")

    entities = []

    # Create session entity
    session_entity = {
        "name": f"session:{project_name}:{timestamp}",
        "entityType": "session",
        "observations": [
            f"Archived: {content['timestamp']}",
            f"State: {content['current_state'][:200]}" if content['current_state'] else "State: Working session"
        ]
    }

    # Add decisions
    for i, decision in enumerate(content['decisions'][:5]):
        session_entity["observations"].append(f"Decision: {decision[:100]}")

    # Add lessons
    for lesson in content['lessons'][:3]:
        session_entity["observations"].append(f"Lesson: {lesson[:100]}")

    entities.append(session_entity)

    # Call MCP
    try:
        cmd = [
            "mcp-cli", "call", "memory/create_entities",
            json.dumps({"entities": entities})
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"MCP save failed: {e}")
        return False

def save_to_file(content: Dict[str, Any], project_name: str) -> Path:
    """Save extracted content to local archive file."""
    archive_dir = ARCHIVE_DIR / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"session-{timestamp}.md"
    filepath = archive_dir / filename

    md_content = f"""# Session Archive: {timestamp}

**Project:** {project_name}
**Archived:** {content['timestamp']}

## Current State
{content['current_state'] or 'No state captured'}

## Decisions Made
"""

    for decision in content['decisions']:
        md_content += f"- {decision[:150]}...\n"

    if not content['decisions']:
        md_content += "- No decisions captured\n"

    md_content += "\n## Lessons Learned\n"
    for lesson in content['lessons']:
        md_content += f"- {lesson[:150]}...\n"

    if not content['lessons']:
        md_content += "- No lessons captured\n"

    md_content += "\n## Tasks Completed\n"
    for task in content['tasks_completed'][:10]:
        md_content += f"- {task[:100]}\n"

    if not content['tasks_completed']:
        md_content += "- No tasks captured\n"

    md_content += f"""
---
*Auto-archived by efficient-context-RAG*
"""

    filepath.write_text(md_content)
    return filepath

def update_messages_md(content: Dict[str, Any]) -> Path:
    """Update or create .claude/messages.md with compressed context."""
    messages_file = ARCHIVE_DIR / "messages.md"
    ARCHIVE_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Create header if file doesn't exist
    if not messages_file.exists():
        header = """# Compressed Message History

> Auto-archived conversation context for RAG retrieval.
> This file is updated automatically when context exceeds threshold.

---

"""
        messages_file.write_text(header)

    # Append new archive
    new_content = f"""
## Archive: {timestamp}

### State
{content['current_state'][:300] if content['current_state'] else 'Working session'}

### Key Points
"""

    for decision in content['decisions'][:3]:
        new_content += f"- Decision: {decision[:100]}\n"

    for lesson in content['lessons'][:2]:
        new_content += f"- Lesson: {lesson[:100]}\n"

    new_content += "\n---\n"

    # Append to file
    with open(messages_file, 'a') as f:
        f.write(new_content)

    return messages_file

def check_context():
    """Check current context usage."""
    usage = estimate_context_usage()

    if "error" in usage:
        print(f"❌ Error: {usage['error']}")
        return

    # Visual bar
    filled = int(usage['usage_percent'] / 5)
    empty = 20 - filled
    bar = "█" * filled + "░" * empty

    status = "🟢 Good" if usage['usage_percent'] < 50 else \
             "🟡 Monitor" if usage['usage_percent'] < CONTEXT_THRESHOLD else \
             "🔴 Archive Now!"

    print(f"""
╔══════════════════════════════════════════════════════════╗
║                  Context Usage Check                      ║
╠══════════════════════════════════════════════════════════╣
║                                                           ║
║  [{bar}] {usage['usage_percent']}%              ║
║                                                           ║
║  Estimated tokens: {usage['estimated_tokens']:,}                          ║
║  Free space: {usage['free_percent']}%                                      ║
║  Threshold: {CONTEXT_THRESHOLD}%                                         ║
║                                                           ║
║  Status: {status}                                    ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
""")

    if usage['needs_archive']:
        print("💡 Run: python auto-archive.py archive")

def archive_session(dry_run: bool = False):
    """Archive current session to MCP and files."""
    print("📦 Archiving session...\n")

    # Get project info
    project_name = Path.cwd().name
    project_dir = get_current_project_dir()

    if not project_dir:
        print("❌ Could not find project directory")
        return

    session_file = get_latest_session(project_dir)
    if not session_file:
        print("❌ Could not find session file")
        return

    print(f"   Project: {project_name}")
    print(f"   Session: {session_file.name}")

    # Extract content
    print("\n📝 Extracting key content...")
    content = extract_key_content(session_file)

    if dry_run:
        print("\n📋 Summary (dry run - not saving):")
        print(f"   Decisions: {len(content['decisions'])}")
        print(f"   Lessons: {len(content['lessons'])}")
        print(f"   Tasks: {len(content['tasks_completed'])}")
        print(f"\n   Current state preview:")
        print(f"   {content['current_state'][:200]}...")
        return

    # Save to MCP
    print("\n💾 Saving to MCP Memory...")
    mcp_success = save_to_mcp(content, project_name)
    if mcp_success:
        print("   ✓ Saved to MCP")
    else:
        print("   ⚠ MCP save failed (server may not be running)")

    # Save to files
    print("\n📁 Saving to local files...")

    archive_file = save_to_file(content, project_name)
    print(f"   ✓ Archive: {archive_file}")

    messages_file = update_messages_md(content)
    print(f"   ✓ Messages: {messages_file}")

    print(f"""
╔══════════════════════════════════════════════════════════╗
║                  ✓ Archive Complete                       ║
╠══════════════════════════════════════════════════════════╣
║                                                           ║
║  Saved to:                                                ║
║  • MCP Memory: session:{project_name}:*           ║
║  • {archive_file}                      ║
║  • {messages_file}                             ║
║                                                           ║
║  Next: Run /compact in Claude to free context space      ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
""")

def auto_archive():
    """Automatically archive if context exceeds threshold."""
    usage = estimate_context_usage()

    if "error" in usage:
        print(f"❌ Error: {usage['error']}")
        return

    if usage['needs_archive']:
        print(f"⚠️  Context at {usage['usage_percent']}% (threshold: {CONTEXT_THRESHOLD}%)")
        print("   Auto-archiving...\n")
        archive_session()
    else:
        print(f"✓ Context at {usage['usage_percent']}% - no archive needed")

def main():
    parser = argparse.ArgumentParser(
        description='Auto-archive context for Claude Code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto-archive.py check           # Check context level
  python auto-archive.py archive         # Archive now
  python auto-archive.py archive --dry   # Preview without saving
  python auto-archive.py auto            # Archive only if needed
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Check command
    subparsers.add_parser('check', help='Check current context usage')

    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive current session')
    archive_parser.add_argument('--dry', action='store_true', help='Dry run (preview only)')

    # Auto command
    subparsers.add_parser('auto', help='Auto-archive if threshold exceeded')

    # Summary command
    subparsers.add_parser('summary', help='Generate summary only')

    args = parser.parse_args()

    if args.command == 'check':
        check_context()
    elif args.command == 'archive':
        archive_session(dry_run=args.dry if hasattr(args, 'dry') else False)
    elif args.command == 'auto':
        auto_archive()
    elif args.command == 'summary':
        archive_session(dry_run=True)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
