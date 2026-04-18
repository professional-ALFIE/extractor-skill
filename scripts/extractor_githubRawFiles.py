#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True

import requests 
import os
import sys
import re
from typing import Any, Dict, List, Optional, Set, Tuple

COLOR_RED = "\033[91m"  # string
COLOR_YELLOW = "\033[93m"  # string
COLOR_GREEN = "\033[92m"  # string
COLOR_RESET = "\033[0m"  # string

download_path = os.getcwd()  # 다운로드 파일이 저장될 기본 경로(현재 작업 디렉터리)
HEADERS = None  # GitHub API 요청에 사용할 헤더(GITHUB_TOKEN이 있으면 Authorization 포함)

token = os.environ.get("GITHUB_TOKEN")  # string | None
if token:
    HEADERS = {"Authorization": "Bearer " + token}


def function_style_heading(variable_text: str) -> str:
    variable_bold_underline = "\033[1m\033[4m"  # string
    variable_reset = "\033[0m"  # string
    return f"{variable_bold_underline}{variable_text}{variable_reset}"


def function_print_usage() -> None:
    print(f"{function_style_heading('Usage:')} python3 downgit.py [GITHUB_URL] [IGNORE...]")
    print("")
    print(function_style_heading("Arguments:"))
    print("  GITHUB_URL    GitHub URL to download (file or directory)")
    print(
        '  IGNORE       [optional] Exclude paths, GitHub URLs, or extensions (e.g. ".ts"). '
        "You can pass multiple IGNORE arguments."
    )


def function_print_no_url_error_and_usage() -> None:
    # Only the "error" word is red (the rest is default color).
    print(f"{COLOR_RED}error{COLOR_RESET}: No GITHUB_URL provided. Either specify one as an argument.")
    print("")
    function_print_usage()


def function_github_get_json(
    variable_url: str,
    variable_params: Optional[Dict[str, str]] = None,
) -> Tuple[Optional[Any], int]:
    try:
        variable_response = requests.get(variable_url, headers=HEADERS, params=variable_params)
    except Exception:
        print(COLOR_RED + "Could not connect to GitHub. Please check your internet connection" + COLOR_RESET)
        sys.exit(0)

    if variable_response.status_code == 200:
        return variable_response.json(), 200
    if variable_response.status_code == 404:
        return None, 404

    try:
        variable_message = variable_response.json().get("message", "Unknown error")
    except Exception:
        variable_message = variable_response.text.strip() or "Unknown error"
    raise ValueError(variable_message)


def function_extract_owner_repo_and_suffix(variable_github_url: str) -> Tuple[str, str, str]:
    # Supports:
    # - https://github.com/OWNER/REPO/...
    # - git@github.com:OWNER/REPO.git
    variable_base_pattern = r"github\.com[:/]([\w-]+)/([\w.-]+?)(?:\.git)?(?:(/.*))?$"
    variable_base_match = re.search(variable_base_pattern, variable_github_url)
    if not variable_base_match:
        raise ValueError("Invalid GitHub URL provided.")

    variable_owner, variable_repo, variable_suffix = variable_base_match.groups()
    return variable_owner, variable_repo, (variable_suffix or "")


def function_get_default_branch(variable_owner: str, variable_repo: str) -> str:
    variable_repo_url = f"https://api.github.com/repos/{variable_owner}/{variable_repo}"
    variable_json, variable_status = function_github_get_json(variable_repo_url)
    if variable_status != 200 or not isinstance(variable_json, dict):
        raise ValueError("Failed to fetch repository info.")
    variable_default_branch = variable_json.get("default_branch")
    if not isinstance(variable_default_branch, str) or not variable_default_branch:
        raise ValueError("Failed to detect default branch.")
    return variable_default_branch


def function_build_contents_api_url(variable_owner: str, variable_repo: str, variable_path: str) -> str:
    variable_base = f"https://api.github.com/repos/{variable_owner}/{variable_repo}/contents"
    if not variable_path:
        return variable_base
    return f"{variable_base}/{variable_path}"


def function_contents_exists(variable_owner: str, variable_repo: str, variable_ref: str, variable_path: str) -> bool:
    variable_api_url = function_build_contents_api_url(variable_owner, variable_repo, variable_path)
    _, variable_status = function_github_get_json(variable_api_url, {"ref": variable_ref})
    return variable_status == 200


def function_resolve_ref_and_path_from_segments(
    variable_owner: str,
    variable_repo: str,
    variable_segments: List[str],
) -> Tuple[str, str]:
    # Fast path: most branches/tags don't contain '/'
    variable_ref = variable_segments[0]
    variable_path = "/".join(variable_segments[1:])
    if function_contents_exists(variable_owner, variable_repo, variable_ref, variable_path):
        return variable_ref, variable_path

    # Fallback: try the longest possible ref first and shrink until Contents API resolves.
    for variable_i in range(len(variable_segments), 0, -1):
        variable_ref = "/".join(variable_segments[:variable_i])
        variable_path = "/".join(variable_segments[variable_i:])
        if function_contents_exists(variable_owner, variable_repo, variable_ref, variable_path):
            return variable_ref, variable_path

    raise ValueError("Could not resolve branch/tag/commit and path from the given URL.")


def function_parse_github_target(variable_github_url: str) -> Tuple[str, str, str, str]:
    variable_owner, variable_repo, variable_suffix = function_extract_owner_repo_and_suffix(variable_github_url)
    variable_suffix = variable_suffix.lstrip("/")
    variable_segments = [variable_segment for variable_segment in variable_suffix.split("/") if variable_segment]

    if not variable_segments:
        variable_ref = function_get_default_branch(variable_owner, variable_repo)
        return variable_owner, variable_repo, variable_ref, ""

    if variable_segments[0] in ("tree", "blob"):
        if len(variable_segments) < 2:
            raise ValueError("Invalid GitHub URL: missing branch/tag/commit after /tree/ or /blob/.")
        variable_candidate_segments = variable_segments[1:]
        variable_ref, variable_path = function_resolve_ref_and_path_from_segments(
            variable_owner, variable_repo, variable_candidate_segments
        )
        return variable_owner, variable_repo, variable_ref, variable_path

    # If it's not a /tree/ or /blob/ URL (issues, pulls, etc.), treat as repo root.
    variable_ref = function_get_default_branch(variable_owner, variable_repo)
    return variable_owner, variable_repo, variable_ref, ""


def function_flatten_ignore_args(variable_ignore_args: List[str]) -> List[str]:
    variable_tokens: List[str] = []
    for variable_arg in variable_ignore_args:
        if variable_arg is None:
            continue
        for variable_part in variable_arg.split(";"):
            variable_part = variable_part.strip()
            if variable_part:
                variable_tokens.append(variable_part)
    return variable_tokens


def function_is_github_url(variable_text: str) -> bool:
    return variable_text.startswith("http://") or variable_text.startswith("https://") or variable_text.startswith("git@")


def function_is_extension_token(variable_text: str) -> bool:
    return variable_text.startswith(".") and ("/" not in variable_text) and ("://" not in variable_text)


def function_normalize_repo_path(variable_path: str) -> str:
    variable_path = variable_path.strip()
    variable_path = variable_path.lstrip("/")
    variable_path = variable_path.rstrip("/")
    return variable_path


def function_parse_ignore_config(
    variable_owner: str,
    variable_repo: str,
    variable_ignore_args: List[str],
) -> Tuple[Set[str], Set[str]]:
    variable_ignore_paths: Set[str] = set()
    variable_ignore_extensions: Set[str] = set()

    for variable_token in function_flatten_ignore_args(variable_ignore_args):
        if function_is_github_url(variable_token) and "github.com" in variable_token:
            variable_ignore_owner, variable_ignore_repo, _, variable_ignore_path = function_parse_github_target(variable_token)
            if variable_ignore_owner != variable_owner or variable_ignore_repo != variable_repo:
                raise ValueError("IGNORE URL must point to the same repository as GITHUB_URL.")
            variable_ignore_path = function_normalize_repo_path(variable_ignore_path)
            if not variable_ignore_path:
                raise ValueError("IGNORE URL points to the repository root; refusing to ignore everything.")
            variable_ignore_paths.add(variable_ignore_path)
            continue

        if function_is_extension_token(variable_token):
            variable_ignore_extensions.add(variable_token)
            continue

        variable_path = function_normalize_repo_path(variable_token)
        if variable_path:
            variable_ignore_paths.add(variable_path)

    return variable_ignore_paths, variable_ignore_extensions


def function_should_ignore_path(variable_repo_path: str, variable_ignore_paths: Set[str]) -> bool:
    for variable_prefix in variable_ignore_paths:
        if variable_repo_path == variable_prefix:
            return True
        if variable_repo_path.startswith(variable_prefix + "/"):
            return True
    return False


def function_should_ignore_extension(variable_repo_path: str, variable_ignore_extensions: Set[str]) -> bool:
    for variable_extension in variable_ignore_extensions:
        if variable_repo_path.endswith(variable_extension):
            return True
    return False



def download_file(url, file_path, size=0):
    save_path = os.path.join(download_path, file_path)
    # check if file already exists
    if os.path.exists(save_path):
        if size == os.path.getsize(save_path):
            print(f"{COLOR_GREEN}File {COLOR_RESET}{file_path}{COLOR_GREEN} already exists{COLOR_RESET}")
            return

    # DOWNLOAD FILE
    print(f"{COLOR_GREEN}Downloading {COLOR_RESET}{file_path}...")
    # get file
    r = requests.get(url, headers=HEADERS, stream=True)


    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    if r.status_code == 200:
        with open(save_path, 'wb') as f:
            for data in r.iter_content(chunk_size=1024):
                f.write(data)
        if size != 0 and os.path.getsize(save_path) != size:
            print(COLOR_RED + "ERROR, something went wrong" + COLOR_RESET)
    else:
        print(f"{COLOR_RED}Failed to download {file_path}. Status code: {r.status_code}{COLOR_RESET}")

def get_content(
    url: str,
    ref: str,
    base_path: str,
    ignore_paths: Set[str],
    ignore_extensions: Set[str],
) -> None:
    try:
        content, status = function_github_get_json(url, {"ref": ref})
        if status != 200:
            raise ValueError("Not found")
    except Exception:
        print(COLOR_YELLOW + "Please provide a valid url" + COLOR_RESET)
        sys.exit(0)

    # if content is list(multiple files)
    try:
        if isinstance(content, list):
            for i in content:
                if not isinstance(i, dict):
                    continue

                item_type = i.get("type")
                item_path = i.get("path")
                if not isinstance(item_type, str) or not isinstance(item_path, str):
                    continue

                if function_should_ignore_path(item_path, ignore_paths):
                    continue

                if item_type == "dir":
                    get_content(i["url"], ref, base_path, ignore_paths, ignore_extensions)
                    continue

                if function_should_ignore_extension(item_path, ignore_extensions):
                    continue

                path = item_path
                if base_path:
                    base_prefix = base_path.rstrip("/") + "/"
                    if path.startswith(base_prefix):
                        path = path[len(base_prefix):]

                size = i.get("size", 0)
                url = i.get("download_url")
                if not isinstance(url, str) or not url:
                    continue
                download_file(url, path, size)

        # if content is dict(single file)
        elif isinstance(content, dict):
            item_type = content.get("type")
            item_path = content.get("path")
            if not isinstance(item_type, str) or not isinstance(item_path, str):
                raise ValueError("Unexpected content response")

            if function_should_ignore_path(item_path, ignore_paths):
                return
            if function_should_ignore_extension(item_path, ignore_extensions):
                return

            path = os.path.basename(item_path)
            size = content.get("size", 0)
            url = content.get("download_url")
            if not isinstance(url, str) or not url:
                raise ValueError("Missing download_url")
            download_file(url, path, size)
    except Exception:
        try:
            print(COLOR_RED + "Error occured:" + content["message"] + COLOR_RESET)
        except Exception:
            print(COLOR_RED + "An unknown error occured" + COLOR_RESET)
        
        print(COLOR_YELLOW + "Possible solution:" + COLOR_RESET)
        print(COLOR_YELLOW + "1. Set GITHUB_TOKEN environment variable to increase GitHub API rate limits" + COLOR_RESET)
        print(COLOR_YELLOW + "2. Wait for 60 minutes and try again (unauthenticated rate limit is ~60 requests per hour)" + COLOR_RESET)
        sys.exit(0)

def main():
    global download_path

    if len(sys.argv) < 2:
        function_print_no_url_error_and_usage()
        sys.exit(1)

    github_url_var = sys.argv[1]

    # 두 번째 인자가 있고 --ignore로 시작하지 않으면 출력 디렉토리로 처리
    if len(sys.argv) >= 3 and not sys.argv[2].startswith('--ignore'):
        download_path = os.path.abspath(sys.argv[2])
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        ignore_args_var = sys.argv[3:]
    else:
        ignore_args_var = sys.argv[2:]

    try:
        owner_var, repo_var, ref_var, path_var = function_parse_github_target(github_url_var)
        ignore_paths_var, ignore_extensions_var = function_parse_ignore_config(owner_var, repo_var, ignore_args_var)
        api_url_var = function_build_contents_api_url(owner_var, repo_var, path_var)

        # 대상이 디렉토리인지 먼저 확인
        content_var, status_var = function_github_get_json(api_url_var, {"ref": ref_var})
        if status_var != 200:
            raise ValueError("Target not found")

        is_directory_var = isinstance(content_var, list)  # bool

        if is_directory_var:
            # 폴더인 경우: 폴더명으로 하위 디렉토리 생성
            folder_name_var = os.path.basename(path_var) if path_var else repo_var  # string
            download_path = os.path.join(download_path, folder_name_var)
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            print(f"{COLOR_GREEN}Downloading to {COLOR_RESET}{folder_name_var}/")

        get_content(api_url_var, ref_var, path_var, ignore_paths_var, ignore_extensions_var)
        print(COLOR_GREEN + "Download complete" + COLOR_RESET)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    
