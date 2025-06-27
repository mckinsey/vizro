"""Utility functions for the Vizro MCP."""

import base64
import gzip
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union
from urllib.parse import quote, urlencode

import pandas as pd
import vizro
import vizro.models as vm
from pydantic.json_schema import GenerateJsonSchema
from vizro.models._base import _format_and_lint

from vizro_mcp._utils.configs import DFInfo, DFMetaData

if TYPE_CHECKING:
    from vizro_mcp._schemas.schemas import ChartPlan

# PyCafe URL for Vizro snippets
PYCAFE_URL = "https://py.cafe"


@dataclass
class VizroCodeAndPreviewLink:
    python_code: str
    pycafe_url: str


def convert_github_url_to_raw(path_or_url: str) -> str:
    """Convert a GitHub URL to a raw URL if it's a GitHub URL, otherwise return the original path or URL."""
    github_pattern = r"https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/(?:blob|raw)/([^/]+)/(.+)"
    github_match = re.match(github_pattern, path_or_url)

    if github_match:
        user, repo, branch, file_path = github_match.groups()
        return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"

    return path_or_url


def load_dataframe_by_format(
    path_or_url: Union[str, Path], mime_type: Optional[str] = None
) -> tuple[pd.DataFrame, Literal["pd.read_csv", "pd.read_json", "pd.read_html", "pd.read_excel", "pd.read_parquet"]]:
    """Load a dataframe based on file format determined by MIME type or file extension."""
    file_path_str_lower = str(path_or_url).lower()

    # Determine format
    if mime_type == "text/csv" or file_path_str_lower.endswith(".csv"):
        df = pd.read_csv(
            path_or_url,
            on_bad_lines="warn",
            low_memory=False,
        )
        read_fn = "pd.read_csv"
    elif mime_type == "application/json" or file_path_str_lower.endswith(".json"):
        df = pd.read_json(path_or_url)
        read_fn = "pd.read_json"
    elif mime_type == "text/html" or file_path_str_lower.endswith((".html", ".htm")):
        tables = pd.read_html(path_or_url)
        if not tables:
            raise ValueError("No HTML tables found in the provided file or URL")
        df = tables[0]  # Get the first table by default
        read_fn = "pd.read_html"
    elif mime_type in [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.oasis.opendocument.spreadsheet",
    ] or any(file_path_str_lower.endswith(ext) for ext in [".xls", ".xlsx", ".ods"]):
        df = pd.read_excel(path_or_url)  # opens only sheet 0
        read_fn = "pd.read_excel"
    elif mime_type == "application/vnd.apache.parquet" or file_path_str_lower.endswith(
        ".parquet"
    ):  # mime type exists but I did not manage to ever extract it
        df = pd.read_parquet(path_or_url)
        read_fn = "pd.read_parquet"
    else:
        raise ValueError("Could not determine file format")

    # Check if the result is a Series and convert to DataFrame if needed
    if isinstance(df, pd.Series):
        df = df.to_frame()

    return df, read_fn


def path_or_url_check(string: str) -> str:
    """Check if a string is a link or a file path."""
    if string.startswith(("http://", "https://", "www.")):
        return "remote"

    if Path(string).is_file():
        return "local"

    return "invalid"


def get_dataframe_info(df: pd.DataFrame) -> DFInfo:
    """Get the info of a DataFrame."""
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()

    # Sample only as many rows as exist in the dataframe, up to 5
    sample_size = min(5, len(df)) if not df.empty else 0

    return DFInfo(general_info=info_string, sample=df.sample(sample_size).to_dict() if sample_size > 0 else {})


def create_pycafe_url(python_code: str) -> str:
    """Create a PyCafe URL for a given Python code."""
    # Create JSON object for py.cafe
    json_object = {
        "code": python_code,
        "requirements": f"vizro=={vizro.__version__}",
        "files": [],
    }

    # Convert to compressed base64 URL
    json_text = json.dumps(json_object)
    compressed_json_text = gzip.compress(json_text.encode("utf8"))
    base64_text = base64.b64encode(compressed_json_text).decode("utf8")
    query = urlencode({"c": base64_text}, quote_via=quote)
    pycafe_url = f"{PYCAFE_URL}/snippet/vizro/v1?{query}"

    return pycafe_url


# TODO: is this still needed after 0.1.42
def remove_figure_quotes(code_string: str) -> str:
    """Remove quotes around all figure argument values."""
    return _format_and_lint(re.sub(r'figure="([^"]*)"', r"figure=\1", code_string))


def get_python_code_and_preview_link(
    model_object: vm.VizroBaseModel,
    data_infos: list[DFMetaData],
    custom_charts: list["ChartPlan"],
) -> VizroCodeAndPreviewLink:
    """Get the Python code and preview link for a Vizro model object."""
    # Get the Python code
    python_code = model_object._to_python(
        extra_callable_defs={custom_chart.get_chart_code(vizro=True) for custom_chart in custom_charts}
    )

    # Gather all imports (static + custom), deduplicate, and insert at the first empty line
    static_imports = [
        "from vizro import Vizro",
        "import pandas as pd",
        "from vizro.managers import data_manager",
    ]
    custom_imports = [
        imp for custom_chart in custom_charts for imp in custom_chart.get_imports(vizro=True).split("\n") if imp.strip()
    ]
    all_imports = list(dict.fromkeys(static_imports + custom_imports))
    lines = python_code.splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            lines[i:i] = all_imports
            break
    python_code = "\n".join(lines)

    # Prepare data loading code
    data_loading_code = "\n".join(
        f'data_manager["{info.file_name}"] = {info.read_function_string}("{info.file_path_or_url}")'
        for info in data_infos
    )

    # Patterns to identify the data manager section
    data_manager_start_marker = "####### Data Manager Settings #####"
    data_manager_end_marker = "########### Model code ############"

    # Replace everything between the markers with our data loading code
    pattern = re.compile(f"{data_manager_start_marker}.*?{data_manager_end_marker}", re.DOTALL)
    replacement = f"{data_manager_start_marker}\n{data_loading_code}\n\n{data_manager_end_marker}"
    python_code = pattern.sub(replacement, python_code)

    # Add final run line
    python_code += "\n\nVizro().build(model).run()"

    python_code = remove_figure_quotes(python_code)

    pycafe_url = create_pycafe_url(python_code)

    return VizroCodeAndPreviewLink(python_code=python_code, pycafe_url=pycafe_url)


class NoDefsGenerateJsonSchema(GenerateJsonSchema):
    """Custom schema generator that handles reference cases appropriately."""

    def generate(self, schema, mode="validation"):
        """Generate schema and resolve references if needed."""
        json_schema = super().generate(schema, mode=mode)

        # If schema is a reference (has $ref but no properties)
        if "$ref" in json_schema and "properties" not in json_schema:
            # Extract the reference path - typically like "#/$defs/ModelName"
            ref_path = json_schema["$ref"]
            if ref_path.startswith("#/$defs/"):
                model_name = ref_path.split("/")[-1]
                # Get the referenced definition from $defs
                # Simply copy the referenced definition content to the top level
                json_schema.update(json_schema["$defs"][model_name])
                # Remove the $ref since we've resolved it
                json_schema.pop("$ref", None)

        # Remove the $defs section if it exists
        json_schema.pop("$defs", None)
        return json_schema


# if __name__ == "__main__":
# print(vm.Dashboard.model_json_schema(schema_generator=NoDefsGenerateJsonSchema).keys())
