"""Downloads the Material Design Icons font from Google Fonts and saves it to the local static folder."""

from pathlib import Path

import requests

FONT_URL = "https://github.com/google/material-design-icons/raw/refs/heads/master/variablefont/MaterialSymbolsOutlined%5BFILL,GRAD,opsz,wght%5D.woff2"
LOCAL_PATH = Path(__file__).parent.parent / "src/vizro/static/css/fonts/material-symbols-outlined.woff2"


def download_font(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        path.write_bytes(response.content)
        print(f"✍️ Material font downloaded and saved to {path}")
    else:
        print(f"❌ Failed to download Material font. Status code: {response.status_code}")


if __name__ == "__main__":
    download_font(FONT_URL, LOCAL_PATH)
