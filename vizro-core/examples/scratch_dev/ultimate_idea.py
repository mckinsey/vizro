"""This file illustrates how we can do revalidate_instances="always" and convert every field that's a Vizro model into a
discriminated union even if it has only one type to begin with (e.g. pages: list[Page]).

We forget about add_type and trying to generate a "correct" schema. Anything that's a custom model must stay as it is
and so be validated as Any. This sounds bad but is actually ok by me since the custom model itself performs the validation
it needs.

Advantages:
- we keep revalidate_instances="always", so model manager registration works and it feels correct
- no need for add_type anywhere any more! In future we can just remove this entirely. Maybe we can come up with a better
mechanism for modifying the schema in future.
- a custom component can always (a) subclass an existing model in the discriminated union or (b) directly subclass VizroBaseModel.
  Previously (a) and (b) worked for discriminated union fields (e.g. components: list[ComponentsType] but only
  (a) worked for non-discriminated union fields (e.g. pages: list[Page]).
- hopefully not breaking in any way.
- no need for the stupid type field in all models (this is handled automatically through discriminator function).
  We now rely on the class name to say whether it's a custom component or not rather than manually supplying the type.
  We could keep with the current type field system if we wanted to but I don't see any advnatage in doing so.

Disadvantages:
- feels very heavy handed/ugly - JSON schema becomes a mess (though arguably more accurate), API docs get messier

Notes:
- we don't have (or arguably need) a way of updating the schema at all. While you can't add specific types to the schema
any more, arguably the "custom" placeholder is just a general "injection point" for arbitrary types (a bit like our
extra field).
- there's no way to do custom component from YAML at all. Previously this was possible but completely undocumented.

Remaining challenges:
- will the copy on model revalidate cause us real problems in the model manager? As in last post of
https://github.com/pydantic/pydantic/issues/7608. Not worried about tests breaking so long as things work in practice
(and we understand why) since we can fix tests later.

Alternative solution:
- drop revalidate_instances="always", but then need to go back to figure out how to handle model manager in a way that
builds tree correctly and avoids global variable. If we do go down that route then maybe from_attributes would be
useful for DashboardProxy.model_validate(Dashboard, from_attributes=True). See https://github.com/pydantic/pydantic/discussions/8933
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Union

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag


class VizroBaseModel(BaseModel):
    # Need to define some type here so that it's possible to use Graph from yaml without raising an error that
    # type is unexpected extra argument (unless we relax to extra="allow"). It exists on all models but we never need
    # to explicitly define it for any models. For dashboard configuration it's only ever specified in YAML config.
    type: str = ""
    model_config = ConfigDict(
        extra="forbid",  # Good for spotting user typos and being strict.
        validate_assignment=True,  # Run validators when a field is assigned after model instantiation.
        revalidate_instances="always",
    )


# Written by ChatGPT
def camel_to_snake(name):
    # Add underscores before uppercase letters, then lowercase everything
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def make_discriminated_union(*args):
    # Build discriminated union out of types in args. Tags are just the snake case version of the class names.
    # Tag "custom_component" must validate as Any to keep its custom class.
    builtin_tags = [camel_to_snake(T.__name__) for T in args]
    types = [Annotated[T, Tag(builtin_tag)] for T, builtin_tag in zip(args, builtin_tags)]
    types.append(Annotated[Any, Tag("custom_component")])

    def discriminator(model):
        if isinstance(model, dict):
            # YAML configuration where no custom type possible
            if len(builtin_tags) == 1:
                # Fake discriminated union where there's only one option.
                # Coerce to that model (could raise error if type specified and doesn't match if we wanted to, doesn't
                # really matter)
                return builtin_tags[0]
            else:
                # Real discriminated union case need a type to be specified
                # If it's not specified then return None which wil raise a pydantic discriminated union error
                return model.get("type", None)
        elif isinstance(model, VizroBaseModel):
            # Find tag of supplied model.
            tag = camel_to_snake(type(model).__name__)
            if tag in builtin_tags:
                # It's one of the expected ones, so validate it to that type.
                return tag
            else:
                # It's a custom component so validate as Any.
                return "custom_component"
        else:
            raise ValueError("something")

    return Annotated[Union[tuple(types)], Field(discriminator=Discriminator(discriminator))]


########################################################################################################################
# Defined in Vizro framework
class Dashboard(VizroBaseModel):
    # Example of field where there's really only one option that's built-in but we need to make it a discriminated union.
    # This will make automated API docstrings much worse but we can explain it somewhere...
    pages: list[make_discriminated_union(Page)]


# Defined in Vizro framework
class Page(VizroBaseModel):
    title: str
    # Example of field where there's multiple options so it's already a real discriminated union.
    components: list[make_discriminated_union(Graph, Card)]


# Defined in Vizro framework
class Graph(VizroBaseModel):
    figure: str


# Defined in Vizro framework
class Card(VizroBaseModel):
    text: str


# User defined
class CustomPage(Page):
    # Allow int
    title: int


class CustomGraph(Graph):
    figure: int


# If the above custom components subclass VizroBaseModel instead of Page/Graph then behaviour should be the same (
# unlike it is now).
graph_1 = Graph(figure="a")
custom_graph_1 = CustomGraph(figure=2)

graph_2 = Graph(figure="a")
custom_graph_2 = CustomGraph(figure=2)

page = Page(title="Title", components=[graph_1, custom_graph_1])
custom_page = CustomPage(title=2, components=[graph_2, custom_graph_2])

# No add_type needed anywhere!!

dashboard = Dashboard(pages=[page, custom_page])
dashboard = Dashboard.model_validate(dashboard)

assert type(dashboard.pages[0]) is Page
assert type(dashboard.pages[1]) is CustomPage
assert type(dashboard.pages[0].components[0]) is Graph
assert type(dashboard.pages[0].components[1]) is CustomGraph
assert type(dashboard.pages[1].components[0]) is Graph
assert type(dashboard.pages[1].components[1]) is CustomGraph

###
# YAML configuration
# Must have type specified since it's a real discriminated union:
graph_1 = dict(figure="a", type="graph")
# Can't specify type since it's not a real discriminated union. There's no way of doing a custom component like this
# (this is currently possible thanks to add_type but in docs we say it's not possible so it's ok to break).
page = dict(title="Title", components=[graph_1])

dashboard = Dashboard(pages=[page])
dashboard = Dashboard.model_validate(dashboard)

assert type(dashboard.pages[0]) is Page
assert type(dashboard.pages[0].components[0]) is Graph
