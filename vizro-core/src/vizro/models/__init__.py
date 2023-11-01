# Keep this import at the top to avoid circular imports since it's used in every model.
from ._base import VizroBaseModel  # noqa: I001
from ._action import Action
from ._components import Card, Graph, Table, Tabs, SubPage
from ._components.form import Button, Checklist, Dropdown, RadioItems, RangeSlider, Slider
from ._controls import Filter, Parameter
from ._navigation.navigation import Navigation
from ._dashboard import Dashboard
from ._layout import Layout
from ._page import Page

SubPage.update_forward_refs(Button=Button, Card=Card, Graph=Graph, Tabs=Tabs)
Tabs.update_forward_refs(SubPage=SubPage)
Page.update_forward_refs(
    Button=Button, Card=Card, Filter=Filter, Graph=Graph, Parameter=Parameter, Table=Table, Tabs=Tabs
)
Dashboard.update_forward_refs(Page=Page, Navigation=Navigation)

# Please keep alphabetically ordered
__all__ = [
    "Action",
    "Button",
    "Card",
    "Checklist",
    "Dashboard",
    "Dropdown",
    "Filter",
    "Graph",
    "Layout",
    "Navigation",
    "Page",
    "Parameter",
    "RadioItems",
    "RangeSlider",
    "Slider",
    "Table",
    "VizroBaseModel",
    "Tab",
    "Tabs",
]
