"""Contains reusable data sets and constants."""

import logging
from pathlib import Path

import autoflake
import black
import isort
import pandas as pd
import vizro.plotly.express as px
from custom_components import CodeClipboard

# To disable logging info messages caused by black.format_str: https://github.com/psf/black/issues/2058
logging.getLogger("blib2to3").setLevel(logging.ERROR)

VIZRO_CODE_TEMPLATE = """
import vizro.models as vm
from vizro import Vizro
{example_code}
page = vm.Page(title="{title}", components=[vm.Graph(figure=fig)])
dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
"""
# TODO:
# Roll out changes across all files - need to modify all example files other than magnitude ones and import fig directly
# from those files in all vm.Graph().
# De-duplicate.


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
        example_code = VIZRO_CODE_TEMPLATE.format(title="Title", example_code=example_code)
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

# DATA --------------------------------------------------------------
gapminder = px.data.gapminder()
iris = px.data.iris()
stocks = px.data.stocks()
tips = px.data.tips()
wind = px.data.wind()
ages = pd.DataFrame(
    {
        "Age": ["0-19", "20-29", "30-39", "40-49", "50-59", ">=60"],
        "Male": [800, 2000, 4200, 5000, 2100, 800],
        "Female": [1000, 3000, 3500, 3800, 3600, 700],
    }
)
sankey_data = pd.DataFrame(
    {
        "Origin": [0, 1, 0, 2, 3, 3],
        "Destination": [2, 3, 3, 4, 4, 5],
        "Value": [8, 4, 2, 8, 4, 2],
    }
)

funnel_data = pd.DataFrame(
    {"Stage": ["Leads", "Sales calls", "Follow-up", "Conversion", "Sales"], "Value": [10, 7, 4, 2, 1]}
)

stepped_line_data = pd.DataFrame(
    {
        "year": [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003],
        "rate": [0.10, 0.12, 0.15, 0.13, 0.14, 0.13, 0.14, 0.16, 0.15],
    }
)


carshare = px.data.carshare()

tasks = pd.DataFrame(
    [
        {"Task": "Job A", "Start": "2009-01-01", "Finish": "2009-02-28"},
        {"Task": "Job B", "Start": "2009-03-05", "Finish": "2009-04-15"},
        {"Task": "Job C", "Start": "2009-02-20", "Finish": "2009-05-30"},
    ]
)

waterfall_data = pd.DataFrame(
    {
        "x": ["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
        "y": [60, 80, 0, -40, -20, 0],
        "measure": ["relative", "relative", "total", "relative", "relative", "total"],
    }
)

pastries = pd.DataFrame(
    {
        "pastry": [
            "Scones",
            "Bagels",
            "Muffins",
            "Cakes",
            "Donuts",
            "Cookies",
            "Croissants",
            "Eclairs",
        ],
        "Profit Ratio": [-0.10, -0.05, 0.10, 0.05, 0.15, -0.08, 0.08, -0.12],
        "Strongly Disagree": [20, 30, 10, 5, 15, 5, 10, 25],
        "Disagree": [30, 25, 20, 10, 20, 10, 15, 30],
        "Agree": [30, 25, 40, 40, 45, 40, 40, 25],
        "Strongly Agree": [20, 20, 30, 45, 20, 45, 35, 20],
    }
)

salaries = pd.DataFrame(
    {
        "Job": ["Developer", "Analyst", "Manager", "Specialist"],
        "Min": [60000, 55000, 70000, 50000],
        "Max": [130000, 110000, 96400, 80000],
    }
)
