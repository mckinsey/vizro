"""Prompts for the Vizro MCP."""

from typing import Literal

import vizro.models as vm

CHART_INSTRUCTIONS = """
IMPORTANT:
    - ALWAYS VALIDATE:if you iterate over a valid produced solution, make sure to ALWAYS call the
        validate_chart_code tool to validate the chart code, display the figure code to the user
    - DO NOT modify the background (with plot_bgcolor) or color sequences unless explicitly asked for

Instructions for creating a Vizro chart:
    - analyze the datasets needed for the chart using the load_and_analyze_data tool - the most important
        information here are the column names and column types
    - if the user provides no data, but you need to display a chart or table, use the get_sample_data_info
        tool to get sample data information
    - create a chart using plotly express and/or plotly graph objects, and call the function `custom_chart`
    - call the validate_chart_code tool to validate the chart code, display the figure code to the user (as artifact)
    - do NOT call any other tool after, especially do NOT create a dashboard
            """

STANDARD_INSTRUCTIONS = """
IMPORTANT:
    - ALWAYS VALIDATE: if you iterate over a valid produced solution, make sure to ALWAYS call the
        `validate_dashboard_config` tool again to ensure the solution is still valid
    - DO NOT show any code or config to the user until you have validated the solution, do not say you are preparing
        a solution, just do it and validate it
    - ALWAYS CHECK SCHEMA: to start with, or when stuck, try enquiring the schema of the component in question
with the `get_model_json_schema` tool (available models see below)

- IF the user has no plan (ie no components or pages), use the config at the bottom of this prompt, OTHERWISE:
- make a plan of what components you would like to use, then request all necessary schemas
    using the `get_model_json_schema` tool (start with `Dashboard`, and don't forget `Graph`)
- assemble your components into a page, then add the page or pages to a dashboard, DO NOT show config or code
    to the user until you have validated the solution
- ALWAYS validate the dashboard configuration using the `validate_dashboard_config` tool
- using `custom_chart` is encouraged for advanced visualizations, no need to call the planner tool in advanced mode
"""

IDE_INSTRUCTIONS = """
- after validation, add the python code to `app.py` with the following code:
    ```python
    app = Vizro().build(dashboard)
    if __name__ == "__main__":
        app.run(debug=True, port=8050)
- you MUST use the code from the validation tool, do not modify it, watch out for differences to previous
    `app.py`
"""

GENERIC_HOST_INSTRUCTIONS = """
- you should call the `validate_dashboard_config` tool to validate the solution, and unless
    otherwise specified, open the dashboard in the browser
- if you cannot open the dashboard in the browser, communicate this to the user, provide them with the python code
    instead and explain how to run it
"""

# This dict is used to give the model and overview of what is available in the vizro.models namespace.
# It helps it to narrow down the choices when asking for a model.
MODEL_GROUPS: dict[str, list[type[vm.VizroBaseModel]]] = {
    "main": [vm.Dashboard, vm.Page],
    "components": [vm.Card, vm.Button, vm.Text, vm.Container, vm.Tabs, vm.Graph, vm.AgGrid],  #'Figure', 'Table'
    "layouts": [vm.Grid, vm.Flex],
    "controls": [vm.Filter, vm.Parameter],
    "selectors": [
        vm.Dropdown,
        vm.RadioItems,
        vm.Checklist,
        vm.DatePicker,
        vm.Slider,
        vm.RangeSlider,
        vm.DatePicker,
    ],
    "navigation": [vm.Navigation, vm.NavBar, vm.NavLink],
    # vm.Tooltip
}


def get_overview_vizro_models() -> dict[str, list[dict[str, str]]]:
    """Get all available models in the vizro.models namespace.

    Returns:
        Dictionary with categories of models and their descriptions
    """
    result: dict[str, list[dict[str, str]]] = {}
    for category, models_list in MODEL_GROUPS.items():
        result[category] = [
            {
                "name": model_class.__name__,
                "description": (model_class.__doc__ or "No description available").split("\n")[0],
            }
            for model_class in models_list
        ]
    return result


def get_dashboard_instructions(
    advanced_mode: bool = False, user_host: Literal["generic_host", "ide"] = "generic_host"
) -> str:
    """Get instructions for creating a Vizro dashboard in an IDE/editor."""
    if not advanced_mode:
        return f"""
    {STANDARD_INSTRUCTIONS}

    {IDE_INSTRUCTIONS if user_host == "ide" else GENERIC_HOST_INSTRUCTIONS}

    Models you can use:
    {get_overview_vizro_models()}

    Very simple dashboard config:
    {get_simple_dashboard_config()}
"""
    else:
        return """
    Instructions for going beyond the basic dashboard:
    - ensure that you have called the `get_vizro_chart_or_dashboard_plan` tool with advanced_mode=False first
    - communicate to the user that you are going to use Python code to create the dashboard, and that
        they will have to run the code themselves
    - search the web for more information about the components you are using, if you cannot search the web
        communicate this to the user, and tell them that this is a current limitation of the tool
    - if stuck, return to a JSON based config, and call the `validate_dashboard_config` tool to validate the solution
"""
