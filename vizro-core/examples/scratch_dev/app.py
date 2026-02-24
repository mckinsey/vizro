"""Dev app to try things out."""

from typing import Literal

from dash import html
import dash_mantine_components as dmc
import vizro.models as vm
from vizro import Vizro
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

# Shared layout constants
GAP = "20px"
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
        """Build layout: container with a grid of DMC showcase cards."""
        return html.Div(
            id=self.id,
            children=dmc.Container(
                [
                    dmc.Grid(
                        [
                            dmc.GridCol(span=6, children=_sample_components_card()),
                            dmc.GridCol(span=6, children=_pickers_card()),
                            dmc.GridCol(span=6, children=_typography_card()),
                            dmc.GridCol(span=6, children=_navigation_card()),
                            dmc.GridCol(span=6, children=_form_card()),
                            dmc.GridCol(span=6, children=_progress_containers_card()),
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
                    dmc.Flex(
                        [
                            dmc.ActionIcon("✎", variant="filled", size="lg"),
                            dmc.ActionIcon("✎", variant="outline", size="md"),
                            dmc.ActionIcon("✎", variant="subtle", size="sm"),
                        ],
                        gap="sm",
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
                    dmc.Divider(variant="solid"),
                    _section_label("Breadcrumbs"),
                    dmc.Breadcrumbs(
                        children=[
                            dmc.Anchor("Home", href="#"),
                            dmc.Anchor("Docs", href="#"),
                            dmc.Anchor("Anchor", href="#"),
                        ],
                        separator="/",
                    ),
                    dmc.Divider(variant="solid"),
                    _section_label("NavLink"),
                    dmc.NavLink(label="Dashboard", href="#"),
                    dmc.NavLink(label="Settings", href="#", active=True),
                    dmc.Divider(variant="solid"),
                    _section_label("Pagination"),
                    dmc.Pagination(total=10, value=1, id="dmc-showcase-pagination"),
                    dmc.Divider(variant="solid"),
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
                    dmc.Divider(variant="solid"),
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
                    dmc.Divider(variant="solid"),
                    _section_label("Tabs"),
                    dmc.Tabs(
                        [
                            dmc.TabsList(
                                [
                                    dmc.TabsTab("Tab 1", value="tab1"),
                                    dmc.TabsTab("Tab 2", value="tab2"),
                                ],
                            ),
                            dmc.TabsPanel("Tab 1 content.", value="tab1"),
                            dmc.TabsPanel("Tab 2 content.", value="tab2"),
                        ],
                        value="tab1",
                    ),
                    dmc.Divider(variant="solid"),
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


def _progress_containers_card():
    """Progress, RingProgress, SemiCircleProgress, Sliders, Rating, Loader, BarChart, AreaChart."""
    _bar_data = [
        {"month": "Jan", "A": 120, "B": 80, "C": 60, "D": 40},
        {"month": "Feb", "A": 190, "B": 120, "C": 90, "D": 70},
        {"month": "Mar", "A": 90, "B": 150, "C": 110, "D": 85},
    ]
    _area_data = [
        {"date": "Mon", "X": 40, "Y": 60, "Z": 30, "W": 50},
        {"date": "Tue", "X": 55, "Y": 45, "Z": 65, "W": 35},
        {"date": "Wed", "X": 70, "Y": 80, "Z": 50, "W": 45},
    ]
    return _card_wrapper(
        "Progress, sliders & display",
        [
            dmc.Stack(
                [
                    _section_label("Progress & sliders"),
                    dmc.Progress(value=45),
                    dmc.Slider(id="dmc-showcase-slider", value=50, min=0, max=100, labelAlwaysOn=True),
                    dmc.RangeSlider(id="dmc-showcase-range", value=[25, 75], min=0, max=100),
                    dmc.Rating(id="dmc-showcase-rating", value=3, count=5),
                    dmc.Loader(),
                    _section_label("RingProgress"),
                    dmc.Group(
                        [
                            dmc.RingProgress(
                                label="65%",
                                sections=[{"value": 65, "color": "blue"}],
                            ),
                            dmc.RingProgress(
                                sections=[
                                    {"value": 40, "color": "cyan"},
                                    {"value": 30, "color": "orange"},
                                    {"value": 20, "color": "grape"},
                                ],
                            ),
                            dmc.RingProgress(
                                sections=[{"value": 40, "color": "yellow"}],
                                rootColor="gray",
                            ),
                        ],
                        gap="md",
                    ),
                    _section_label("SemiCircleProgress"),
                    dmc.Group(
                        [
                            dmc.SemiCircleProgress(
                                value=40,
                                size=100,
                                thickness=10,
                                label="40%",
                            ),
                            dmc.SemiCircleProgress(
                                value=70,
                                size=100,
                                thickness=10,
                                label="70%",
                                labelPosition="center",
                            ),
                        ],
                        gap="lg",
                    ),
                    _section_label("BarChart"),
                    dmc.BarChart(
                        h=180,
                        dataKey="month",
                        data=_bar_data,
                        series=[
                            {"name": "A", "color": "violet.6"},
                            {"name": "B", "color": "teal.6"},
                            {"name": "C", "color": "orange.6"},
                            {"name": "D", "color": "grape.6"},
                        ],
                        tickLine="y",
                        withXAxis=True,
                        withYAxis=True,
                    ),
                    _section_label("AreaChart"),
                    dmc.AreaChart(
                        h=180,
                        dataKey="date",
                        data=_area_data,
                        type="stacked",
                        series=[
                            {"name": "X", "color": "indigo.6"},
                            {"name": "Y", "color": "blue.6"},
                            {"name": "Z", "color": "cyan.6"},
                            {"name": "W", "color": "lime.6"},
                        ],
                        withXAxis=True,
                        withYAxis=True,
                    ),
                ],
                style={"gap": GAP},
            ),
        ],
    )


def _pickers_card():
    """Card and date range picker together in one card."""
    return _card_wrapper(
        "Card & pickers",
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
                    dmc.Divider(variant="solid"),
                    dmc.DatePickerInput(
                        id="dmc-showcase-date-picker",
                        type="range",
                        label="Pick a date range",
                        placeholder="Pick start and end date",
                        popoverProps={"opened": True},
                        value=["2024-01-01", "2024-01-15"],
                    ),
                ],
                style={"gap": GAP},
            ),
        ],
        style={"minHeight": "320px"},
    )


def _typography_card():
    """Title, Text, Highlight, List, Blockquote, CodeHighlight — typography components."""
    return _card_wrapper(
        "Typography",
        [
            dmc.Stack(
                [
                    _section_label("Title"),
                    dmc.Title("Title order 1", order=1),
                    dmc.Title("Title order 2", order=2),
                    dmc.Title("Title order 3", order=3),
                    _section_label("Text"),
                    html.Div(
                        [
                            dmc.Text("Extra small text", size="xs"),
                            dmc.Text("Small text", size="sm"),
                            dmc.Text("Default text", size="md"),
                            dmc.Text("Large text", size="lg"),
                            dmc.Text("Extra large text", size="xl"),
                            dmc.Text("Semi bold", fw=500),
                            dmc.Text("Bold", fw=700),
                            dmc.Text("Underlined", td="underline"),
                            dmc.Text("Red text", c="red"),
                            dmc.Text("Blue text", c="blue"),
                            dmc.Text("Gray text", c="gray"),
                            dmc.Text("Uppercase", tt="uppercase"),
                            dmc.Text("capitalized text", tt="capitalize"),
                            dmc.Text("Aligned to center", ta="center"),
                            dmc.Text("Aligned to right", ta="right"),
                        ],
                        style={"display": "flex", "flexDirection": "column", "gap": "4px"},
                    ),
                    _section_label("Highlight"),
                    dmc.Highlight(
                        "Highlight this, definitely this and also this!",
                        highlight="this",
                    ),
                    dmc.Highlight(
                        "Highlight this, definitely this and also that!",
                        highlight=["this", "that"],
                        color="lime",
                    ),
                    _section_label("List"),
                    dmc.List(
                        [
                            dmc.ListItem(
                                dmc.Text(
                                    [
                                        "Join our ",
                                        dmc.Anchor(
                                            "Discord",
                                            href="https://discord.gg/KuJkh4Pyq5",
                                            underline=False,
                                        ),
                                        " Community.",
                                    ]
                                ),
                            ),
                            dmc.ListItem("Install python virtual environment."),
                            dmc.ListItem("Add your component to the showcase."),
                        ],
                    ),
                    dmc.List(
                        type="ordered",
                        children=[
                            dmc.ListItem("First ordered item"),
                            dmc.ListItem("Second ordered item"),
                            dmc.ListItem("Third ordered item"),
                        ],
                    ),
                    _section_label("Blockquote"),
                    dmc.Blockquote(
                        "Everything we hear is an opinion, not a fact. Everything we see is a perspective, not the truth.",
                        cite="— Marcus Aurelius, Meditations",
                    ),
                    _section_label("CodeHighlight"),
                    dmc.CodeHighlight(
                        language="python",
                        code="""# Kadane's Algorithm

class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        curr, summ = nums[0], nums[0]
        for n in nums[1:]:
            curr = max(n, curr + n)
            summ = max(summ, curr)
        return summ""",
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
                    dmc.Divider(variant="solid"),
                    dmc.RadioGroup(
                        label="Radio group",
                        children=[
                            dmc.Radio("Option A", value="a"),
                            dmc.Radio("Option B", value="b"),
                            dmc.Radio("Option C", value="c"),
                        ],
                        value="a",
                    ),
                    dmc.Divider(variant="solid"),
                    dmc.SegmentedControl(
                        orientation="horizontal",
                        data=[
                            {"label": "A", "value": "a"},
                            {"label": "B", "value": "b"},
                            {"label": "C", "value": "c"},
                        ],
                        value="a",
                    ),
                    dmc.Divider(variant="solid"),
                    dmc.Flex(
                        [
                            dmc.ChipGroup(
                                multiple=False,
                                children=[
                                    dmc.Chip("Chip 1", value="1", checked=False),
                                    dmc.Chip("Chip 2", value="2", checked=True),
                                    dmc.Chip("Chip 3", value="3", checked=False),
                                ],
                                value=["2"],
                            ),
                        ],
                        gap="sm",
                        wrap="nowrap",
                    ),
                    dmc.Divider(variant="solid"),
                    dmc.Checkbox(label="Checkbox", checked=False),
                    dmc.Checkbox(label="Checkbox", checked=True),
                    dmc.Divider(variant="solid"),
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
