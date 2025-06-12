"""Pre-set configs for the Vizro MCP."""

from dataclasses import dataclass
from typing import Any, Literal, Optional


@dataclass
class DFMetaData:
    file_name: str
    file_path_or_url: str
    file_location_type: Literal["local", "remote"]
    read_function_string: Literal["pd.read_csv", "pd.read_json", "pd.read_html", "pd.read_parquet", "pd.read_excel"]
    column_names_types: Optional[dict[str, str]] = None


@dataclass
class DFInfo:
    general_info: str
    sample: dict[str, Any]


IRIS = DFMetaData(
    file_name="iris_data",
    file_path_or_url="https://raw.githubusercontent.com/plotly/datasets/master/iris-id.csv",
    file_location_type="remote",
    read_function_string="pd.read_csv",
    column_names_types={
        "sepal_length": "float",
        "sepal_width": "float",
        "petal_length": "float",
        "petal_width": "float",
        "species": "str",
    },
)

TIPS = DFMetaData(
    file_name="tips_data",
    file_path_or_url="https://raw.githubusercontent.com/plotly/datasets/master/tips.csv",
    file_location_type="remote",
    read_function_string="pd.read_csv",
    column_names_types={
        "total_bill": "float",
        "tip": "float",
        "sex": "str",
        "smoker": "str",
        "day": "str",
        "time": "str",
        "size": "int",
    },
)

STOCKS = DFMetaData(
    file_name="stocks_data",
    file_path_or_url="https://raw.githubusercontent.com/plotly/datasets/master/stockdata.csv",
    file_location_type="remote",
    read_function_string="pd.read_csv",
    column_names_types={
        "Date": "str",
        "IBM": "float",
        "MSFT": "float",
        "SBUX": "float",
        "AAPL": "float",
        "GSPC": "float",
    },
)

GAPMINDER = DFMetaData(
    file_name="gapminder_data",
    file_path_or_url="https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv",
    file_location_type="remote",
    read_function_string="pd.read_csv",
    column_names_types={
        "country": "str",
        "continent": "str",
        "year": "int",
        "lifeExp": "float",
        "pop": "int",
        "gdpPercap": "float",
    },
)

SAMPLE_DASHBOARD_CONFIG = """
{
  `config`: {
    `pages`: [
      {
        `title`: `Iris Data Analysis`,
        `controls`: [
          {
            `id`: `species_filter`,
            `type`: `filter`,
            `column`: `species`,
            `targets`: [
              `scatter_plot`
            ],
            `selector`: {
              `type`: `dropdown`,
              `multi`: true
            }
          }
        ],
        `components`: [
          {
            `id`: `scatter_plot`,
            `type`: `graph`,
            `title`: `Sepal Dimensions by Species`,
            `figure`: {
              `x`: `sepal_length`,
              `y`: `sepal_width`,
              `color`: `species`,
              `_target_`: `scatter`,
              `data_frame`: `iris_data`,
              `hover_data`: [
                `petal_length`,
                `petal_width`
              ]
            }
          }
        ]
      }
    ],
    `theme`: `vizro_dark`,
    `title`: `Iris Dashboard`
  },
  `data_infos`: `
[
    {
        \"file_name\": \"iris_data\",
        \"file_path_or_url\": \"https://raw.githubusercontent.com/plotly/datasets/master/iris-id.csv\",
        \"file_location_type\": \"remote\",
        \"read_function_string\": \"pd.read_csv\",
    }
]
`
}

"""


def get_simple_dashboard_config() -> str:
    """Very simple Vizro dashboard configuration. Use this config as a starter when no other config is provided."""
    return SAMPLE_DASHBOARD_CONFIG
