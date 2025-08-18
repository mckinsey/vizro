"""Maxi trial"""

from __future__ import annotations

import random
import uuid
from types import SimpleNamespace
from typing import Annotated, Any, List, Literal, Optional, Self, Union

from nutree.typed_tree import TypedTree
from pydantic import (
    BaseModel,
    Field,
    ModelWrapValidatorHandler,
    PrivateAttr,
    ValidatorFunctionWrapHandler,
    field_validator,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo

rd = random.Random(0)


class VizroBaseModel(BaseModel):
    id: Annotated[
        str,
        Field(
            default=None,
            description="ID to identify model. Must be unique throughout the whole dashboard."
            "When no ID is chosen, ID will be automatically generated.",
            validate_default=True,
        ),
    ]
    _tree: Optional[TypedTree] = PrivateAttr(None)  # initialised in model_after

    # @classmethod
    # def __pydantic_init_subclass__(cls, **kwargs):
    #     super().__pydantic_init_subclass__(**kwargs)
    #     print("==== PYDANTIC INIT SUBCLASS ====")

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print("==== INIT SUBCLASS ====")
        field_names = [f for f in cls.__annotations__.keys() if (not f.startswith("_") and f != "type")]
        # print("==== FIELDS ====")
        # print(field_names)

        if field_names:

            @field_validator(*field_names, mode="wrap")
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

            cls.build_tree_field_wrap = build_tree_field_wrap

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
                f"{indent}{cls.__name__} Before validation: {info.context['field_stack'] if 'field_stack' in info.context else 'no field stack'}"
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
        return cls.model_validate(
            data,
            context={
                "build_tree": True,
                "parent_model": parent_model,
                "field_stack": [field_name],
                "id_stack": [parent_model.id],
            },
        )

    class Config:
        revalidate_instances = "always"
        validate_assignment = True


class Dashboard(VizroBaseModel):
    title: str
    pages: list[Page]


class OtherComponent(VizroBaseModel):
    type: Literal["other_component"] = "other_component"
    x: str = "other_component"


class Component(VizroBaseModel):
    type: Literal["component"] = "component"
    x: Union[str, list[SubComponent]]


class SubComponent(VizroBaseModel):
    y: str = "subcomponent"


ComponentType = Annotated[Union[Component, OtherComponent], Field(discriminator="type")]
# ComponentType = Component


class Page(VizroBaseModel):
    title: str
    components: list[ComponentType]

    # @model_validator(mode="before")
    # @classmethod
    # def set_id(cls, values):
    #     if "title" not in values:
    #         return values

    #     values.setdefault("id", values["title"])
    #     return values

    def pre_build(self):
        print(f"Updating page {self=}")

        if self.components[0].x == "c3":
            # Works on nested things without doing from_pre_build on each! SubComponent is just a "regular"
            # SubComponent()
            self.components = [
                Component.from_pre_build(
                    {"x": [SubComponent(y="new c3"), SubComponent(y="another new c3")]},
                    self,
                    "components",
                )
            ]


# It shouldn't matter how you get to this point - with pydantic models like Dashboard() or not. Since "build_tree"
# won't be set in the validation context, nothing will modify the tree.
dashboard_data = {
    "title": "dashboard_title",
    "pages": [
        {
            "components": [
                {"x": "c1", "type": "component"},
                {
                    "x": [{}],
                    "type": "component",
                },
            ],
            "title": "page_1",
        },
        {"components": [{"x": "c3", "type": "component"}], "title": "page_2"},
    ],
}

# "build_tree": True has to be explicitly specified to o build the tree, so that users can still call model_validate()
# themselves without needing to specify "build_tree": False.
dashboard = Dashboard.model_validate(dashboard_data, context={"build_tree": True})

# a single shared tree:
assert dashboard._tree is dashboard.pages[0]._tree
# print("==== The tree ====")
# print(dashboard.pages[0]._tree.print())
# print(dashboard.pages[0].id)
# print("---")
# dashboard.pages[0]._tree.print()
# print()
dashboard._tree.print()

# Haven't thought about the order of these operations yet, but from tree creation point of view it shouldn't make a
# difference any more!!
print("-" * 50)
for page in dashboard.pages:
    page.pre_build()

# print()
# # The tree is still a single shared one, even once it's modified.
assert dashboard._tree is dashboard.pages[0]._tree
# assert dashboard._tree is dashboard.pages[1]._tree
# dashboard._tree.print()

"""
BIG QUESTIONS:
- does it work on Vizro itself? Can we used TypedTree with model.id automatically. If there's bugs here then report 
them
- will ordering of validators in subclasses break stuff here? Shouldn't interfere in any way I think since this tree 
stuff is independent of everything else.
- does rerunning validators cause us problems? Probably not.
- do we want validate_assignment=True or not?
- can we do pre_build itself using model_validate with context={"pre_build": True}. Is this actually useful in any 
way compared to iterating through tree? Probably not as have less control over ordering. Would still write code in 
pre_build method. But advantage might be that all pre_builds run iteratively automatically when created.

Ideal world:

"""

### https://docs.python.org/3/howto/annotations.html
