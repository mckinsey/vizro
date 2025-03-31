# Keep this import at the top to avoid circular imports since it's used in every model.
from ._base import VizroBaseModel  # noqa: I001
from ._action import Action
from ._components import Card, Container, Graph, Text, Table, Tabs, Figure
from ._components import AgGrid
from ._components.form import Button, Checklist, DatePicker, Dropdown, RadioItems, RangeSlider, Slider
from ._controls import Filter, Parameter
from ._navigation.accordion import Accordion
from ._navigation.navigation import Navigation
from ._navigation.nav_bar import NavBar
from ._navigation.nav_link import NavLink
from ._dashboard import Dashboard
from ._layout import Layout
from ._page import Page


# Since pydantic==2.11.0 we need to rebuilt more than the Dashboard model
# The below model rebuilds are the minimal set of models that need to be rebuilt,
# presumably because they contain types that are not fully resolved during the initial build.
Dashboard.model_rebuild()
Page.model_rebuild()
Container.model_rebuild()
NavBar.model_rebuild()
NavLink.model_rebuild()
Navigation.model_rebuild()
Tabs.model_rebuild()


__all__ = [
    "Accordion",
    "Action",
    "AgGrid",
    "Button",
    "Card",
    "Checklist",
    "Container",
    "Dashboard",
    "DatePicker",
    "Dropdown",
    "Figure",
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
    "Tabs",
    "Text",
    "VizroBaseModel",
]
