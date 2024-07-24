"""Contains variables that store each chart page."""

import vizro.models as vm
import vizro.plotly.express as px

from ._page_utils import DATA_DICT, PAGE_GRID
from .chart_factory import (
    bar_factory,
    butterfly_factory,
    column_factory,
    scatter_factory,
    treemap_factory,
)
from .custom_extensions import CodeClipboard, FlexContainer, Markdown, sankey

# PAGES -------------------------------------------------------------
time_column = column_factory("Time-Column", "Column")
scatter = scatter_factory("Scatter", "Scatter")
bar = bar_factory("Bar", "Bar")
ordered_bar = bar_factory("Ordered Bar", "Ordered Bar")
column = column_factory("Column", "Column")
ordered_column = column_factory("Ordered Column", "Ordered Column")
treemap = treemap_factory("Treemap", "Treemap")
magnitude_treemap = treemap_factory("Magnitude-Treemap", "Treemap")
butterfly_page = butterfly_factory("Butterfly", "Butterfly")
distribution_butterfly = butterfly_factory("Distribution-Butterfly", "Butterfly")
