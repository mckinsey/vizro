from dataclasses import dataclass
from typing import Literal


@dataclass
class Component:
    type: Literal["ag_grid", "card", "graph"]


@dataclass
class Control:
    type: Literal["filter", "parameter"]
