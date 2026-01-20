"""Script to get an overview of available Vizro models."""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "vizro",
# ]
# ///

from typing import Protocol

import vizro.actions as va
import vizro.figures as vf
import vizro.models as vm


class HasNameAndDoc(Protocol):
    """Protocol for objects that have a name and a docstring."""

    __name__: str
    __doc__: str | None


# This dict is used to give the model and overview of what is available in the vizro.models namespace.
# It helps it to narrow down the choices when asking for a model.
MODEL_GROUPS: dict[str, list[type[HasNameAndDoc]]] = {
    "main": [vm.Dashboard, vm.Page],
    "static components": [
        vm.Card,
        vm.Button,
        vm.Text,
        vm.Container,
        vm.Tabs,
    ],
    "dynamic components": [vm.Figure, vm.Graph, vm.AgGrid],
    "layouts": [vm.Grid, vm.Flex],
    "controls": [vm.Filter, vm.Parameter],
    "selectors": [
        vm.Dropdown,
        vm.RadioItems,
        vm.Checklist,
        vm.DatePicker,
        vm.Slider,
        vm.RangeSlider,
        vm.Switch,
    ],
    "navigation": [vm.Navigation, vm.NavBar, vm.NavLink],
    "additional_info": [vm.Tooltip],
    "functions available for vm.Figure(...,figure=...) model": [vf.__dict__[func] for func in vf.__all__],
    "functions available from vizro.actions namespace": [va.__dict__[action] for action in va.__all__],
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


if __name__ == "__main__":
    import json

    overview = get_overview_vizro_models()
    print(json.dumps(overview, indent=2))  # noqa: T201
