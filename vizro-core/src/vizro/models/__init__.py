# Keep this import at the top to avoid circular imports since it's used in every model.
from ._base import VizroBaseModel  # noqa: I001
from ._action import Action
from ._components import Card, Graph, Table
from ._components.form import Button, Checklist, Dropdown, RadioItems, RangeSlider, Slider
from ._controls import Filter, Parameter
from ._navigation.accordion import Accordion
from ._navigation.navigation import Navigation
from ._navigation.nav_bar import NavBar
from ._navigation.nav_item import NavItem
from ._dashboard import Dashboard
from ._layout import Layout
from ._page import Page

Page.update_forward_refs(
    Button=Button, Card=Card, Filter=Filter, Graph=Graph, Parameter=Parameter, Table=Table, Accordion=Accordion
)
Navigation.update_forward_refs(Accordion=Accordion, NavBar=NavBar, NavItem=NavItem)
Dashboard.update_forward_refs(Page=Page, Navigation=Navigation)
NavBar.update_forward_refs(NavItem=NavItem)
NavItem.update_forward_refs(Accordion=Accordion)

# Please keep alphabetically ordered
__all__ = [
    "Accordion",
    "Action",
    "Button",
    "Card",
    "Checklist",
    "Dashboard",
    "Dropdown",
    "Filter",
    "Graph",
    "Layout",
    "NavBar",
    "NavItem",
    "Navigation",
    "Page",
    "Parameter",
    "RadioItems",
    "RangeSlider",
    "Slider",
    "Table",
    "VizroBaseModel",
]
