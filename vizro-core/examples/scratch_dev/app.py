"""Dev app to try things out."""

import vizro.models as vm
from vizro import Vizro
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, html
from typing import Literal

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class DmcShowcase(VizroBaseModel):
    """Development-only component that renders a grid of Dash Mantine components.

    Use this to verify how DMC components look inside a Vizro app with vizro-bootstrap theme.
    """

    type: Literal["dmc_showcase"] = "dmc_showcase"

    @_log_call
    def build(self):
        """Build layout: Container with title, subtitle, action buttons, divider, then Group of cards."""
        return html.Div(
            id=self.id,
            children=dmc.Container(
                [
                    dmc.Group(
                        [
                            dmc.Title("Dash Mantine Components in Vizro", order=1, mt="lg"),
                            dmc.Anchor(
                                "DMC docs",
                                href="https://www.dash-mantine-components.com",
                                target="_blank",
                                size="sm",
                            ),
                        ],
                        justify="space-between",
                    ),
                    dmc.Title(
                        "Components styled with vizro-bootstrap theme (light/dark)",
                        order=3,
                        mb="lg",
                    ),
                    dmc.Divider(size="md", mt="lg"),
                    dmc.Space(h=60),
                    dmc.Grid(
                        [
                            dmc.GridCol(span=6, children=_sample_components_card()),
                            dmc.GridCol(span=6, children=_progress_card()),
                            dmc.GridCol(span=6, children=_figures_card()),
                            dmc.GridCol(span=6, children=_date_picker_card()),
                            dmc.GridCol(span=6, children=_authentication_card()),
                            dmc.GridCol(span=6, children=_stepper_card()),
                            dmc.GridCol(span=6, children=_inputs_card()),
                            dmc.GridCol(span=6, children=_card_paper_card()),
                            dmc.GridCol(span=6, children=_accordion_card()),
                            dmc.GridCol(span=6, children=_tabs_card()),
                        ],
                        gutter="lg",
                    ),
                ],
                mb="lg",
            ),
            className="dmc-showcase-root",
        )


def _card_wrapper(title: str, children):
    """Wrap content in a Card with a title."""
    return dmc.Card(
        [
            dmc.Text(title, fw=600, size="sm", c="dimmed", mb="xs"),
            dmc.Stack(children, gap="sm"),
        ],
        withBorder=True,
        padding="md",
        shadow="sm",
        style={"height": "100%"},
    )


def _sample_components_card():
    """Alert, Badge, Buttons, Loader."""
    return _card_wrapper(
        "Sample components",
        [
            dmc.Alert(
                "This is an Alert. It uses theme colors.",
                title="Info",
                color="blue",
            ),
            dmc.Group(
                [
                    dmc.Badge("Default", color="gray"),
                    dmc.Badge("Primary", color="blue"),
                    dmc.Badge("Success", color="green"),
                    dmc.Badge("Warning", color="yellow"),
                ],
                gap="sm",
            ),
            dmc.Group(
                [
                    dmc.Button("Filled", variant="filled"),
                    dmc.Button("Outline", variant="outline"),
                    dmc.Button("Light", variant="light"),
                    dmc.Button("Subtle", variant="subtle"),
                ],
                gap="sm",
            ),
            dmc.Loader(size="sm"),
        ],
    )


def _progress_card():
    """Progress bar and RingProgress."""
    return _card_wrapper(
        "Progress",
        [
            dmc.Progress(value=45, size="md"),
            dmc.RingProgress(
                label="65%",
                sections=[{"value": 65, "color": "blue"}],
            ),
        ],
    )


def _figures_card():
    """Simple Plotly graph."""
    fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[2, 1, 4], mode="lines+markers")])
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=180)
    return _card_wrapper(
        "Figures",
        [dcc.Graph(figure=fig, config={"displayModeBar": False})],
    )


def _date_picker_card():
    """DatePickerInput."""
    return _card_wrapper(
        "Date picker",
        [
            dmc.DatePickerInput(
                id="dmc-showcase-date-picker",
                label="Pick a date",
                placeholder="Select date",
            ),
        ],
    )


def _authentication_card():
    """Login-style form: email, password, button."""
    return _card_wrapper(
        "Authentication",
        [
            dmc.TextInput(
                label="Email",
                placeholder="your@email.com",
            ),
            dmc.TextInput(
                label="Password",
                placeholder="Password",
            ),
            dmc.Button("Sign in", variant="filled"),
        ],
    )


def _stepper_card():
    """Stepper with steps."""
    return _card_wrapper(
        "Stepper",
        [
            dmc.Stepper(
                id="dmc-showcase-stepper",
                active=1,
                children=[
                    dmc.StepperStep(label="First", description="First step"),
                    dmc.StepperStep(label="Second", description="Second step"),
                    dmc.StepperStep(label="Third", description="Third step"),
                ],
            ),
        ],
    )


def _inputs_card():
    """TextInput, Select, Checkbox, Switch."""
    return _card_wrapper(
        "Inputs",
        [
            dmc.TextInput(label="Text input", placeholder="Placeholder"),
            dmc.Select(
                label="Select",
                data=["Option 1", "Option 2", "Option 3"],
                value="Option 1",
            ),
            dmc.Checkbox(label="Checkbox", checked=False),
            dmc.Switch(label="Switch", checked=False),
        ],
    )


def _card_paper_card():
    """Card and Paper."""
    return _card_wrapper(
        "Card & Paper",
        [
            dmc.Card(
                children=[
                    dmc.Text("Card title", fw=500, size="lg"),
                    dmc.Text(
                        "Card description. Uses theme background and border.",
                        c="dimmed",
                        size="sm",
                    ),
                ],
                withBorder=True,
                padding="md",
            ),
            dmc.Paper(
                "Paper component with padding.",
                withBorder=True,
                p="md",
            ),
        ],
    )


def _accordion_card():
    """Accordion."""
    return _card_wrapper(
        "Accordion",
        [
            dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Item 1"),
                            dmc.AccordionPanel("Content for item 1."),
                        ],
                        value="item1",
                    ),
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Item 2"),
                            dmc.AccordionPanel("Content for item 2."),
                        ],
                        value="item2",
                    ),
                ],
            ),
        ],
    )


def _tabs_card():
    """Tabs and Divider."""
    return _card_wrapper(
        "Tabs & Divider",
        [
            dmc.Tabs(
                [
                    dmc.TabsList(
                        [
                            dmc.TabsTab("Tab 1", value="tab1"),
                            dmc.TabsTab("Tab 2", value="tab2"),
                        ]
                    ),
                    dmc.TabsPanel("Tab 1 content.", value="tab1"),
                    dmc.TabsPanel("Tab 2 content.", value="tab2"),
                ],
                value="tab1",
            ),
            dmc.Divider(label="Divider", labelPosition="left"),
        ],
    )


vm.Page.add_type("components", DmcShowcase)

dmc_page = vm.Page(
    title="DMC Showcase",
    components=[DmcShowcase()],
)

dashboard = vm.Dashboard(
    title="DMC in Vizro",
    theme="vizro_light",
    pages=[dmc_page],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
