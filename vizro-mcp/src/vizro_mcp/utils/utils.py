"""Utility functions for the Vizro MCP."""

import base64
import gzip
import json
from pathlib import Path
from typing import Any, Union
from urllib.parse import quote, urlencode

import pandas as pd
import vizro.models as vm

# PyCafe URL for Vizro snippets
PYCAFE_URL = "https://py.cafe"


# Function to capture DataFrame info
def get_dataframe_info(df: pd.DataFrame, file_path_or_url: Union[str, Path]) -> dict[str, Any]:
    """Get the info of a DataFrame."""
    return {
        # "info": info_str,
        "location_type": "local" if isinstance(file_path_or_url, Path) else "remote",
        "file_path_or_url": file_path_or_url,
        "shape": df.shape,
        "columns": list(df.columns),
        "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        # "missing_values": df.isna().sum().to_dict(),
        # "numeric_stats": df.describe().to_dict() if not df.empty else {},
        "sample": df.sample(5).to_dict() if not df.empty else {},
    }


def get_python_code_and_preview_link(
    model_object: vm.VizroBaseModel, file_name: str, file_paths_or_urls: str
) -> dict[str, Any]:
    """Get the Python code and preview link for a Vizro model object."""
    # Get the Python code
    python_code = model_object._to_python()

    # Add imports and dataset definitions at the top
    imports_and_data = f"""from vizro import Vizro
import vizro.plotly.express as px
from vizro.managers import data_manager
import pandas as pd
import vizro.models as vm

# Load data into the data_manager
data_manager["{file_name}"] = pd.read_csv("{file_paths_or_urls}")

"""
    # Find the model code section and prepend imports_and_data
    model_code_marker = "########### Model code ############"
    if model_code_marker in python_code:
        parts = python_code.split(model_code_marker, 1)
        python_code = imports_and_data + model_code_marker + parts[1]
    # Fallback if marker not found
    elif python_code.startswith("from vizro import Vizro"):
        python_code = imports_and_data + python_code[len("from vizro import Vizro\n") :]
    else:
        python_code = imports_and_data + python_code

    # Add final run line if not present
    if "Vizro().build(model).run()" not in python_code:
        python_code += "\n\nVizro().build(model).run()"

    # Create JSON object for py.cafe
    json_object = {
        "code": python_code,
        "requirements": "vizro",
        "files": [],
    }

    # Convert to compressed base64 URL
    json_text = json.dumps(json_object)
    compressed_json_text = gzip.compress(json_text.encode("utf8"))
    base64_text = base64.b64encode(compressed_json_text).decode("utf8")
    query = urlencode({"c": base64_text}, quote_via=quote)
    pycafe_url = f"{PYCAFE_URL}/snippet/vizro/v1?{query}"

    return {"python_code": python_code, "pycafe_url": pycafe_url}
