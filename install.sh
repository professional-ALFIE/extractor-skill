#!/bin/bash
set -e

SKILL_DIR="$HOME/.claude/skills/extractor"
REPO="professional-ALFIE/extractor-skill"
BRANCH="master"
BASE_URL="https://raw.githubusercontent.com/$REPO/$BRANCH/.claude/skills/extractor"

echo "Installing extractor skill..."

mkdir -p "$SKILL_DIR/scripts"

curl -sL "$BASE_URL/SKILL.md" -o "$SKILL_DIR/SKILL.md"
curl -sL "$BASE_URL/scripts/extractor_htmlToMarkdown.ts" -o "$SKILL_DIR/scripts/extractor_htmlToMarkdown.ts"
curl -sL "$BASE_URL/scripts/extractor_githubRawLinks.py" -o "$SKILL_DIR/scripts/extractor_githubRawLinks.py"
curl -sL "$BASE_URL/scripts/extractor_githubRawFiles.py" -o "$SKILL_DIR/scripts/extractor_githubRawFiles.py"

chmod +x "$SKILL_DIR/scripts/"*

echo ""
echo "Installed to: $SKILL_DIR"
echo "Done!"
