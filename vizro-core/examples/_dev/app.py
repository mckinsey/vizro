import json
from datetime import date
from enum import Enum
from typing import Literal, Any

import dash_mantine_components as dmc
from dash import MATCH, Dash, Input, Output, _dash_renderer, callback
from pydantic import BaseModel, Field, ValidationError

from dash_pydantic_form import FormSection, ModelForm, Sections, fields, ids
import vizro.models as vm
from dash import html

class Office(Enum):
    """Office enum."""

    AU = "au"
    FR = "fr"
    UK = "uk"


class Species(Enum):
    """Species enum."""

    CAT = "cat"
    DOG = "dog"


class Metadata(BaseModel):
    """Metadata model."""

    languages: list[Literal["fr", "en", "sp", "cn"]] = Field(title="Languages spoken", default_factory=list)
    siblings: int | None = Field(title="Siblings", default=None)


class Pet(BaseModel):
    """Pet model."""

    name: str = Field(title="Name", description="Name of the pet")
    species: Species = Field(title="Species", description="Species of the pet")
    dob: date | None = Field(title="Date of birth", description="Date of birth of the pet", default=None)
    alive: bool = Field(title="Alive", description="Is the pet alive", default=True)


class HomeOffice(BaseModel):
    """Home office model."""

    type: Literal["home_office"]
    has_workstation: bool = Field(title="Has workstation", description="Does the employee have a suitable workstation")


class WorkOffice(BaseModel):
    """Work office model."""

    type: Literal["work_office"]
    commute_time: int = Field(title="Commute time", description="Commute time in minutes", ge=0)


class Employee(BaseModel):
    """Employee model."""

    name: str = Field(title="Name", description="Name of the employee")
    age: int = Field(title="Age", description="Age of the employee, starting from their birth")
    mini_bio: str | None = Field(title="Mini bio", description="Short bio of the employee", default=None)
    joined: date = Field(title="Joined", description="Date when the employee joined the company")
    office: Office = Field(title="Office", description="Office of the employee")
    metadata: Metadata | None = Field(title="Employee metadata", default=None)
    location: HomeOffice | WorkOffice | None = Field(title="Work location", default=None, discriminator="type")
    pets: list[Pet] = Field(title="Pets", description="Employee pets", default_factory=list)


class Form(vm.VizroBaseModel):
    """New custom component `Jumbotron`."""

    type: Literal["form"] = "form"
    model: Any

    def build(self):
        return html.Div(
            [
                ModelForm(self.model, "foo", "bar")
            ]
        )




vm.Page.add_type("components", Form)


@callback(
    Output("card", "children"),
    Input(ModelForm.ids.main("foo", "bar"), "data"),
)
def display(form_data):
    """Display form data."""
    children = str(json.dumps(form_data, indent=2))
    return children

page = vm.Page(
    title="Custom Component",
    components=[
        Form(
            model=Employee,
        ),
        vm.Card(id = "card",text = "This is the output")
    ],
    layout=vm.Layout(grid = [[0,1]]),
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    from vizro import Vizro
    # form = ModelForm(Employee, "foo", "bar")
    # app.run_server(debug=True)
    Vizro().build(dashboard).run()
