#!/bin/bash
# Claude Project Initializer
# Usage: init-project.sh [project_path] [project_name]

set -e

PROJECT_PATH="${1:-.}"
PROJECT_NAME="${2:-$(basename "$PROJECT_PATH")}"
TEMPLATE_PATH="$HOME/.claude/templates/workspace"
TARGET_PATH="$PROJECT_PATH/.claude"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE=$(date '+%Y-%m-%d')

echo "Initializing Claude project context..."
echo "   Project: $PROJECT_NAME"
echo "   Path: $PROJECT_PATH"

# Check if .claude already exists
if [ -d "$TARGET_PATH" ]; then
    echo "Warning: .claude folder already exists at $TARGET_PATH"
    read -p "   Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    rm -rf "$TARGET_PATH"
fi

# Create directory structure
mkdir -p "$TARGET_PATH/contracts"
mkdir -p "$TARGET_PATH/handoffs"
mkdir -p "$TARGET_PATH/logs"

# Copy and customize templates
for file in status.md progress.md todo-list.md context.md improvements.md; do
    if [ -f "$TEMPLATE_PATH/$file" ]; then
        sed -e "s/{PROJECT_NAME}/$PROJECT_NAME/g" \
            -e "s/{TIMESTAMP}/$TIMESTAMP/g" \
            -e "s/{DATE}/$DATE/g" \
            -e "s/{MILESTONE_NAME}/Initial Setup/g" \
            "$TEMPLATE_PATH/$file" > "$TARGET_PATH/$file"
    fi
done

# Copy contracts
if [ -f "$TEMPLATE_PATH/contracts/api.md" ]; then
    cp "$TEMPLATE_PATH/contracts/api.md" "$TARGET_PATH/contracts/"
fi
if [ -f "$TEMPLATE_PATH/contracts/types.md" ]; then
    cp "$TEMPLATE_PATH/contracts/types.md" "$TARGET_PATH/contracts/"
fi

# Copy logs
if [ -f "$TEMPLATE_PATH/logs/agent-log.md" ]; then
    sed "s/{TIMESTAMP}/$TIMESTAMP/g" "$TEMPLATE_PATH/logs/agent-log.md" > "$TARGET_PATH/logs/agent-log.md"
fi

# Create .gitkeep for handoffs
echo "# Handoff files go here" > "$TARGET_PATH/handoffs/.gitkeep"

# Add to .gitignore if it exists
if [ -f "$PROJECT_PATH/.gitignore" ]; then
    if ! grep -q "^\.claude/logs/" "$PROJECT_PATH/.gitignore"; then
        echo "" >> "$PROJECT_PATH/.gitignore"
        echo "# Claude agent logs (optional - can exclude)" >> "$PROJECT_PATH/.gitignore"
        echo ".claude/logs/" >> "$PROJECT_PATH/.gitignore"
    fi
fi

echo "Project initialized!"
echo ""
echo "Created structure:"
echo "   $TARGET_PATH/"
echo "   ├── status.md"
echo "   ├── progress.md"
echo "   ├── todo-list.md"
echo "   ├── context.md"
echo "   ├── improvements.md"
echo "   ├── contracts/"
echo "   │   ├── api.md"
echo "   │   └── types.md"
echo "   ├── handoffs/"
echo "   └── logs/"
echo "       └── agent-log.md"
echo ""
echo "Next: Update context.md with project-specific info"
