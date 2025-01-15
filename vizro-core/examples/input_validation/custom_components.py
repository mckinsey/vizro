""" Custom components. """
import dash_bootstrap_components as dbc
import vizro.models as vm

from dash import html, dcc
from typing import Literal


class NumberInput(vm.VizroBaseModel):
    """Custom component that wraps Vizro dbc.Input type="number" component."""
    type: Literal["number_input"] = "number_input"

    title: str = None
    min: float = None
    max: float = None
    step: float = None
    value: float = None

    def build(self):
        return html.Div(
            children=[
                dbc.Label(children=self.title, html_for=self.id) if self.title else None,
                dbc.Input(
                    id=self.id,
                    type="number",
                    min=self.min,
                    max=self.max,
                    step=self.step,
                    value=self.value,
                    persistence=True,
                    persistence_type="session",
                    # TODO: Consider debounce. This prevents the callback from firing until form focus is lost.
                    # debounce=True,
                )
            ],
        )


class ValidationComponent(vm.VizroBaseModel):
    """Custom component that wraps Vizro component and adds a validation error message field."""

    type: Literal["validation_component"] = "validation_component"
    wrapped_component: vm.VizroBaseModel

    def build(self):
        # Make that wrapped Vizro component ID is overwritten with the ID of the ValidationComponent.
        # This ensures that the underlying component (e.g. vm.Dropdown) can be used as actions input/output.
        self.wrapped_component.id = self.id

        return html.Div(
            children=[
                self.wrapped_component.build(),
                html.Div(
                    id=f"{self.id}-error-id",
                    children="",
                    style={"color": "red"},
                ),
            ]
        )


class LoadingSpinner(vm.VizroBaseModel):
    """Custom component that wraps Vizro dcc.Loading component with a spinner."""
    type: Literal["loading_spinner"] = "loading_spinner"

    def build(self):
        # If self.id is output of the
        return dcc.Loading(
            children=[html.Div(id=self.id, children="", style={"height": "50px", "width": "50px"})], type="circle"
        )


class InitiallyHiddenCard(vm.Card):
    """Custom component that wraps Vizro Card component and hides it initially."""
    type: Literal["initially_hidden_card"] = "initially_hidden_card"

    def build(self):
        card_build_obj = super().build()
        card_build_obj.id = f"{self.id}-outer-div"
        card_build_obj.style = {"display": "none", "cursor": "pointer"}
        return card_build_obj
