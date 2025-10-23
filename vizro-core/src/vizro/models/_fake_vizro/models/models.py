## Notes from A
"""Fake Vizro models.

This file illustrates how we can do revalidate_instances="always" and convert every field that's a Vizro model into a
discriminated union even if it has only one type to begin with (e.g. pages: list[Page]).
We forget about add_type and trying to generate a "correct" schema. Anything that's a custom model must stay as it is
and so be validated as Any. This sounds bad but is actually ok by me since the custom model itself performs the validation
it needs. NO - SEE BELOW AAARGH, this is probably not ok :( But I think we can figure it out.
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
  We could keep with the current type field system if we wanted to but I don't see any adnnatage in doing so.
Disadvantages:
- feels very heavy handed/ugly - JSON schema becomes a mess (though arguably more accurate), API docs get messier
- AAAARGH just realised another problem that's obvious and I didn't think of before. As soon as we have Any then you
could e.g. do Dashboard(pages=[graph]) and validation would pass when it shouldn't. This seems very bad for
Vizro-MCP and life in general. How can we prevent this but still allow custom components to be injected anywhere? Do we
force custom components to have type explicitly specified as "custom_component" instead of just taking it from the class name?
Or we could maintain a list of built-in tags and throw error if the tag matches one of those when it shouldn't to stop
e.g. Graph being used as a Page. Probably the explicit type being specified is best. We can manage this by
distinguishing our built-in models from user-created ones e.g. just by assigning all of ours an explicit type that
custom components wouldn't specify or checking the import path, etc. So overall this is probably not disastrous,
we should be able to validate well enough. The below code doesn't demonstrate this and will work for Dashboard(
pages=[graph]).

Notes:
- we don't have (or arguably need) a way of updating the schema at all. While you can't add specific types to the schema
any more, arguably the "custom" placeholder is just a general "injection point" for arbitrary types (a bit like our
extra field).
- there's no way to do custom component from YAML at all. Previously this was possible but completely undocumented.
Remaining challenges:
- will the copy on model revalidate cause us real problems in the model manager? As in last post of
https://github.com/pydantic/pydantic/issues/7608. Not worried about tests breaking so long as things work in practice
(and we understand why) since we can fix tests later.
- how to solve the new AAAARGH above, but I have some ideas here so don't worry about it too much. I am pretty
confident this is not a show-stopper and I can handle it when I'm back.
Alternative solution:
- drop revalidate_instances="always", but then need to go back to figure out how to handle model manager in a way that
builds tree correctly and avoids global variable. If we do go down that route then maybe from_attributes would be
useful for DashboardProxy.model_validate(Dashboard, from_attributes=True). See https://github.com/pydantic/pydantic/discussions/8933
IMPORTANT IDEA we shouldn't forget:
- if/when we have dashboard = model_validate(dashboard) in Vizro.build, the argument dashboard: Dashboard can be much more general
i.e. it could also be dict. This would make loading from yaml/json more direct which would be nice. We could also
introduce and argument json=True/False or context (to match pydantic), which is passed through to the pydantic
context (could even use model_validate_json instead?). This would allow us to handle differently the load from json vs.
Python configuration:
  - some things are possible from Python but not JSON
  - CapturedCallable parsing can be split more cleaning depending on pydantic context
- We can introduce this argument as mandatory for JSON and it's non breaking. Or we could just decide based on
whether dashboard is instance of Dashboard whether to parse and JSON or as Python. This would be breaking for current
examples but we could change to this behaviour in breaking release.

Additional notes MS:
- using SkipJsonSchema seems to be a good idea, as it cleans up the schema, which should not care about arbitrary Python extensions.
- using type = "" is not a good idea because it will hide the default from the JSON schema, which may (although not tested)
seriously confuse LLMs
- if __pydantic_init_subclass__ is not causing any trouble, then this might be the better solution


"""

from __future__ import annotations

import json
import re
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag
from pydantic.fields import FieldInfo
from pydantic.json_schema import SkipJsonSchema


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
    types.append(SkipJsonSchema[Annotated[Any, Tag("custom_component")]])

    print(types)

    # With a proper type field established, we could go back to a normal discriminator on this field
    # but this has the other consequence of needing a work-around for the stack mechanism of the model manager
    # see former implementation here: https://github.com/McK-Internal/vizro-internal/issues/2273
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


class VizroBaseModel(BaseModel):
    # Need to define some type here so that it's possible to use Graph from yaml without raising an error that
    # type is unexpected extra argument (unless we relax to extra="allow"). It exists on all models but we never need
    # to explicitly define it for any models. For dashboard configuration it's only ever specified in YAML config.
    type: str = Field(default="")
    model_config = ConfigDict(
        extra="forbid",  # Good for spotting user typos and being strict.
        validate_assignment=True,  # Run validators when a field is assigned after model instantiation.
        revalidate_instances="always",
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Automatically set the type field as a Literal with the snake_case class name for each subclass.

        This is called by Pydantic after basic class initialization, ensuring model_fields is available.
        """
        super().__pydantic_init_subclass__(**kwargs)

        # Get the snake_case class name
        class_name = camel_to_snake(cls.__name__)

        # Dynamically create Literal type for this specific class
        literal_type = Literal[class_name]  # type: ignore[misc]

        # Update the type annotation in the class
        cls.__annotations__["type"] = literal_type

        # Update the field info with the new annotation and default
        type_field: FieldInfo = cls.model_fields["type"]  # type: ignore[index]
        type_field.annotation = literal_type
        type_field.default = class_name

        # Rebuild the model to ensure Pydantic updates its schema with the new Literal type
        cls.model_rebuild(force=True)

    # @model_validator(mode="before")
    # @classmethod
    # def _set_type_default(cls, data: Any) -> Any:
    #     """Set the type field to the snake_case class name if not already set."""
    #     if isinstance(data, dict):
    #         # For both dict-based initialization (e.g., from YAML/JSON) and Python instantiation
    #         if "type" not in data or not data["type"]:
    #             data = {**data, "type": camel_to_snake(cls.__name__)}
    #     return data


class Graph(VizroBaseModel):
    figure: str


class Card(VizroBaseModel):
    text: str


class Page(VizroBaseModel):
    title: str
    # Example of field where there's multiple options so it's already a real discriminated union.
    components: list[make_discriminated_union(Graph, Card)]


class Dashboard(VizroBaseModel):
    # Example of field where there's really only one option that's built-in but we need to make it a discriminated union.
    # This will make automated API docstrings much worse but we can explain it somewhere...
    pages: list[make_discriminated_union(Page)]


if __name__ == "__main__":
    """
TODOs Maxi:
- build in MM
- check for model copy
- check for json schema
- serialization/deserialization

"""
    print("=== Graph Schema ===")
    print(json.dumps(Graph.model_json_schema(), indent=2))
    graph = Graph(type="graph", figure="a")
    print(json.dumps(graph.model_dump(exclude_unset=True, exclude_defaults=True), indent=2))

    # print("\n=== Card Schema ===")
    # print(json.dumps(Card.model_json_schema(), indent=2))
    # print("\n=== Page Schema ===")
    # print(json.dumps(Page.model_json_schema(), indent=2))
    print("\n=== Dashboard Schema ===")
    print(json.dumps(Dashboard.model_json_schema(), indent=2))

    #####
    # print("=== Card Vizro===")
    # from vizro.models import Card

    # card = Card(text="a")
    # print(json.dumps(Card.model_json_schema(), indent=2))
    # print(json.dumps(card.model_dump(exclude_unset=True), indent=2))
