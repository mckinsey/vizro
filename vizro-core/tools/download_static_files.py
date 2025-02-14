"""Script to update the Google Material Design Icons font in the static folder."""


import sys
from dataclasses import dataclass
from pathlib import Path
import re

import requests

from vizro import VIZRO_ASSETS_PATH

TIMEOUT = 10  # seconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3"
# HERE HERE HERE
#
# comment: taken from https://www.useragents.me/
# update comment in figures.css and matnein_dates.css
# check hatch.toml and github script
# run it once per week

@dataclass
class StaticFileConfig:
    source_url: str
    pattern: str
    destination: Path

def fetch_extracted_url(source_url: str, pattern: str) -> bytes:
    response = requests.get(source_url, timeout=TIMEOUT, headers={"user-agent": USER_AGENT})
    response.raise_for_status()

    match = re.search(pattern, response.text)
    if not match:
        sys.exit(f"Could not extract URL to download from {source_url}.")

    url_to_download = match["url_to_download"]
    print(f"Fetching {url_to_download}...")
    response = requests.get(url_to_download, timeout=TIMEOUT)
    response.raise_for_status()

    return response.content


static_file_configs = [StaticFileConfig(
    source_url="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
    pattern=r"src: url\((?P<url_to_download>.+)\) format\('woff2'\)",
    destination=VIZRO_ASSETS_PATH / "css/fonts/material-symbols-outlined.woff2"),
StaticFileConfig(
    source_url="https://raw.githubusercontent.com/snehilvj/dash-mantine-components/refs/heads/master/dash_mantine_components/styles.py",
    pattern=r'DATES = "(?P<url_to_download>.+)"',
    destination=VIZRO_ASSETS_PATH / "css/mantine_dates.css")
]


for static_file_config in static_file_configs:
    static_file_config.destination.write_bytes(fetch_extracted_url(static_file_config.source_url,
                                                              static_file_config.pattern))
