"""Script to update the Google Material Design Icons font in the static folder."""

import logging
from pathlib import Path

import requests

FONT_URL = "https://github.com/google/material-design-icons/raw/refs/heads/master/variablefont/MaterialSymbolsOutlined%5BFILL,GRAD,opsz,wght%5D.woff2"
LOCAL_PATH = Path(__file__).parent.parent / "src/vizro/static/css/fonts/material-symbols-outlined.woff2"
STATUS_OK = 200
TIMEOUT = 10  # seconds

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def download_font(url, path):
    """Downloads the Material Design Icons font from Google Fonts and saves it to the local static folder."""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == STATUS_OK:
            path.write_bytes(response.content)
            logger.info(f"✍️ Material font downloaded and saved to {path}")
        else:
            logger.error(f"❌ Failed to download Material font. Status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"❌ Failed to download Material font due to an unexpected error: {e}")


if __name__ == "__main__":
    download_font(FONT_URL, LOCAL_PATH)
