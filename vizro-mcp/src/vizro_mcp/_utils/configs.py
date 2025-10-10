"""Pre-set configs for the Vizro MCP."""

from dataclasses import dataclass
from typing import Any, Literal, Optional

import pandas as pd
from pydantic import BaseModel, Field, field_validator, model_validator

DF_MEMORY_LIMIT = 50  # MB


class DFMetaData(BaseModel):
    file_name: str
    file_path_or_url: str
    file_location_type: Literal["local", "remote"] = Field(
        description="The location type of the data. Needs to be `remote` if complete_data is provided."
    )
    read_function_string: Literal["pd.read_csv", "pd.read_json", "pd.read_html", "pd.read_parquet", "pd.read_excel"]
    column_names_types: Optional[dict[str, str]] = None
    complete_data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Fill this if you want to preview local data in PyCafe OR if you have created data as part of research.",
    )

    @model_validator(mode="after")
    def check_complete_data(self):
        if self.complete_data:
            self.file_location_type = "remote"
            self.file_path_or_url = f"{self.file_name}.csv"
        return self

    @classmethod
    @field_validator("complete_data")
    def check_complete_data_type(cls, v):
        if v:
            try:
                pd.DataFrame(v)
            except Exception as e:
                raise ValueError(f"complete_data must be convertible to a pandas DataFrame: {e}")
        return v


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
