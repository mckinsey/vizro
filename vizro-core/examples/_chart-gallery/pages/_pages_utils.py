"""Contains reusable data sets and constants."""

from pathlib import Path

import black
import pandas as pd
import vizro.plotly.express as px
from custom_components import CodeClipboard


def make_code_clipboard_from_py_file(filepath: str):
    # Black doesn't yet have a Python API, so format_str might not work at some point in the future.
    # https://black.readthedocs.io/en/stable/faq.html#does-black-have-an-api
    filepath = Path(__file__).parents[1] / "pages/examples" / filepath
    return CodeClipboard(
        code=black.format_str(filepath.read_text(encoding="utf-8"), mode=black.Mode(line_length=80)),
        language="python",
    )


PAGE_GRID = [[0, 0, 0, 0, 0, 0, 0]] * 2 + [[1, 1, 1, 1, 2, 2, 2]] * 5

# DATA --------------------------------------------------------------
gapminder = px.data.gapminder()
iris = px.data.iris()
stocks = px.data.stocks()
tips = px.data.tips()

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
