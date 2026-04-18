[English](../README.md) | [한국어](./README.ko.md) | **[日本語](./README.ja.md)** | [中文](./README.zh.md)

# GitHub Extractor Skill for Claude Code / Codex CLI / Gemini CLI

> AIエージェントにオープンソース分析を頼む？ 500MBのリポ全体を`/tmp`にクローン。もう一度頼む？ またクローン…トークンも時間も無駄。ウェブ検索で分析させる？ 実際のコードを読むより精度は低く、ハルシネーションは多く、トークン消費もさらに多い。
>
> **もうその必要はありません。** 必要なフォルダだけダウンロードするか、rawリンクだけ抽出して直接使えます。
>
> **🚀 rawリンクを[NotebookLM](https://notebooklm.google.com)に入れれば、どんなGitHubリポからでも自分だけの[Deep Wiki](https://deepwiki.com)が作れます。**

---

## 何ができる？

| 入力 | → | 出力 | ユースケース |
|------|---|------|------------|
| **GitHub特定フォルダ** | → | Raw URLリスト | NotebookLM、LLMへ投入 |
| **GitHub特定フォルダ** | → | ファイルダウンロード | 部分クローン（リポ全体不要） |

---

## インストール

### クイックインストール（推奨）

```bash
curl -sL https://raw.githubusercontent.com/professional-ALFIE/github-extractor/master/install.sh | bash
```

`~/.claude/skills/github-extractor/`にスキルとスクリプトがインストールされます。

---

## スクリプト

### 1. extractor_githubRawLinks.py

GitHub特定パスのraw URLリストを抽出します。

**なぜ`git clone`を使わない？** フォルダ1つだけ必要なのに、500MBのリポ全体をダウンロードする必要はありません。

```bash
./extractor_githubRawLinks.py https://github.com/owner/repo/tree/main/docs
```

**出力:**
```
https://raw.githubusercontent.com/owner/repo/main/docs/guide.md
https://raw.githubusercontent.com/owner/repo/main/docs/api.md
```

- クリップボードに自動コピー（macOS）
- あらゆるブランチ、タグ、コミットに対応

**要件:** Python 3 + `requests`

> **ヒント:** `GITHUB_TOKEN`を設定するとレートリミットが増加します！（60 → 5000リクエスト/時間）

---

### 2. extractor_githubRawFiles.py

GitHub特定ディレクトリのファイルのみダウンロード — フルクローン不要。

```bash
./extractor_githubRawFiles.py https://github.com/owner/repo/tree/main/docs ./local-docs
```

**自動除外:** `node_modules/`, `.git/`, `__pycache__/`, `dist/`, `build/`, `.next/`, `venv/`, `.pyc`, `.exe`, `.dll`, `.so`

**要件:** Python 3 + `requests`

> **ヒント:** `GITHUB_TOKEN`を設定するとレートリミットが増加します！（60 → 5000リクエスト/時間）

---

## Claude Codeと一緒に使う

スキルをインストールしたら、こう聞くだけ：

- 「https://github.com/owner/repo/tree/main/docs のrawリンクを取得して」
- 「https://github.com/owner/repo/tree/main/src のファイルをダウンロードして」

---

## ライセンス

MIT
