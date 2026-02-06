#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True
import os
import sys
import requests
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple


def function_get_github_headers() -> Dict[str, str]:
    # Setting GITHUB_TOKEN increases GitHub API rate limits, which makes recursive traversal more reliable.
    variable_token = os.environ.get("GITHUB_TOKEN")  # string | None
    if not variable_token:
        return {}
    return {"Authorization": f"Bearer {variable_token}"}


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


def function_github_get_json(
    variable_url: str,
    variable_headers: Dict[str, str],
    variable_params: Optional[Dict[str, str]] = None,
) -> Tuple[Optional[Any], int]:
    variable_response = requests.get(variable_url, headers=variable_headers, params=variable_params)
    if variable_response.status_code == 200:
        return variable_response.json(), 200
    if variable_response.status_code == 404:
        return None, 404

    try:
        variable_message = variable_response.json().get("message", "Unknown error")
    except Exception:
        variable_message = variable_response.text.strip() or "Unknown error"
    raise ValueError(f"Error accessing GitHub API: {variable_message}")


def function_get_default_branch(variable_owner: str, variable_repo: str, variable_headers: Dict[str, str]) -> str:
    variable_repo_url = f"https://api.github.com/repos/{variable_owner}/{variable_repo}"
    variable_json, variable_status = function_github_get_json(variable_repo_url, variable_headers)
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


def function_contents_exists(
    variable_owner: str,
    variable_repo: str,
    variable_ref: str,
    variable_path: str,
    variable_headers: Dict[str, str],
) -> bool:
    variable_api_url = function_build_contents_api_url(variable_owner, variable_repo, variable_path)
    _, variable_status = function_github_get_json(variable_api_url, variable_headers, {"ref": variable_ref})
    return variable_status == 200


def function_resolve_ref_and_path_from_segments(
    variable_owner: str,
    variable_repo: str,
    variable_segments: List[str],
    variable_headers: Dict[str, str],
) -> Tuple[str, str]:
    # GitHub web URL format doesn't delimit ref vs path when ref contains '/',
    # so we try the longest possible ref first and shrink until Contents API resolves.
    for variable_i in range(len(variable_segments), 0, -1):
        variable_ref = "/".join(variable_segments[:variable_i])
        variable_path = "/".join(variable_segments[variable_i:])
        if function_contents_exists(variable_owner, variable_repo, variable_ref, variable_path, variable_headers):
            return variable_ref, variable_path

    raise ValueError("Could not resolve branch/tag/commit and path from the given URL.")


def function_parse_github_target(
    variable_github_url: str, variable_headers: Dict[str, str]
) -> Tuple[str, str, str, str]:
    variable_owner, variable_repo, variable_suffix = function_extract_owner_repo_and_suffix(variable_github_url)
    variable_suffix = variable_suffix.lstrip("/")
    variable_segments = [variable_segment for variable_segment in variable_suffix.split("/") if variable_segment]

    if not variable_segments:
        variable_ref = function_get_default_branch(variable_owner, variable_repo, variable_headers)
        return variable_owner, variable_repo, variable_ref, ""

    if variable_segments[0] in ("tree", "blob"):
        if len(variable_segments) < 2:
            raise ValueError("Invalid GitHub URL: missing branch/tag/commit after /tree/ or /blob/.")
        variable_candidate_segments = variable_segments[1:]
        variable_ref, variable_path = function_resolve_ref_and_path_from_segments(
            variable_owner, variable_repo, variable_candidate_segments, variable_headers
        )
        return variable_owner, variable_repo, variable_ref, variable_path

    # If it's not a /tree/ or /blob/ URL (issues, pulls, etc.), treat as repo root.
    variable_ref = function_get_default_branch(variable_owner, variable_repo, variable_headers)
    return variable_owner, variable_repo, variable_ref, ""


def function_build_raw_url(variable_owner: str, variable_repo: str, variable_ref: str, variable_path: str) -> str:
    return f"https://raw.githubusercontent.com/{variable_owner}/{variable_repo}/{variable_ref}/{variable_path}"


def function_copy_to_clipboard(variable_text: str) -> bool:
    # Prints to stdout AND also copies to the clipboard via pbcopy.
    try:
        subprocess.run(["pbcopy"], input=variable_text.encode("utf-8"), check=True)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


def function_collect_raw_urls(
    variable_owner: str,
    variable_repo: str,
    variable_ref: str,
    variable_path: str,
    variable_headers: Dict[str, str],
) -> List[str]:
    variable_api_url = function_build_contents_api_url(variable_owner, variable_repo, variable_path)
    variable_json, variable_status = function_github_get_json(variable_api_url, variable_headers, {"ref": variable_ref})
    if variable_status != 200:
        raise ValueError("Failed to fetch contents.")

    variable_urls: List[str] = []

    if isinstance(variable_json, list):
        for variable_item in variable_json:
            if not isinstance(variable_item, dict):
                continue
            variable_item_type = variable_item.get("type")
            variable_item_path = variable_item.get("path")
            if not isinstance(variable_item_type, str) or not isinstance(variable_item_path, str):
                continue

            if variable_item_type == "dir":
                variable_urls.extend(
                    function_collect_raw_urls(
                        variable_owner, variable_repo, variable_ref, variable_item_path, variable_headers
                    )
                )
                continue

            if variable_item_type in ("file", "symlink") and variable_item_path:
                variable_urls.append(function_build_raw_url(variable_owner, variable_repo, variable_ref, variable_item_path))

        return variable_urls

    if isinstance(variable_json, dict):
        variable_item_type = variable_json.get("type")
        variable_item_path = variable_json.get("path")
        if variable_item_type in ("file", "symlink") and isinstance(variable_item_path, str) and variable_item_path:
            return [function_build_raw_url(variable_owner, variable_repo, variable_ref, variable_item_path)]
        if variable_item_type == "dir" and isinstance(variable_item_path, str):
            return function_collect_raw_urls(variable_owner, variable_repo, variable_ref, variable_item_path, variable_headers)
        raise ValueError("The given URL does not point to a file or directory.")

    raise ValueError("Unexpected GitHub API response.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 raw_link_extractor.py <github_repo_url>")
        sys.exit(1)

    variable_github_url = sys.argv[1]
    try:
        variable_headers = function_get_github_headers()
        variable_owner, variable_repo, variable_ref, variable_path = function_parse_github_target(
            variable_github_url, variable_headers
        )
        variable_raw_urls = function_collect_raw_urls(
            variable_owner, variable_repo, variable_ref, variable_path, variable_headers
        )
        variable_output_text = "\n".join(variable_raw_urls) + ("\n" if variable_raw_urls else "")  # string
        for variable_url in variable_raw_urls:
            print(variable_url)

        # Prints to stdout AND also copies to the clipboard via pbcopy.
        variable_copied = function_copy_to_clipboard(variable_output_text)
        if variable_copied:
            variable_color_green = "\033[92m"  # string
            variable_color_reset = "\033[0m"  # string
            print(f"{variable_color_green}Copied to your clipboard.{variable_color_reset}")
        else:
            print("Warning: pbcopy not found or failed; clipboard copy skipped.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
