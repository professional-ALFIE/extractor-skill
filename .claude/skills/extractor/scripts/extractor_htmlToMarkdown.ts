#!/usr/bin/env bun

/**
 * extractor_htmlToMarkdown.ts - URL을 마크다운으로 변환하는 CLI 도구
 *
 * 사용법:
 *   ./extractor_htmlToMarkdown.ts <URL>                    자동 파일명으로 저장
 *   ./extractor_htmlToMarkdown.ts <URL> -o <파일명>         지정한 파일명으로 저장
 *   ./extractor_htmlToMarkdown.ts <URL> -s                 터미널에 출력
 *
 * 의존성 (bun이 자동 설치):
 *   - @mozilla/readability: 본문 추출
 *   - jsdom: DOM 파싱
 *   - turndown: HTML → Markdown 변환
 *   - turndown-plugin-gfm: GFM 지원 (테이블, 취소선 등)
 *   - highlight.js: 코드 언어 자동 감지
 */

import { Readability } from "@mozilla/readability";
import { JSDOM } from "jsdom";
import TurndownService from "turndown";
import { gfm } from "turndown-plugin-gfm";
import hljs from "highlight.js";
import { mkdir, writeFile } from "fs/promises";
import { basename, join, dirname } from "path";

// ─────────────────────────────────────────────────────────────
// Turndown 설정
// ─────────────────────────────────────────────────────────────

function create_turndown_service_func(image_folder_var: string | null) {
  const turndown_service_var = new TurndownService({
    headingStyle: "atx",           // # 스타일 헤딩
    codeBlockStyle: "fenced",      // ``` 코드 블록
    bulletListMarker: "-",         // 리스트 마커
  });

  // GFM 플러그인 (테이블, 취소선, 자동링크 등)
  turndown_service_var.use(gfm);

  // 불필요한 요소 제거
  turndown_service_var.remove(["script", "style", "noscript", "iframe", "nav", "footer", "aside"]);

  // 이미지 규칙: 로컬 경로로 변환
  if (image_folder_var) {
    turndown_service_var.addRule("images", {
      filter: "img",
      replacement: (content: string, node: any) => {
        const src_var = node.getAttribute("src") || "";
        const alt_var = node.getAttribute("alt") || "";

        if (!src_var) return "";

        // 이미지 파일명 추출
        const url_obj_var = new URL(src_var, "https://example.com");
        let filename_var = basename(url_obj_var.pathname) || "image";

        // 확장자가 없으면 .png 추가
        if (!filename_var.includes(".")) {
          filename_var += ".png";
        }

        // 로컬 경로로 변환
        const local_path_var = `./${basename(image_folder_var)}/${filename_var}`;
        return `![${alt_var}](${local_path_var})`;
      },
    });
  }

  // 코드 블록 언어 자동 감지
  turndown_service_var.addRule("codeBlock", {
    filter: (node: any) => {
      return (
        node.nodeName === "PRE" &&
        node.firstChild &&
        node.firstChild.nodeName === "CODE"
      );
    },
    replacement: (content: string, node: any) => {
      const code_node_var = node.firstChild;
      const code_text_var = code_node_var.textContent || "";

      // 기존 언어 클래스 확인
      let language_var = "";
      const class_match_var = code_node_var.className?.match(/language-(\w+)/);
      if (class_match_var) {
        language_var = class_match_var[1];
      } else {
        // highlight.js로 자동 감지
        try {
          const result_var = hljs.highlightAuto(code_text_var);
          language_var = result_var.language || "";
        } catch {
          language_var = "";
        }
      }

      return `\n\n\`\`\`${language_var}\n${code_text_var.trim()}\n\`\`\`\n\n`;
    },
  });

  return turndown_service_var;
}

// ─────────────────────────────────────────────────────────────
// 이미지 다운로드
// ─────────────────────────────────────────────────────────────

async function download_images_func(
  html_var: string,
  base_url_var: string,
  image_folder_var: string
): Promise<void> {
  // 이미지 URL 추출
  const img_regex_var = /<img[^>]+src=["']([^"']+)["']/gi;
  const matches_var = [...html_var.matchAll(img_regex_var)];

  if (matches_var.length === 0) return;

  // 폴더 생성
  await mkdir(image_folder_var, { recursive: true });

  // 이미지 다운로드
  const download_promises_var = matches_var.map(async (match_var) => {
    let src_var = match_var[1];

    // 상대 경로를 절대 경로로 변환
    try {
      const url_obj_var = new URL(src_var, base_url_var);
      src_var = url_obj_var.href;
    } catch {
      return; // 잘못된 URL은 스킵
    }

    // data: URL은 스킵
    if (src_var.startsWith("data:")) return;

    // 파일명 추출
    const url_obj_var = new URL(src_var);
    let filename_var = basename(url_obj_var.pathname) || "image";

    // 확장자가 없으면 .png 추가
    if (!filename_var.includes(".")) {
      filename_var += ".png";
    }

    // 특수문자 제거
    filename_var = filename_var.replace(/[^a-zA-Z0-9._-]/g, "_");

    const filepath_var = join(image_folder_var, filename_var);

    try {
      const response_var = await fetch(src_var, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        },
      });

      if (!response_var.ok) return;

      const buffer_var = await response_var.arrayBuffer();
      await writeFile(filepath_var, Buffer.from(buffer_var));
      console.error(`  📷 ${filename_var}`);
    } catch {
      // 다운로드 실패는 조용히 스킵
    }
  });

  await Promise.all(download_promises_var);
}

// ─────────────────────────────────────────────────────────────
// 메인 변환 함수
// ─────────────────────────────────────────────────────────────

interface ConvertResult {
  markdown: string;
  title: string;
  html: string;
}

async function fetch_and_convert_func(
  url_var: string,
  image_folder_var: string | null
): Promise<ConvertResult> {
  // 1. HTML 가져오기
  const response_var = await fetch(url_var, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    },
  });

  if (!response_var.ok) {
    throw new Error(`HTTP ${response_var.status}: ${response_var.statusText}`);
  }

  const html_var = await response_var.text();

  // 2. JSDOM으로 파싱
  const dom_var = new JSDOM(html_var, { url: url_var });
  const document_var = dom_var.window.document;

  // 3. Readability로 본문 추출
  const reader_var = new Readability(document_var);
  const article_var = reader_var.parse();

  if (!article_var) {
    throw new Error("본문을 추출할 수 없습니다. Readability 파싱 실패.");
  }

  // 4. Turndown으로 마크다운 변환
  const turndown_service_var = create_turndown_service_func(image_folder_var);
  const markdown_var = turndown_service_var.turndown(article_var.content);

  // 5. 메타데이터 추가
  const title_var = article_var.title || "Untitled";
  const timestamp_var = new Date().toISOString();

  const output_var = `# ${title_var}

**Source:** ${url_var}
**Saved:** ${timestamp_var}

---

${markdown_var}
`;

  return {
    markdown: output_var,
    title: title_var,
    html: html_var,
  };
}

// ─────────────────────────────────────────────────────────────
// 파일명 생성
// ─────────────────────────────────────────────────────────────

function sanitize_filename_func(title_var: string): string {
  return title_var
    .replace(/[<>:"/\\|?*]/g, "")      // 금지 문자 제거
    .replace(/\s+/g, "-")               // 공백을 하이픈으로
    .replace(/-+/g, "-")                // 연속 하이픈 제거
    .replace(/^-|-$/g, "")              // 앞뒤 하이픈 제거
    .substring(0, 100);                 // 최대 100자
}

// ─────────────────────────────────────────────────────────────
// CLI 처리
// ─────────────────────────────────────────────────────────────

const HELP_TEXT = `
extractor_htmlToMarkdown.ts - URL을 마크다운으로 변환하는 CLI 도구

사용법:
  ./extractor_htmlToMarkdown.ts <URL>                    자동 파일명으로 저장 (기본)
  ./extractor_htmlToMarkdown.ts <URL> -o <파일명>         지정한 파일명으로 저장
  ./extractor_htmlToMarkdown.ts <URL> -s                 터미널에 출력 (stdout)

옵션:
  -o, --output <파일>   마크다운을 지정한 파일에 저장
  -s, --stdout          터미널에 출력 (파일 저장 안 함)
  -h, --help            이 도움말 출력
  -v, --version         버전 정보 출력

예시:
  ./extractor_htmlToMarkdown.ts https://example.com/article
  ./extractor_htmlToMarkdown.ts https://goddaehee.tistory.com/504 -o openclaw.md
  ./extractor_htmlToMarkdown.ts https://news.ycombinator.com -s > hn.md

출력 구조 (기본):
  {제목}.md
  {제목}_images/
    ├── image1.png
    ├── image2.jpg
    └── ...

의존성 (bun이 자동 설치):
  - @mozilla/readability   본문 추출 (광고/네비게이션 제거)
  - jsdom                  DOM 파싱
  - turndown               HTML → Markdown 변환
  - turndown-plugin-gfm    GFM 지원 (테이블, 취소선 등)
  - highlight.js           코드 언어 자동 감지
`;

const VERSION = "2.0.0";

async function main_func() {
  const args_var = process.argv.slice(2);  // $1, $2, ... = CLI 인자들

  // --help, -h 처리
  if (args_var.includes("--help") || args_var.includes("-h") || args_var.length === 0) {
    console.log(HELP_TEXT);
    process.exit(0);
  }

  // --version, -v 처리
  if (args_var.includes("--version") || args_var.includes("-v")) {
    console.log(`extractor_htmlToMarkdown.ts v${VERSION}`);
    process.exit(0);
  }

  const url_var = args_var[0];

  // URL 검증
  if (!url_var.startsWith("http://") && !url_var.startsWith("https://")) {
    console.error("❌ 유효한 URL을 입력해주세요 (http:// 또는 https://)");
    process.exit(1);
  }

  // -s, --stdout 옵션 처리
  const is_stdout_var = args_var.includes("-s") || args_var.includes("--stdout");

  // -o, --output 옵션 처리
  let output_index_var = args_var.indexOf("-o");
  if (output_index_var === -1) output_index_var = args_var.indexOf("--output");
  const specified_output_var = output_index_var !== -1 ? args_var[output_index_var + 1] : null;

  try {
    if (is_stdout_var) {
      // stdout 모드: 이미지 다운로드 안 함
      console.error("🔄 변환 중...");
      const result_var = await fetch_and_convert_func(url_var, null);
      console.log(result_var.markdown);
    } else {
      // 파일 저장 모드
      console.error("🔄 변환 중...");

      // 먼저 변환해서 제목 얻기
      const temp_result_var = await fetch_and_convert_func(url_var, null);
      const safe_title_var = sanitize_filename_func(temp_result_var.title);

      // 파일명 결정
      const md_filename_var = specified_output_var || `${safe_title_var}.md`;
      const base_name_var = md_filename_var.replace(/\.md$/, "");
      const image_folder_var = `${base_name_var}_images`;

      // 이미지 폴더와 함께 다시 변환
      const result_var = await fetch_and_convert_func(url_var, image_folder_var);

      // 이미지 다운로드
      console.error("📷 이미지 다운로드 중...");
      await download_images_func(result_var.html, url_var, image_folder_var);

      // 마크다운 저장
      await writeFile(md_filename_var, result_var.markdown);

      console.error(`✅ 저장 완료: ${md_filename_var}`);
    }
  } catch (error_var) {
    console.error(`❌ 오류: ${(error_var as Error).message}`);
    process.exit(1);
  }
}

main_func();
