[English](../README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | **[中文](./README.zh.md)**

# GitHub Extractor Skill for Claude Code

> **零LLM token消耗。零幻觉。100%确定性。**
>
> 从GitHub仓库提取raw链接和下载文件，无需完整克隆。
>
> **🚀 将raw链接导入[NotebookLM](https://notebooklm.google.com)，从任何GitHub仓库构建属于你自己的[Deep Wiki](https://deepwiki.com)。**

---

## 功能

| 输入 | → | 输出 | 用途 |
|------|---|------|------|
| **GitHub特定文件夹** | → | Raw URL列表 | 导入NotebookLM、LLM |
| **GitHub特定文件夹** | → | 文件下载 | 部分克隆（无需整个仓库） |

---

## 安装

### 快速安装（推荐）

```bash
curl -sL https://raw.githubusercontent.com/professional-ALFIE/github-extractor/master/install.sh | bash
```

技能和脚本将安装到 `~/.claude/skills/github-extractor/`。

---

## 脚本

### 1. extractor_githubRawLinks.py

提取GitHub特定路径下的raw URL列表。

**为什么不用`git clone`？** 只需要一个文件夹，没必要下载500MB的整个仓库。

```bash
./extractor_githubRawLinks.py https://github.com/owner/repo/tree/main/docs
```

**输出：**
```
https://raw.githubusercontent.com/owner/repo/main/docs/guide.md
https://raw.githubusercontent.com/owner/repo/main/docs/api.md
```

- 自动复制到剪贴板（macOS）
- 支持任何分支、标签或提交

**依赖：** Python 3 + `requests`

> **提示：** 设置`GITHUB_TOKEN`可提高速率限制（60 → 5000请求/小时）

---

### 2. extractor_githubRawFiles.py

仅下载GitHub特定目录的文件 — 无需完整克隆。

```bash
./extractor_githubRawFiles.py https://github.com/owner/repo/tree/main/docs ./local-docs
```

**自动忽略：** `node_modules/`, `.git/`, `__pycache__/`, `dist/`, `build/`, `.next/`, `venv/`, `.pyc`, `.exe`, `.dll`, `.so`

**依赖：** Python 3 + `requests`

> **提示：** 设置`GITHUB_TOKEN`可提高速率限制（60 → 5000请求/小时）

---

## 配合Claude Code使用

安装技能后，直接询问：

- "获取 https://github.com/owner/repo/tree/main/docs 的raw链接"
- "下载 https://github.com/owner/repo/tree/main/src 的文件"

---

## 许可证

MIT
