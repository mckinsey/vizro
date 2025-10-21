"""Checks vizro docs links availability in mcp prompts for the latest vizro version."""

import re
import sys
from pathlib import Path

import requests
import vizro

# Regex to find any http/https URLs in text
URL_PATTERN = re.compile(r'https?://[^\s\'"<>]+')


def replace_part_in_url(url):
    """Replace the {vizro.__version__} placeholder with the real version."""
    return url.replace("{vizro.__version__}", vizro.__version__)


def check_url_availability(url):
    """Check if URL is reachable (status code < 400)."""
    status_code = 400
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code < status_code
    except requests.RequestException:
        return False


def process_python_files():
    """Links parsing and checking logic."""
    all_urls = []
    failed_urls = []

    for file_path in Path(".").rglob("prompts.py"):
        text = file_path.read_text(encoding="utf-8")

        # Extract URLs
        urls = URL_PATTERN.findall(text)
        if not urls:
            continue

        all_urls.extend(urls)
        new_text = text

        for url in urls:
            # Replace placeholder
            new_url = replace_part_in_url(url)
            new_text = new_text.replace(url, new_url)

            # Check availability
            is_ok = check_url_availability(new_url)
            print(f"Checking {new_url} -> {'✅ OK' if is_ok else '❌ FAILED'}")  # noqa

            if not is_ok:
                failed_urls.append(new_url)

    # Exit with error if any link is broken
    if failed_urls:
        print("\n❌ Some URLs are unavailable:")  # noqa
        for bad in failed_urls:
            print(f"  - {bad}")  # noqa
        sys.exit(1)  # non-zero exit code for CI/CD or shell failure
    else:
        print("\n✅ All URLs are available.")  # noqa


if __name__ == "__main__":
    process_python_files()
