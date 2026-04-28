"""File-upload chip renders through the real dcc.Upload pipeline (CSV + PNG)."""

import base64
from pathlib import Path

from playwright.sync_api import Page, expect

from vizro_experimental.chat._constants import (
    CSS_FILE_CHIP,
    CSS_FILE_CHIP_REMOVE,
    CSS_FILE_CHIP_SUBTITLE,
    CSS_FILE_CHIP_THUMB,
    CSS_FILE_CHIP_THUMB_ICON,
    CSS_FILE_CHIP_TITLE,
)

# Minimal 1x1 red PNG; decoded at test time so the fixture stays tracked as text.
_TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="


def _write_csv(dir: Path) -> Path:
    path = dir / "sample.csv"
    path.write_text("name,value\nalpha,1\nbeta,2\ngamma,3\n")
    return path


def _write_png(dir: Path) -> Path:
    path = dir / "tiny.png"
    path.write_bytes(base64.b64decode(_TINY_PNG_B64))
    return path


def test_csv_upload_renders_doc_chip_and_remove_deletes_it(page: Page, app_url: str, tmp_path: Path) -> None:
    csv = _write_csv(tmp_path)

    page.goto(app_url + "/examples--upload")
    expect(page.get_by_placeholder("Upload a file and ask questions...")).to_be_visible()

    page.set_input_files("input[type=file]", str(csv))

    chip = page.locator(f".{CSS_FILE_CHIP}")
    expect(chip).to_have_count(1)
    expect(chip.locator(f".{CSS_FILE_CHIP_TITLE}")).to_have_text("sample.csv")
    expect(chip.locator(f".{CSS_FILE_CHIP_SUBTITLE}")).to_contain_text("CSV")

    assert page.locator(f".{CSS_FILE_CHIP} img.{CSS_FILE_CHIP_THUMB}").count() == 0
    expect(chip.locator(f".{CSS_FILE_CHIP_THUMB}.{CSS_FILE_CHIP_THUMB_ICON}")).to_be_visible()

    expect(chip.locator(f".{CSS_FILE_CHIP_REMOVE}")).to_be_visible()
    chip.locator(f".{CSS_FILE_CHIP_REMOVE}").click()
    expect(page.locator(f".{CSS_FILE_CHIP}")).to_have_count(0)


def test_png_upload_renders_image_chip_with_img_thumbnail(page: Page, app_url: str, tmp_path: Path) -> None:
    png = _write_png(tmp_path)

    page.goto(app_url + "/examples--upload")
    expect(page.get_by_placeholder("Upload a file and ask questions...")).to_be_visible()

    page.set_input_files("input[type=file]", str(png))

    chip = page.locator(f".{CSS_FILE_CHIP}")
    expect(chip).to_have_count(1)
    expect(chip.locator(f".{CSS_FILE_CHIP_TITLE}")).to_have_text("tiny.png")
    expect(chip.locator(f".{CSS_FILE_CHIP_SUBTITLE}")).to_contain_text("PNG")

    img = chip.locator(f"img.{CSS_FILE_CHIP_THUMB}")
    expect(img).to_have_count(1)
    src = img.get_attribute("src") or ""
    assert src.startswith("data:image/"), f"expected data:image/ src, got {src[:40]!r}"
