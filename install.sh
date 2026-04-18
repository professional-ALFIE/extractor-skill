#!/bin/bash
set -e

SKILL_NAME="github-extractor"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
REPO="professional-ALFIE/github-extractor"
BRANCH="master"
BASE_URL="https://raw.githubusercontent.com/$REPO/$BRANCH"

# ── Force clean install (always inject latest version) ──
if [ -d "$SKILL_DIR" ]; then
  echo "Existing installation found. Replacing with latest version..."
  rm -rf "$SKILL_DIR"
fi

echo "Installing $SKILL_NAME skill..."

mkdir -p "$SKILL_DIR/scripts"

# Core skill file
curl -sL "$BASE_URL/SKILL.md" -o "$SKILL_DIR/SKILL.md"

# Scripts
curl -sL "$BASE_URL/scripts/extractor_githubRawLinks.py" -o "$SKILL_DIR/scripts/extractor_githubRawLinks.py"
curl -sL "$BASE_URL/scripts/extractor_githubRawFiles.py" -o "$SKILL_DIR/scripts/extractor_githubRawFiles.py"

# Metadata
cat > "$SKILL_DIR/.skill-meta.json" << EOF
{
  "source": "github",
  "repo": "$REPO",
  "isRootSkill": true,
  "installedAt": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
  "updatedAt": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"
}
EOF

# Make scripts executable
chmod +x "$SKILL_DIR/scripts/"*

# Verify
if [ -f "$SKILL_DIR/SKILL.md" ] && [ -f "$SKILL_DIR/scripts/extractor_githubRawLinks.py" ]; then
  echo ""
  echo "✓ Installed to: $SKILL_DIR"
  echo "  Files:"
  ls -1 "$SKILL_DIR" "$SKILL_DIR/scripts/" | sed 's/^/    /'
  echo ""
  echo "Done! Restart Claude Code to activate."
else
  echo "✗ Installation failed. Check network and try again." >&2
  exit 1
fi
