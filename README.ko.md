# Extractor Skill for Claude Code

> **LLM 토큰 소모? 없어요. AI 할루시네이션? 없어요. Markdown 변환 시 변형도? 없어요.**
>
> **100% 결정적.**

## AI한테 시키면 되는 거 아닌가요?!

LLM한테 "이 웹페이지 마크다운으로 변환해줘"라고 하면:
1. **토큰 2배** — AI가 페이지 읽고, AI가 다시 씀
2. **내용 변형** — AI가 처리할 때마다 조금씩 바뀔 수 있음
3. **느림** — API 왕복 여러 번
4. **일관성 없음** — 매번 결과가 다름

**이 스킬은 스크립트를 직접 실행합니다.** AI 처리 없고, 토큰 소모 없어요.

매번 똑같은 결과. 변형도 없습니다. **원본 그대로!**

에이전트는 단순 작업을 스크립트한테 맡기고 진짜 생각해야 할 일에 집중할 수 있죠.


*Claude Code 에이전트도 좋아합니다. 허드렛일 줄이고, 머리 쓸 일에 집중하죠.*
***컨텍스트 오염이 적습니다.***

---

## 뭘 하는 건가요?

| 입력 | → | 출력 | 용도 |
|------|---|------|------|
| **아무 웹페이지 URL** | → | 마크다운 + 이미지 | 아티클, 문서 저장 |
| **GitHub 특정 폴더** | → | Raw URL 목록 | NotebookLM, LLM에 먹이기 |
| **GitHub 특정 폴더** | → | 파일 다운로드 | 부분 클론 (전체 레포 필요 없음) |

---

## 설치

### 원라이너

```bash
curl -sL https://raw.githubusercontent.com/professional-ALFIE/extractor-skill/master/install.sh | bash
```

### 수동 설치

```bash
git clone https://github.com/professional-ALFIE/extractor-skill.git
cp -a extractor-skill/.claude/skills/extractor ~/.claude/skills/
```

### 단독 사용

```bash
# 설치 후 스크립트 위치: ~/.claude/skills/extractor/scripts/
./extractor_htmlToMarkdown.ts <URL>
./extractor_githubRawLinks.py <GITHUB_URL>
./extractor_githubRawFiles.py <GITHUB_URL> [출력_디렉토리]
```

---

## 스크립트

### 1. extractor_htmlToMarkdown.ts

웹페이지를 깔끔한 마크다운 + 이미지로 변환해요.

```bash
./extractor_htmlToMarkdown.ts --help
./extractor_htmlToMarkdown.ts https://example.com/article
./extractor_htmlToMarkdown.ts https://example.com/article -o article.md
./extractor_htmlToMarkdown.ts https://example.com/article -s  # stdout만
```

| 플래그 | 설명 |
|--------|------|
| `-o, --output <파일>` | 지정한 파일에 저장 |
| `-s, --stdout` | 터미널에 출력 (파일/이미지 저장 안 함) |
| `-h, --help` | 도움말 |
| `-v, --version` | 버전 |

**출력:**
```
글-제목.md
글-제목_images/
├── image1.png
└── ...
```

**내부 동작:** Readability.js (본문 추출) + Turndown (HTML→MD) + highlight.js (코드 언어 감지)

**요구사항:** [bun](https://bun.sh) — 첫 실행 시 의존성 자동 설치돼요!

---

### 2. extractor_githubRawLinks.py

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

### 3. extractor_githubRawFiles.py

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

- "이 URL 마크다운으로 변환해줘: https://example.com"
- "https://github.com/owner/repo/tree/main/docs 의 raw 링크 줘"
- "https://github.com/owner/repo/tree/main/src 파일 다운받아줘"

---

## 라이선스

MIT
