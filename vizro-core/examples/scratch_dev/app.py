"""Dev app to try things out."""

import vizro.models as vm
from vizro import Vizro
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, html
from typing import Literal

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

# Shared layout constants
GAP = "12px"
CARD_TITLE_SIZE = "md"
SECTION_LABEL_SIZE = "sm"


def _section_label(text: str):
    """Section heading inside a card (e.g. 'Anchor', 'Breadcrumbs')."""
    return dmc.Text(text, size=SECTION_LABEL_SIZE, fw=600, c="dimmed", mb="xs")


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
                    dmc.Grid(
                        [
                            dmc.GridCol(span=6, children=_sample_components_card()),
                            dmc.GridCol(span=6, children=_pickers_card()),
                            dmc.GridCol(span=6, children=_form_card()),
                            dmc.GridCol(span=6, children=_navigation_card()),
                            dmc.GridCol(span=6, children=_progress_sliders_card()),
                            dmc.GridCol(span=6, children=_containers_display_card()),
                        ],
                        gutter="lg",
                    ),
                ],
                mb="lg",
            ),
            className="dmc-showcase-root",
        )


def _card_wrapper(title: str, children, style=None):
    """Wrap content in a Card with a title."""
    card_style = {"height": "100%", "backgroundColor": "inherit"}
    if style:
        card_style = {**card_style, **style}
    return dmc.Card(
        [
            dmc.Text(title, fw=600, size=CARD_TITLE_SIZE, c="dimmed", mb="sm"),
            dmc.Stack(children, style={"gap": GAP}),
        ],
        withBorder=True,
        padding="md",
        shadow="sm",
        style=card_style,
    )


def _sample_components_card():
    """Alert, Badge, Buttons."""
    return _card_wrapper(
        "Sample components",
        [
            dmc.Stack(
                [
                    dmc.Alert(
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                        title="Info",
                        color="blue",
                    ),
                    dmc.Alert(
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                        title="Success",
                        color="green",
                    ),
                    dmc.Alert(
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                        title="Danger",
                        color="red",
                    ),
                    dmc.Alert(
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                        title="Warning",
                        color="yellow",
                    ),
                    dmc.Flex(
                        [
                            dmc.Badge("Default", color="gray"),
                            dmc.Badge("Primary", color="blue"),
                            dmc.Badge("Success", color="green"),
                            dmc.Badge("Warning", color="yellow"),
                        ],
                        gap="sm",
                        wrap="wrap",
                    ),
                    dmc.Flex(
                        [
                            dmc.Button("Filled", variant="filled"),
                            dmc.Button("Outline", variant="outline"),
                            dmc.Button("Light", variant="light"),
                            dmc.Button("Subtle", variant="subtle"),
                        ],
                        gap="sm",
                        wrap="wrap",
                    ),
                ],
                style={"gap": GAP},
            ),
        ],
    )


def _navigation_card():
    """Anchor, Breadcrumbs, NavLink, Pagination, Stepper, Timeline, Tabs, Accordion."""
    return _card_wrapper(
        "Navigation",
        [
            dmc.Stack(
                [
                    _section_label("Anchor"),
                    dmc.Group(
                        [
                            dmc.Anchor("Underline always", href="#", underline="always"),
                            dmc.Anchor("Hover", href="#", underline="hover"),
                            dmc.Anchor("Never", href="#", underline="never"),
                        ],
                        gap="sm",
                    ),
                    _section_label("Breadcrumbs"),
                    dmc.Breadcrumbs(
                        children=[
                            dmc.Anchor("Home", href="#"),
                            dmc.Anchor("Docs", href="#"),
                            dmc.Anchor("Anchor", href="#"),
                        ],
                        separator="/",
                    ),
                    _section_label("NavLink"),
                    dmc.NavLink(label="Dashboard", href="#"),
                    dmc.NavLink(label="Settings", href="#", active=True),
                    _section_label("Pagination"),
                    dmc.Pagination(total=10, value=1, id="dmc-showcase-pagination"),
                    _section_label("Stepper"),
                    dmc.Stepper(
                        orientation="vertical",
                        id="dmc-showcase-stepper",
                        active=1,
                        children=[
                            dmc.StepperStep(label="First", description="First step"),
                            dmc.StepperStep(label="Second", description="Second step"),
                            dmc.StepperStep(label="Third", description="Third step"),
                        ],
                    ),
                    _section_label("Timeline"),
                    dmc.Timeline(
                        id="dmc-showcase-timeline",
                        active=1,
                        bulletSize=15,
                        lineWidth=2,
                        children=[
                            dmc.TimelineItem(
                                title="Step one",
                                children=dmc.Text("First event description.", c="dimmed", size="sm"),
                            ),
                            dmc.TimelineItem(
                                title="Step two",
                                children=dmc.Text("Second event description.", c="dimmed", size="sm"),
                            ),
                            dmc.TimelineItem(
                                title="Step three",
                                lineVariant="dashed",
                                children=dmc.Text("Third event (dashed line).", c="dimmed", size="sm"),
                            ),
                        ],
                    ),
                    _section_label("Tabs"),
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
                    _section_label("Accordion"),
                    dmc.Accordion(
                        id="dmc-showcase-accordion",
                        value=["customization"],
                        multiple=True,
                        variant="contained",
                        chevronPosition="right",
                        children=[
                            dmc.AccordionItem(
                                [
                                    dmc.AccordionControl("Customization"),
                                    dmc.AccordionPanel(
                                        "Colors, fonts, shadows and many other parts are customizable to fit your design."
                                    ),
                                ],
                                value="customization",
                            ),
                            dmc.AccordionItem(
                                [
                                    dmc.AccordionControl("Flexibility"),
                                    dmc.AccordionPanel(
                                        "Configure appearance and behavior with a vast amount of settings or overwrite any "
                                        "part of component styles."
                                    ),
                                ],
                                value="flexibility",
                            ),
                            dmc.AccordionItem(
                                [
                                    dmc.AccordionControl("Item 3 (disabled)", disabled=True),
                                    dmc.AccordionPanel("This panel is not reachable."),
                                ],
                                value="item3",
                            ),
                        ],
                    ),
                ],
                style={"gap": GAP},
            ),
        ],
    )


def _progress_sliders_card():
    """Progress, RingProgress, Slider, RangeSlider, Rating, Loader."""
    return _card_wrapper(
        "Progress & sliders",
        [
            dmc.Stack(
                [
                    dmc.Progress(value=45),
                    dmc.RingProgress(label="65%", sections=[{"value": 65, "color": "blue"}]),
                    dmc.Slider(id="dmc-showcase-slider", value=50, min=0, max=100, labelAlwaysOn=True),
                    dmc.RangeSlider(id="dmc-showcase-range", value=[25, 75], min=0, max=100),
                    dmc.Rating(id="dmc-showcase-rating", value=3, count=5),
                    dmc.Loader(),
                ],
                style={"gap": GAP},
            ),
        ],
    )


def _pickers_card():
    """Date picker."""
    return _card_wrapper(
        "Pickers",
        [
            dmc.Stack(
                [
                    dmc.DatePickerInput(
                        id="dmc-showcase-date-picker",
                        label="Pick a date",
                        placeholder="Select date",
                        popoverProps={"opened": True},
                    ),
                ],
                style={"gap": GAP},
            ),
        ],
        style={"minHeight": "320px"},
    )


def _containers_display_card():
    """Card, Paper, ActionIcon, Avatar, Blockquote, Tooltip."""
    return _card_wrapper(
        "Containers & display",
        [
            dmc.Stack(
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
                    dmc.Flex(
                        [
                            dmc.ActionIcon("⚙", variant="filled", size="lg"),
                            dmc.ActionIcon("✎", variant="outline", size="md"),
                            dmc.ActionIcon("🗑", variant="subtle", size="sm"),
                        ],
                        gap="sm",
                    ),
                    dmc.Avatar("AB", radius="xl", color="blue"),
                    dmc.Blockquote(
                        "Use Blockquote to highlight a quote or callout.",
                        cite="— DMC docs",
                    ),
                    dmc.Tooltip(
                        dmc.Button("Hover me"),
                        label="Tooltip text",
                    ),
                ],
                style={"gap": GAP},
            ),
        ],
    )


def _form_card():
    """Form inputs and submit."""
    return _card_wrapper(
        "Form",
        [
            dmc.Stack(
                [
                    dmc.TextInput(label="Email", placeholder="your@email.com"),
                    dmc.PasswordInput(label="Password", placeholder="Enter password"),
                    dmc.TextInput(label="Text", placeholder="Placeholder"),
                    dmc.NumberInput(label="Number", value=42, min=0, max=100),
                    dmc.Select(
                        label="Select",
                        data=["Option 1", "Option 2", "Option 3"],
                        value="Option 1",
                    ),
                    dmc.MultiSelect(
                        label="Multi select",
                        data=["Item 1", "Item 2", "Item 3"],
                        value=["Item 1"],
                        placeholder="Pick items",
                    ),
                    dmc.Textarea(label="Text area", placeholder="Multi-line text…", minRows=4),
                    dmc.RadioGroup(
                        label="Radio group",
                        children=[
                            dmc.Radio("Option A", value="a"),
                            dmc.Radio("Option B", value="b"),
                            dmc.Radio("Option C", value="c"),
                        ],
                        value="a",
                    ),
                    dmc.SegmentedControl(
                        data=[{"label": "A", "value": "a"}, {"label": "B", "value": "b"}, {"label": "C", "value": "c"}],
                        value="a",
                    ),
                    dmc.ChipGroup(
                        [
                            dmc.Chip("Chip 1", value="1", checked=False),
                            dmc.Chip("Chip 2", value="2", checked=True),
                            dmc.Chip("Chip 3", value="3", checked=False),
                        ],
                        value=["2"],
                    ),
                    dmc.Checkbox(label="Checkbox", checked=False),
                    dmc.Switch(label="Switch", checked=False),
                    dmc.Button("Sign in", variant="filled"),
                ],
                style={"gap": GAP},
            ),
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
