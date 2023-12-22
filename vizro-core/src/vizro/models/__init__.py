# Keep this import at the top to avoid circular imports since it's used in every model.
from ._base import VizroBaseModel  # noqa: I001
from ._action import Action
from ._components import Card, Container, Graph, Table
from ._components.form import Button, Checklist, Dropdown, RadioItems, RangeSlider, Slider
from ._controls import Filter, Parameter
from ._navigation.accordion import Accordion
from ._navigation.navigation import Navigation
from ._navigation.nav_bar import NavBar
from ._navigation.nav_link import NavLink
from ._dashboard import Dashboard
from ._layout import Layout
from ._page import Page

Container.update_forward_refs(Button=Button, Card=Card, Graph=Graph, Table=Table, Layout=Layout)
Page.update_forward_refs(
    Accordion=Accordion,
    Button=Button,
    Card=Card,
    Container=Container,
    Filter=Filter,
    Graph=Graph,
    Parameter=Parameter,
    Table=Table,
)
Navigation.update_forward_refs(Accordion=Accordion, NavBar=NavBar, NavLink=NavLink)
Dashboard.update_forward_refs(Page=Page, Navigation=Navigation)
NavBar.update_forward_refs(NavLink=NavLink)
NavLink.update_forward_refs(Accordion=Accordion)

# Please keep alphabetically ordered
__all__ = [
    "Accordion",
    "Action",
    "Button",
    "Card",
    "Container",
    "Checklist",
    "Dashboard",
    "Dropdown",
    "Filter",
    "Graph",
    "Layout",
    "NavBar",
    "NavLink",
    "Navigation",
    "Page",
    "Parameter",
    "RadioItems",
    "RangeSlider",
    "Slider",
    "Table",
    "VizroBaseModel",
]
