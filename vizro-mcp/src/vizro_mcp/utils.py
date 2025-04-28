"""Utility functions for the Vizro MCP."""

import base64
import gzip
import io
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode

import pandas as pd
import vizro.models as vm

# PyCafe URL for Vizro snippets
PYCAFE_URL = "https://py.cafe"


def _convert_github_url_to_raw(path_or_url: str) -> str:
    """Convert a GitHub URL to a raw URL if it's a GitHub URL, otherwise return the original path or URL."""
    github_pattern = r"https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/(?:blob|raw)/([^/]+)/(.+\.csv)"
    github_match = re.match(github_pattern, path_or_url)

    if github_match:
        user, repo, branch, file_path = github_match.groups()
        return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"

    return path_or_url


def _path_or_url_check(string: str) -> str:
    """Check if a string is a link or a file path."""
    if string.startswith(("http://", "https://", "www.")):
        return "remote"

    if Path(string).is_file():
        return "local"

    return "invalid"


def _get_dataframe_info(df: pd.DataFrame) -> dict[str, Any]:
    """Get the info of a DataFrame."""
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()
    return {
        "general_info": info_string,
        "sample": df.sample(5).to_dict() if not df.empty else {},
    }


def _get_python_code_and_preview_link(
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
import vizro.tables as vt

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

    # Add final run line
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
