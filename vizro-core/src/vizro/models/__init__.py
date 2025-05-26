# Keep these imports at the top to avoid circular imports since they're used in other models.
from ._base import VizroBaseModel  # noqa: I001
from ._tooltip import Tooltip
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
from ._grid import Layout, Grid
from ._page import Page
from ._flex import Flex

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
    "Flex",
    "Graph",
    "Grid",
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
    "Tooltip",
    "VizroBaseModel",
]

# To resolve ForwardRefs we need to import a few more things that are not part of the vizro.models namespace.
# We rebuild all the models even if it's not strictly necessary so that if pydantic changes how model_rebuild works
# we won't end up with unresolved references.
from vizro.actions import export_data, filter_interaction
from vizro.actions._filter_action import _filter
from vizro.actions._on_page_load import _on_page_load
from vizro.actions._parameter_action import _parameter

from ._action._actions_chain import ActionsChain
from ._components.form._text_area import TextArea
from ._components.form._user_input import UserInput

for model in [*__all__, "ActionsChain", "TextArea", "UserInput"]:
    globals()[model].model_rebuild()
