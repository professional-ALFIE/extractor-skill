# Extractor Skill for Claude Code

> **Zero LLM tokens. Zero hallucination. 100% Deterministic.**

## Why Not Just Use AI to Fetch and Convert?

When you ask an LLM to "convert this webpage to markdown":
1. **Token consumption x2** — AI fetches the page, then AI rewrites it
2. **Content drift** — Each AI pass can subtly alter meaning
3. **Slow** — Multiple API roundtrips
4. **Inconsistent** — Different results every time

**This skill runs scripts directly.** No AI processing. No token consumption.

Same result every time. No alterations. **Exact original!**

Your agent delegates the grunt work to deterministic scripts and gets back to thinking.


*Your Claude Code agent will love this. Less busywork, more brainwork.*
***Minimal context pollution.***

---

## What It Does

| Input | → | Output | Use Case |
|-------|---|--------|----------|
| **Any webpage URL** | → | Markdown + images | Save articles, documentation |
| **GitHub specific folder** | → | Raw URL list | Feed to NotebookLM, LLMs |
| **GitHub specific folder** | → | Downloaded files | Partial clone (skip the whole repo) |

---

## Installation

### One-liner

```bash
curl -sL https://raw.githubusercontent.com/professional-ALFIE/extractor-skill/master/install.sh | bash
```

### Manual

```bash
git clone https://github.com/professional-ALFIE/extractor-skill.git
cp -a extractor-skill/.claude/skills/extractor ~/.claude/skills/
```

### Standalone Usage

```bash
# After install, scripts are at ~/.claude/skills/extractor/scripts/
./extractor_htmlToMarkdown.ts <URL>
./extractor_githubRawLinks.py <GITHUB_URL>
./extractor_githubRawFiles.py <GITHUB_URL> [OUTPUT_DIR]
```

---

## Scripts

### 1. extractor_htmlToMarkdown.ts

Convert any webpage to clean Markdown with images.

```bash
./extractor_htmlToMarkdown.ts --help
./extractor_htmlToMarkdown.ts https://example.com/article
./extractor_htmlToMarkdown.ts https://example.com/article -o article.md
./extractor_htmlToMarkdown.ts https://example.com/article -s  # stdout only
```

| Flag | Description |
|------|-------------|
| `-o, --output <file>` | Save to specified file |
| `-s, --stdout` | Print to terminal (no file/images saved) |
| `-h, --help` | Show help |
| `-v, --version` | Show version |

**Output:**
```
Article-Title.md
Article-Title_images/
├── image1.png
└── ...
```

**Under the hood:** Readability.js (content extraction) + Turndown (HTML→MD) + highlight.js (code language detection)

**Requirements:** [bun](https://bun.sh) — dependencies auto-install on first run

---

### 2. extractor_githubRawLinks.py

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

### 3. extractor_githubRawFiles.py

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

- "Convert this URL to markdown: https://example.com"
- "Get raw links for https://github.com/owner/repo/tree/main/docs"
- "Download files from https://github.com/owner/repo/tree/main/src"

---

## License

MIT
