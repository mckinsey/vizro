"""Contains reusable data sets and constants."""

import logging
from pathlib import Path

import autoflake
import black
import isort
from custom_components import CodeClipboard

# To disable logging info messages caused by black.format_str: https://github.com/psf/black/issues/2058
logging.getLogger("blib2to3").setLevel(logging.ERROR)

VIZRO_CODE_TEMPLATE = """
import vizro.models as vm
from vizro import Vizro
{example_code}
page = vm.Page(title="My page", components=[vm.Graph(figure=fig)])
dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
"""


def _format_and_lint(code_string: str, line_length: int) -> str:
    """Inspired by vizro.models._base._format_and_lint. The only difference is that this does isort too."""
    # Tracking https://github.com/astral-sh/ruff/issues/659 for proper Python API
    # Good example: https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
    # While we wait for the API, we can use autoflake and black to process code strings
    # Isort is needed since otherwise example code looks quite strange sometimes. Autoflake is needed since isort can't
    # remove imports by itself: https://github.com/PyCQA/isort/issues/1105.

    removed_imports = autoflake.fix_code(code_string, remove_all_unused_imports=True)
    sorted_imports = isort.code(removed_imports)
    # Black doesn't yet have a Python API, so format_str might not work at some point in the future.
    # https://black.readthedocs.io/en/stable/faq.html#does-black-have-an-api
    formatted = black.format_str(sorted_imports, mode=black.Mode(line_length=line_length))
    return formatted


def make_code_clipboard_from_py_file(filepath: str, mode="vizro"):
    # Black doesn't yet have a Python API, so format_str might not work at some point in the future.
    # https://black.readthedocs.io/en/stable/faq.html#does-black-have-an-api
    example_code = (Path(__file__).parents[1] / "pages/examples" / filepath).read_text()

    if mode == "vizro":
        example_code = VIZRO_CODE_TEMPLATE.format(example_code=example_code)
    else:
        replacements = {"import vizro.plotly.express as px": "import plotly.express as px", '@capture("graph")': ""}
        for old_code, new_code in replacements.items():
            example_code = example_code.replace(old_code, new_code)

    return CodeClipboard(
        code=_format_and_lint(example_code, line_length=80),
        mode=mode,
        language="python",
    )


PAGE_GRID = [[0, 0, 0, 0, 0, 0, 0]] * 2 + [[1, 1, 1, 1, 2, 2, 2]] * 5
