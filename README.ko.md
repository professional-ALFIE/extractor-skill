# GitHub Extractor Skill for Claude Code

> **LLM 토큰 소모? 없어요. AI 할루시네이션? 없어요. 100% 결정적.**
>
> GitHub 레포에서 raw 링크 추출 및 파일 다운로드. 전체 클론 없이.

---

## 뭘 하는 건가요?

| 입력 | → | 출력 | 용도 |
|------|---|------|------|
| **GitHub 특정 폴더** | → | Raw URL 목록 | NotebookLM, LLM에 먹이기 |
| **GitHub 특정 폴더** | → | 파일 다운로드 | 부분 클론 (전체 레포 필요 없음) |

---

## 설치

### 빠른 설치 (권장)

```bash
curl -sL https://raw.githubusercontent.com/professional-ALFIE/github-extractor/master/install.sh | bash
```

`~/.claude/skills/github-extractor/`에 스킬과 스크립트가 설치됩니다.

---

## 스크립트

### 1. extractor_githubRawLinks.py

GitHub 특정 경로의 raw URL 목록을 추출해요.

**왜 `git clone` 안 쓰나요?** 폴더 하나만 필요한데 500MB 레포 전체를 받을 이유가 없잖아요.

```bash
./extractor_githubRawLinks.py https://github.com/owner/repo/tree/main/docs
```

**출력:**
```
https://raw.githubusercontent.com/owner/repo/main/docs/guide.md
https://raw.githubusercontent.com/owner/repo/main/docs/api.md
```

- 클립보드에 자동 복사돼요 (macOS)
- 모든 브랜치, 태그, 커밋 지원

**요구사항:** Python 3 + `requests`

> **팁:** `GITHUB_TOKEN` 설정하면 rate limit이 증가됩니다! (60 → 5000 요청/시간)

---

### 2. extractor_githubRawFiles.py

GitHub 특정 디렉토리의 파일만 다운로드해요 — 이제 전체 클론 안 해도 되죠.

```bash
./extractor_githubRawFiles.py https://github.com/owner/repo/tree/main/docs ./local-docs
```

**자동 무시:** `node_modules/`, `.git/`, `__pycache__/`, `dist/`, `build/`, `.next/`, `venv/`, `.pyc`, `.exe`, `.dll`, `.so`

**요구사항:** Python 3 + `requests`

> **팁:** `GITHUB_TOKEN` 설정하면 rate limit이 증가됩니다! (60 → 5000 요청/시간)

---

## Claude Code랑 같이 쓰기

스킬 설치 후 그냥 요청하세요:

- "https://github.com/owner/repo/tree/main/docs 의 raw 링크 줘"
- "https://github.com/owner/repo/tree/main/src 파일 다운받아줘"

---

## 라이선스

MIT
