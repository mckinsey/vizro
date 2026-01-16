# /// script
# dependencies = [
#   "vizro"
# ]
# ///

import sys
from dataclasses import dataclass
from typing import Any

import vizro.figures as vf
import vizro.models as vm
from pydantic import Field
from pydantic.json_schema import GenerateJsonSchema


@dataclass
class ModelJsonSchemaResults:
    """Results of the get_model_json_schema tool."""

    model_name: str
    json_schema: dict[str, Any]
    additional_info: str


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


# These enhanced models are used to return a more complete schema to the LLM. Although we do not have actual schemas for
# the figure fields, we can prompt the model via the description to produce something likely correct.
class GraphEnhanced(vm.Graph):
    """A Graph model that uses Plotly Express to create the figure."""

    figure: dict[str, Any] = Field(
        description="""
For simpler charts and without need for data manipulation, use this field:
This is the plotly express figure to be displayed. Only use valid plotly express functions to create the figure.
Only use the arguments that are supported by the function you are using and where no extra modules such as statsmodels
are needed (e.g. trendline):
- Configure a dictionary as if this would be added as **kwargs to the function you are using.
- You must use the key: "_target_: "<function_name>" to specify the function you are using. Do NOT precede by
    namespace (like px.line)
- you must refer to the dataframe by name, check file_name in the data_infos field ("data_frame": "<file_name>")
- do not use a title if your Graph model already has a title.
"""
    )


class AgGridEnhanced(vm.AgGrid):
    """AgGrid model that uses dash-ag-grid to create the figure."""

    figure: dict[str, Any] = Field(
        description="""
This is the ag-grid figure to be displayed. Only use arguments from the [`dash-ag-grid` function](https://dash.plotly.com/dash-ag-grid/reference).

The only difference to the dash version is that:
    - you must use the key: "_target_: "dash_ag_grid"
    - you must refer to data via "data_frame": <data_frame_name> and NOT via columnDefs and rowData (do NOT set)
        """
    )


FIGURE_NAMESPACE_FUNCTION_DOCS = {func: vf.__dict__[func].__doc__ for func in vf.__all__}


class FigureEnhanced(vm.Figure):
    """Figure model that allows to use dynamic figure functions."""

    figure: dict[str, Any] = Field(
        description=f"""This is the figure function to be displayed.

Only use arguments from the below mapping of _target_ to figure function documentation:

{FIGURE_NAMESPACE_FUNCTION_DOCS}"""
    )


def get_model_json_schema(
    model_name: str = Field(
        description="Name of the Vizro model/figure/action to get schema for (e.g., 'Card', 'Dashboard', 'Page', 'kpi_card', 'kpi_card_reference' from vizro.figures, or any action from vizro.actions)"
    ),
) -> ModelJsonSchemaResults:
    """Get the JSON schema for the specified Vizro model, figure, or action.

    Returns:
        JSON schema of the requested Vizro model/figure/action
    """
    # Check in vizro.models first
    if hasattr(vm, model_name):
        namespace = vm
        namespace_name = "vizro.models"
    # Then check in vizro.figures
    elif hasattr(vf, model_name):
        namespace = vf
        namespace_name = "vizro.figures"
    # Finally check in vizro.actions
    elif hasattr(va, model_name):
        namespace = va
        namespace_name = "vizro.actions"
    else:
        return ModelJsonSchemaResults(
            model_name=model_name,
            json_schema={},
            additional_info=f"'{model_name}' not found in vizro.models, vizro.figures, or vizro.actions",
        )

    modified_models = {
        "Graph": GraphEnhanced,
        "AgGrid": AgGridEnhanced,
        "Table": AgGridEnhanced,
        "Figure": FigureEnhanced,
    }

    if model_name in modified_models:
        return ModelJsonSchemaResults(
            model_name=model_name,
            json_schema=modified_models[model_name].model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
            additional_info="""LLM must remember to replace `$ref` with the actual config. Request the schema of
that model if necessary.""",
        )
    deprecated_models = {"filter_interaction": "set_control", "Layout": "Grid"}
    if model_name in deprecated_models:
        return ModelJsonSchemaResults(
            model_name=model_name,
            json_schema={},
            additional_info=f"Model '{model_name}' is deprecated. Use {deprecated_models[model_name]} instead.",
        )

    model_class = getattr(namespace, model_name)
    if model_name in {"Grid", "Flex"}:
        return ModelJsonSchemaResults(
            model_name=model_name,
            json_schema=model_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
            additional_info="""Grid layout: use integers starting from 0 to reference elements.
Elements can't overlap, must be rectangular, and rows must have equal column counts.""",
        )

    # Handle vizro.figures and vizro.actions
    if namespace_name in {"vizro.figures", "vizro.actions"}:
        # For functions, try to get their schema if they have model_json_schema method
        if hasattr(model_class, "model_json_schema"):
            return ModelJsonSchemaResults(
                model_name=model_name,
                json_schema=model_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
                additional_info=f"""From {namespace_name}. LLM must remember to replace `$ref` with the actual config. Request the schema of
that model if necessary.""",
            )
        else:
            # Return function documentation if no schema available
            return ModelJsonSchemaResults(
                model_name=model_name,
                json_schema={},
                additional_info=f"""From {namespace_name}. Documentation: {model_class.__doc__ or "No documentation available"}""",
            )

    return ModelJsonSchemaResults(
        model_name=model_name,
        json_schema=model_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
        additional_info="""LLM must remember to replace `$ref` with the actual config. Request the schema of
that model if necessary.""",
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: get_model_json_schema.py <model_name> [<model_name2> ...]",
            file=sys.stderr,
        )
        sys.exit(1)

    import json

    model_names = sys.argv[1:]

    for i, model_name in enumerate(model_names):
        if i > 0:
            print("\n" + "=" * 80 + "\n")

        result = get_model_json_schema(model_name)

        print(f"Model: {result.model_name}")
        print("\nJSON Schema:")
        print(json.dumps(result.json_schema, indent=2))
        print("\nAdditional Info:")
        print(result.additional_info)
