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
- if __pydantic_init_subclass__ is not causing any trouble, then this might be the better solution. EDIT: it is causeing trouble!!


"""

from __future__ import annotations

import random
import re
import uuid
from types import SimpleNamespace
from typing import TYPE_CHECKING, Annotated, Any, Literal, Optional, Self, Union

from nutree.typed_tree import TypedTree
from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    ModelWrapValidatorHandler,
    PrivateAttr,
    Tag,
    ValidatorFunctionWrapHandler,
    field_validator,
    model_validator,
)
from pydantic.fields import FieldInfo
from pydantic.json_schema import SkipJsonSchema
from pydantic_core.core_schema import ValidationInfo

rd = random.Random(0)

# Forward reference setup - creates circular dependency with actions.py
# Using TYPE_CHECKING avoids circular import at runtime, but causes forward ref issue
if TYPE_CHECKING:
    from vizro.models._fake_vizro.actions import ExportDataAction
# Don't define ExportDataAction at runtime - this will cause PydanticUndefinedAnnotation


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

    # print(types)

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
            return model.type
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

    id: Annotated[
        str,
        Field(
            default_factory=lambda: str(uuid.UUID(int=rd.getrandbits(128))),
            description="ID to identify model. Must be unique throughout the whole dashboard. "
            "When no ID is chosen, ID will be automatically generated.",
            validate_default=True,
        ),
    ]
    _tree: Optional[TypedTree] = PrivateAttr(None)  # initialised in model_after

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Automatically set the type field as a Literal with the snake_case class name for each subclass.

        This is called by Pydantic after basic class initialization, ensuring model_fields is available.
        If the user has explicitly set type="custom_component", that choice is respected.
        """
        super().__pydantic_init_subclass__(**kwargs)

        # Get the snake_case class name
        class_name = camel_to_snake(cls.__name__)

        # Get the type field
        type_field: FieldInfo = cls.model_fields["type"]
        # Check if defined as custom component - this would apply to non-Literal types, but I think that's ok
        is_custom_component = type_field.default == "custom_component"

        if not is_custom_component:
            default_value = class_name
        else:
            default_value = "custom_component"

        # Create literal type based on the default value - overwrite given type here!
        literal_type = Literal[default_value]

        # Update the type annotation in the class
        cls.__annotations__["type"] = literal_type

        # Update the field info with the new annotation and default
        type_field.annotation = literal_type
        type_field.default = default_value

        # Tried to skip model_rebuild() here as it will be called later in __init__.py after all imports complete
        # This avoids forward reference issues since ExportDataAction will be imported by then
        # The rebuild in __init__.py will update the schema with the Literal type, however not for all models

    @field_validator("*", mode="wrap")
    @classmethod
    def build_tree_field_wrap(
        cls,
        value: Any,
        handler: ValidatorFunctionWrapHandler,
        info: ValidationInfo,
    ) -> Any:
        if info.context is not None and "build_tree" in info.context:
            #### Field stack ####
            if "id_stack" not in info.context:
                info.context["id_stack"] = []
            if "field_stack" not in info.context:
                info.context["field_stack"] = []
            if info.field_name == "id":
                info.context["id_stack"].append(value)
            else:
                info.context["id_stack"].append(info.data.get("id", "no id"))
            info.context["field_stack"].append(info.field_name)
            #### Level and indentation ####
            # indent = info.context["level"] * " " * 4
            # info.context["level"] += 1

        #### Validation ####
        validated_stuff = handler(value)

        if info.context is not None and "build_tree" in info.context:
            #### Field stack ####
            info.context["id_stack"].pop()
            info.context["field_stack"].pop()

            #### Level and indentation ####
            # info.context["level"] -= 1
            # indent = info.context["level"] * " " * 4
        return validated_stuff

    @model_validator(mode="wrap")
    @classmethod
    def build_tree_model_wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self], info: ValidationInfo) -> Self:
        #### ID ####
        # Check Page ID case!
        # Even change way we set it in Page (path logic etc - ideally separate PR)
        # Leave page setting ID logic for now.
        model_id = "UNKNOWN_ID"
        if isinstance(data, dict):
            if "id" not in data or data["id"] is None:
                model_id = str(uuid.uuid4())
                data["id"] = model_id
                # print(f"    Setting id to {model_id}")
            elif isinstance(data["id"], str):
                model_id = data["id"]
                # print(f"    Using id {model_id}")
        elif hasattr(data, "id"):
            model_id = data.id
            # print(f"    Using id {model_id}")
        else:
            print("GRANDE PROBLEMA!!!")

        if info.context is not None and "build_tree" in info.context:
            #### Level and indentation ####
            if "level" not in info.context:
                info.context["level"] = 0
            indent = info.context["level"] * " " * 4
            info.context["level"] += 1

            #### Tree ####
            print(
                f"{indent}{cls.__name__} Before validation: {info.context['field_stack'] if 'field_stack' in info.context else 'no field stack'} with model id {model_id}"
            )

            if "parent_model" in info.context:
                # print("IF PARENT MODEL")
                info.context["tree"] = info.context["parent_model"]._tree
                tree = info.context["tree"]
                tree[info.context["parent_model"].id].add(
                    SimpleNamespace(id=model_id), kind=info.context["field_stack"][-1]
                )
                # info.context["tree"].print()
            elif "tree" not in info.context:
                # print("NO PARENT MODEL, NO TREE")
                tree = TypedTree("Root", calc_data_id=lambda tree, data: data.id)
                tree.add(SimpleNamespace(id=model_id), kind="dashboard")  # make this more general
                info.context["tree"] = tree
                # info.context["tree"].print()
            else:
                # print("NO PARENT MODEL, TREE")
                tree = info.context["tree"]
                # in words: add a node as children to the parent (so id one higher up), but add as kind
                # the field in which you currently are
                # ID STACK and FIELD STACK are different "levels" of the tree.
                tree[info.context["id_stack"][-1]].add(
                    SimpleNamespace(id=model_id), kind=info.context["field_stack"][-1]
                )
            # print("-" * 50)

        #### Validation ####
        validated_stuff = handler(data)

        if info.context is not None and "build_tree" in info.context:
            #### Replace placeholder nodes and propagate tree to all models ####
            info.context["tree"][validated_stuff.id].set_data(validated_stuff)
            validated_stuff._tree = info.context["tree"]

            #### Level and indentation ####
            info.context["level"] -= 1
            indent = info.context["level"] * " " * 4
            print(f"{indent}{cls.__name__} After validation: {info.context['field_stack']}")
        elif hasattr(data, "_tree") and data._tree is not None:
            #### Revalidation case: model already has a tree (e.g., during assignment) ####
            # Inherit the tree from the original instance
            validated_stuff._tree = data._tree
            # Update the tree node to point to the NEW validated instance
            validated_stuff._tree[validated_stuff.id].set_data(validated_stuff)
            print(f"--> Revalidation: Updated tree node for {validated_stuff.id} <--")

        return validated_stuff

    @classmethod
    # AM NOTE: name TBC.
    def from_pre_build(cls, data, parent_model, field_name):
        # Note this always adds new models to the tree. It's not currently possible to replace or remove a node.
        # It should work with any parent_model, but ideally we should only use it to make children of the calling
        # model, so that parent_model=self in the call (where self isn't the created model instance, it's the calling
        # model).
        # Since we have revalidate_instances = "always", calling model_validate on a single model will also execute
        # the validators on children models.
        # MS: On children models we have the problem that they would not be correctly added
        return cls.model_validate(
            data,
            context={
                "build_tree": True,
                "parent_model": parent_model,
                "field_stack": [field_name],
                "id_stack": [parent_model.id],
            },
        )


def make_actions_chain(self):
    for action in self.actions:
        action.action = action.action + " (from make_actions_chain)"
        action._parent_model = self
    return self


class Action(VizroBaseModel):
    action: str
    # This field uses ExportDataAction - creates the forward reference issue
    # Using string forward reference to trigger PydanticUndefinedAnnotation
    function: Union[str, ExportDataAction] = "default"

    _parent_model: VizroBaseModel = PrivateAttr()


class Graph(VizroBaseModel):
    figure: str
    actions: Optional[list[Action]]

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)


class Card(VizroBaseModel):
    text: str


class SubComponent(VizroBaseModel):
    y: str = "subcomponent"


class Component(VizroBaseModel):
    x: Union[str, list[SubComponent]]


class Page(VizroBaseModel):
    title: str
    # Example of field where there's multiple options so it's already a real discriminated union.
    components: list[make_discriminated_union(Graph, Card, Component)]

    def pre_build(self):
        print(f"Updating page {self.type}")
        if isinstance(self.components[0], Component) and self.components[0].x == "c1":
            self.components = [
                Component.from_pre_build(
                    {"x": "new c1!!!"},  # , SubComponent(y="another new c3")
                    self,
                    "components",
                )
            ]


class Dashboard(VizroBaseModel):
    # Example of field where there's really only one option that's built-in but we need to make it a discriminated union.
    # This will make automated API docstrings much worse but we can explain it somewhere...
    pages: list[make_discriminated_union(Page)]


if __name__ == "__main__":
    """
TODOs Maxi:
- test all combinations of yaml/python instantiations - DONE
- build in MM, see if pydantic_init_subclass is causing any problems - DONE
- check for model copy, do we loose private attributes still? Does it matter? - DONE
- check for json schema, does it look as nice as before? - DONE
- serialization/deserialization - DONE
- NEW: circular deps issue (see below)

NOT FULLY RESSOVLED
- what if we want to add normal component to other fields? (happens a lot!) - just use normal add_type?
- check if pre-build needs to overwrite/delete models
- check if we ever need to add sub models in pre-build, so far it only works for single model
- how much to we need to care about idempotency of validation? Is there a difference between pre and post
pre-build and/or pre and post tree building?

Circular dependency issue:
-------------------
Circular dependency: models.py ↔ actions.py
- models.py needs ExportDataAction for type annotation
- actions.py needs VizroBaseModel from models.py to inherit

The Problem:
- When Action class is defined, __pydantic_init_subclass__ runs
- It calls model_rebuild(force=True)
- Pydantic tries to evaluate Union[str, "ExportDataAction"]
- ExportDataAction not in namespace → PydanticUndefinedAnnotation

Resolution attempts:
- many unstable solutions suggested by Claude, did not try them all
- since we rebuild the models in __init__.py, we can just import ExportDataAction after the models have been rebuilt
- HOWEVER, this still creates incomplete schemas (some $defs in models do not update), as Vizro is highly hierarchical,
so MRO matters, and the order of resolving models needs to be carefully considered (essentially the old add_type problem)
See also: https://docs.pydantic.dev/latest/internals/resolving_annotations/#limitations-and-backwards-compatibility-concerns

==> Using __pydantic_init_subclass__ is not a viable solution if we want the schema of every model to be correct.
"""
