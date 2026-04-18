# GitHub Extractor Skill for Claude Code

> **Zero LLM tokens. Zero hallucination. 100% Deterministic.**
>
> Extract raw links and download files from GitHub repositories without full cloning.

---

## What It Does

| Input | → | Output | Use Case |
|-------|---|--------|----------|
| **GitHub specific folder** | → | Raw URL list | Feed to NotebookLM, LLMs |
| **GitHub specific folder** | → | Downloaded files | Partial clone (skip the whole repo) |

---

## Installation

### For Claude Code Users

```bash
npx ai-agent-skills install professional-ALFIE/extractor-skill
```

Or manually copy the skill folder to `~/.claude/skills/extractor-skill/`.

### Standalone Usage

```bash
git clone https://github.com/professional-ALFIE/extractor-skill.git
cd extractor-skill/scripts

# Run directly (shebang included)
./extractor_githubRawLinks.py <GITHUB_URL>
./extractor_githubRawFiles.py <GITHUB_URL> [OUTPUT_DIR]
```

---

## Scripts

### 1. extractor_githubRawLinks.py

Get raw URLs for files in a specific GitHub path.

**Why not `git clone`?** You only need one folder, not 500MB of repo.

```bash
./extractor_githubRawLinks.py https://github.com/owner/repo/tree/main/docs
```

**Output:**
```
https://raw.githubusercontent.com/owner/repo/main/docs/guide.md
https://raw.githubusercontent.com/owner/repo/main/docs/api.md
```

- Auto-copied to clipboard (macOS)
- Supports any branch, tag, or commit

**Requirements:** Python 3 + `requests`

> **Tip:** Set `GITHUB_TOKEN` to increase rate limit (60 → 5000 req/hour)

---

### 2. extractor_githubRawFiles.py

Download files from a specific GitHub directory — skip the full clone.

```bash
./extractor_githubRawFiles.py https://github.com/owner/repo/tree/main/docs ./local-docs
```

**Auto-ignores:** `node_modules/`, `.git/`, `__pycache__/`, `dist/`, `build/`, `.next/`, `venv/`, `.pyc`, `.exe`, `.dll`, `.so`

**Requirements:** Python 3 + `requests`

> **Tip:** Set `GITHUB_TOKEN` to increase rate limit (60 → 5000 req/hour)

---

## Use with Claude Code

Once installed, just ask:

- "Get raw links for https://github.com/owner/repo/tree/main/docs"
- "Download files from https://github.com/owner/repo/tree/main/src"

---

## License

MIT
