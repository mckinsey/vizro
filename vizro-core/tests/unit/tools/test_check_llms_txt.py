import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).parents[3] / "tools" / "check_llms_txt.py"
SPEC = importlib.util.spec_from_file_location("check_llms_txt", SCRIPT_PATH)
assert SPEC and SPEC.loader
check_llms_txt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_llms_txt)

BASE_URL = "https://vizro.readthedocs.io/en/stable/"


@pytest.fixture
def built_docs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source_page = tmp_path / "docs/pages/guide.md"
    source_page.parent.mkdir(parents=True)
    source_page.write_text("# Guide", encoding="utf-8")
    models_dir = tmp_path / "site/pages/API-reference/models"
    models_dir.mkdir(parents=True)
    (models_dir / "graph.md").write_text("# Graph", encoding="utf-8")
    (models_dir / "index.md").write_text("# Models", encoding="utf-8")
    (tmp_path / "site/llms-full.txt").write_text("# Full documentation", encoding="utf-8")
    return tmp_path


def write_llms_txt(root, links):
    llms_txt = root / "docs/llms.txt"
    llms_txt.write_text("# Test\n\n" + "\n".join(f"- [Link]({url})" for url in links), encoding="utf-8")


def test_check_generated_and_authored_links(built_docs):
    write_llms_txt(
        built_docs,
        [
            f"{BASE_URL}pages/guide/",
            f"{BASE_URL}llms-full.txt",
            f"{BASE_URL}pages/API-reference/models/graph.md",
        ],
    )

    assert check_llms_txt.check_llms_txt() == 0


def test_check_detects_generated_model_missing_from_index(built_docs):
    write_llms_txt(built_docs, [f"{BASE_URL}pages/guide/", f"{BASE_URL}llms-full.txt"])

    assert check_llms_txt.check_llms_txt() == 1


def test_check_detects_broken_generated_link(built_docs):
    write_llms_txt(
        built_docs,
        [
            f"{BASE_URL}pages/guide/",
            f"{BASE_URL}llms-full.txt",
            f"{BASE_URL}pages/API-reference/models/missing.md",
        ],
    )

    assert check_llms_txt.check_llms_txt() == 1
