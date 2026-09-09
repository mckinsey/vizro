import importlib.util
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[4] / "tools" / "stamp_llms_txt.py"
SPEC = importlib.util.spec_from_file_location("stamp_llms_txt", SCRIPT_PATH)
assert SPEC and SPEC.loader
stamp_llms_txt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stamp_llms_txt)

PLACEHOLDER = "https://vizro.readthedocs.io/en/stable/"


def test_stamp_multiple_files(tmp_path, monkeypatch):
    llms_txt = tmp_path / "llms.txt"
    llms_full_txt = tmp_path / "llms-full.txt"
    llms_txt.write_text(f"{PLACEHOLDER}pages/guide/", encoding="utf-8")
    llms_full_txt.write_text(f"Source: {PLACEHOLDER}pages/guide/", encoding="utf-8")
    monkeypatch.setenv("READTHEDOCS_VERSION", "0.2.0")

    result = stamp_llms_txt.stamp_llms_txt(
        PLACEHOLDER,
        tmp_path,
        filenames=("llms.txt", "llms-full.txt"),
    )

    assert result == 0
    assert llms_txt.read_text(encoding="utf-8") == "https://vizro.readthedocs.io/en/0.2.0/pages/guide/"
    assert llms_full_txt.read_text(encoding="utf-8") == "Source: https://vizro.readthedocs.io/en/0.2.0/pages/guide/"


def test_stamp_validates_all_files_before_writing(tmp_path, monkeypatch):
    llms_txt = tmp_path / "llms.txt"
    llms_txt.write_text(PLACEHOLDER, encoding="utf-8")
    monkeypatch.setenv("READTHEDOCS_VERSION", "0.2.0")

    result = stamp_llms_txt.stamp_llms_txt(
        PLACEHOLDER,
        tmp_path,
        filenames=("llms.txt", "llms-full.txt"),
    )

    assert result == 1
    assert llms_txt.read_text(encoding="utf-8") == PLACEHOLDER


def test_stamp_leaves_files_unchanged_outside_readthedocs(tmp_path, monkeypatch):
    llms_txt = tmp_path / "llms.txt"
    llms_txt.write_text(PLACEHOLDER, encoding="utf-8")
    monkeypatch.delenv("READTHEDOCS_VERSION", raising=False)

    assert stamp_llms_txt.stamp_llms_txt(PLACEHOLDER, tmp_path) == 0
    assert llms_txt.read_text(encoding="utf-8") == PLACEHOLDER
