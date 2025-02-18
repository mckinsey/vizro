"""Script to update the static files that come from other libraries."""
# ruff: noqa: T201

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import requests

from vizro import VIZRO_ASSETS_PATH

TIMEOUT = 10  # seconds


@dataclass
class StaticFileConfig:
    """Configuration to fetch a static file.

    Args:
        source_url: URL to look at initially. This is not the file that we want in the repo but will contain a link
            to the file that we want.
        pattern: regex pattern to search for inside source_url file. This should return a match called
            `url_to_download`, which points to the actual file that we want to put in our repo.
        destination: path to download `url_to_download` file to.
        headers: optional argument for headers to pass with the initial request to source_url.
    """

    source_url: str
    pattern: str
    destination: Path
    headers: dict[str, str] = field(default_factory=dict)


def fetch_extracted_url(source_url: str, pattern: str, headers: dict[str, str]) -> bytes:
    """Look at the file at source_url, search for pattern and then download `url_to_download`."""
    response = requests.get(source_url, timeout=TIMEOUT, headers=headers)
    response.raise_for_status()

    match = re.search(pattern, response.text)
    if not match:
        sys.exit(f"Could not extract URL to download from {source_url}.")

    url_to_download = match["url_to_download"]
    print(f"Fetching {url_to_download}...")
    response = requests.get(url_to_download, timeout=TIMEOUT)
    response.raise_for_status()

    return response.content


# The Google fonts API returns different CSS depending on the user agent. If we don't manually specify a user agent then
# it will point us to a ttf rather than woff2 file. So we take a user agent from https://www.useragents.me/ to fake
# being a real Chrome browser so we get the woff2 file.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3"
)

static_file_configs = [
    StaticFileConfig(
        source_url="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
        pattern=r"src: url\((?P<url_to_download>.+)\) format\('woff2'\)",
        destination=VIZRO_ASSETS_PATH / "css/fonts/material-symbols-outlined.woff2",
        headers={"user-agent": USER_AGENT},
    ),
    StaticFileConfig(
        source_url="https://raw.githubusercontent.com/snehilvj/dash-mantine-components/refs/heads/master/dash_mantine_components/styles.py",
        pattern=r'DATES = "(?P<url_to_download>.+)"',
        destination=VIZRO_ASSETS_PATH / "css/mantine_dates.css",
    ),
]


for static_file_config in static_file_configs:
    static_file_config.destination.write_bytes(
        fetch_extracted_url(static_file_config.source_url, static_file_config.pattern, static_file_config.headers)
    )
