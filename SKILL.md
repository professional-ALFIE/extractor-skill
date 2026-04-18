---
name: github-extractor
description: Use this skill whenever the user wants raw file URLs from a GitHub repository or wants to download files from a specific GitHub repo or folder without cloning the whole repository. Trigger on requests like "raw link", "raw URL", "raw 링크", "GitHub 파일 다운로드", "레포 파일 받아줘", "이 GitHub 폴더만 받아줘", or when the user shares a GitHub repo/tree URL and wants local files or raw links instead of a full git clone.
---

# GitHub Extractor
Extract download files or raw links from GitHub repositories and folders.
All scripts are in this skill's `scripts/` directory. Run them directly — shebang handles the runtime.

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| `extractor_githubRawLinks.py` | GitHub URL → raw link list | python3 (shebang) |
| `extractor_githubRawFiles.py` | GitHub URL → file download | python3 (shebang) |

## 1. GitHub File Download
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

## Dependencies
**extractor_githubRaw*.py:**
- python3
- requests (`pip install requests`)
