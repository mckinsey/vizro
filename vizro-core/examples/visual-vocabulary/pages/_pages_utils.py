"""Contains reusable data sets and constants."""

import logging
from pathlib import Path

import black
import pandas as pd
import vizro.plotly.express as px
from custom_components import CodeClipboard

# To disable logging info messages caused by black.format_str: https://github.com/psf/black/issues/2058
logging.getLogger("blib2to3").setLevel(logging.ERROR)


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
            "Brownies",
            "Tarts",
            "Macarons",
            "Pies",
        ],
        "Profit Ratio": [-0.10, -0.15, -0.05, 0.10, 0.05, 0.20, 0.15, -0.08, 0.08, -0.12, 0.02, -0.07],
    }
)


salaries = pd.DataFrame(
    {
        "Job": ["Developer", "Analyst", "Manager", "Specialist"] * 2,
        "Salary": [60000, 55000, 70000, 50000, 130000, 110000, 96400, 80000],
        "Range": ["Min"] * 4 + ["Max"] * 4,
    }
)
