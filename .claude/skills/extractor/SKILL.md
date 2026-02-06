---
name: extractor
description: This skill should be used when the user asks to "마크다운으로 변환", "markdown으로", "URL to markdown", "웹페이지 마크다운", "rawlink", "raw link", "raw 링크", "GitHub 파일 다운로드", "레포 파일 받아줘", "raw파일 다운로드". Provides web content extraction (HTML to Markdown with images) and GitHub file operations (raw links, file downloads).
---

# Extractor

Extract and convert web content and GitHub files.

All scripts are in this skill's `scripts/` directory. Run them directly — shebang handles the runtime.

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| `extractor_htmlToMarkdown.ts` | Webpage → Markdown + images | bun (shebang) |
| `extractor_githubRawLinks.py` | GitHub URL → raw link list | python3 (shebang) |
| `extractor_githubRawFiles.py` | GitHub URL → file download | python3 (shebang) |

## 1. Webpage to Markdown

Convert any webpage to clean markdown with images.

```bash
# Default (auto filename + image download)
./scripts/extractor_htmlToMarkdown.ts <URL>

# Specify output filename
./scripts/extractor_htmlToMarkdown.ts <URL> -o output.md

# stdout only (no image download)
./scripts/extractor_htmlToMarkdown.ts <URL> -s
```

**Output:**
- `{title}.md` - Markdown file
- `{title}_images/` - Image folder (when images exist)

**Features:**
- Readability.js extracts main content (removes ads/navigation)
- Turndown converts HTML to Markdown
- highlight.js auto-detects code language
- Images auto-download with local path conversion

## 2. GitHub Raw Links

Get raw URLs for all files in a GitHub repository or directory.

```bash
./scripts/extractor_githubRawLinks.py <GitHub URL>
```

**Input examples:**
- `https://github.com/owner/repo`
- `https://github.com/owner/repo/tree/main/src`

**Output:**
- Raw URL list to stdout
- Auto-copy to clipboard (pbcopy)

## 3. GitHub File Download

Download files from a specific GitHub directory — no full clone needed.

```bash
./scripts/extractor_githubRawFiles.py <GitHub URL> [output_dir]
```

**Options:**
- `output_dir`: Save directory (default: current folder)
- `GITHUB_TOKEN` env var: Increase rate limit (60 → 5000 req/hour)

**Default ignore patterns:**
- Paths: `node_modules/`, `.git/`, `__pycache__/`, `dist/`, `build/`
- Extensions: `.pyc`, `.pyo`, `.exe`, `.dll`, `.so`

## Dependencies

**extractor_htmlToMarkdown.ts:**
- Requires bun runtime
- Auto-installs packages on first run (@mozilla/readability, jsdom, turndown, highlight.js)

**extractor_githubRaw*.py:**
- python3
- requests (`pip install requests`)
