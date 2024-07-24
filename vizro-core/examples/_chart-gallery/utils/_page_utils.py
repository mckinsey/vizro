"""Contains reusable data sets and constants."""
from pathlib import Path

import black
import pandas as pd
import vizro.plotly.express as px
from utils.custom_extensions import CodeClipboard


def make_code_clipboard_from_py_file(filepath: str):
    # comment on stability
    filepath = Path(__file__).parents[1] / "pages/examples" / filepath
    return CodeClipboard(
        code=black.format_str(filepath.read_text(encoding="utf-8"), mode=black.Mode()), language="python"
    )


# DATA --------------------------------------------------------------
gapminder = px.data.gapminder()
gapminder_2007 = gapminder.query("year == 2007")
iris = px.data.iris()
stocks = px.data.stocks()
tips = px.data.tips()
tips_agg = tips.groupby("day").agg({"total_bill": "sum"}).sort_values("total_bill").reset_index()
ages = pd.DataFrame(
    {
        "Age": ["0-19", "20-29", "30-39", "40-49", "50-59", ">=60"],
        "Male": [800, 2000, 4200, 5000, 2100, 800],
        "Female": [1000, 3000, 3500, 3800, 3600, 700],
    }
)

sankey_data = pd.DataFrame(
    {
        "Origin": [0, 1, 2, 1, 2, 4, 0],  # indices inside labels
        "Destination": [1, 2, 3, 4, 5, 5, 6],  # indices inside labels
        "Value": [10, 4, 8, 6, 4, 8, 8],
    }
)

DATA_DICT = {
    "gapminder": gapminder,
    "gapminder_2007": gapminder_2007,
    "iris": iris,
    "stocks": stocks,
    "tips": tips,
    "tips_agg": tips_agg,
    "ages": ages,
    "sankey_data": sankey_data,
}
PAGE_GRID = [[0, 0, 0, 0, 0]] * 2 + [[1, 1, 1, 2, 2]] * 5
