import logging
import textwrap
from typing import Annotated, Literal, Optional, Union

import pytest
from pydantic import (
    Field,
    FieldSerializationInfo,
    SerializerFunctionWrapHandler,
    ValidationError,
    field_validator,
    model_serializer,
    model_validator,
)

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data
from vizro.models.types import capture
from vizro.tables import dash_ag_grid


class ChildX(vm.VizroBaseModel):
    type: Literal["child_x"] = "child_x"


class ChildY(vm.VizroBaseModel):
    type: Literal["child_y"] = "child_y"


class ChildZ(vm.VizroBaseModel):
    type: Literal["child_Z"] = "child_Z"


class ChildWithForwardRef(vm.VizroBaseModel):
    type: Literal["child_with_forward_ref"] = "child_with_forward_ref"
    grandchild: "ChildXForwardRef" = None  # noqa: F821


# ChildType does not include ChildZ initially.
ChildType = Annotated[Union[ChildX, ChildY], Field(discriminator="type")]


# These parent classes must be done as fixtures so that each test gets a fresh, unmodified copy of the class.
@pytest.fixture()
def Parent():
    # e.g. Parameter.selector: SelectorType
    class _Parent(vm.VizroBaseModel):
        child: ChildType

    return _Parent


@pytest.fixture()
def ParentWithOptional():
    # e.g. Filter.selector: Optional[SelectorType]
    class _ParentWithOptional(vm.VizroBaseModel):
        child: Optional[ChildType]

    return _ParentWithOptional


@pytest.fixture()
def ParentWithList():
    # e.g. Page.controls: list[ControlType] and Page.components: list[ComponentType]
    class _ParentWithList(vm.VizroBaseModel):
        child: list[ChildType]

    return _ParentWithList


@pytest.fixture()
def ParentWithForwardRef():
    class _ParentWithForwardRef(vm.VizroBaseModel):
        child: Annotated[Union["ChildXForwardRef", "ChildYForwardRef"], Field(discriminator="type")]

    # TODO: [MS] This is how I would update the forward refs, but we should double check
    ChildXForwardRef = ChildX
    ChildYForwardRef = ChildY
    _ParentWithForwardRef.model_rebuild()
    return _ParentWithForwardRef


@pytest.fixture()
def ParentWithNonDiscriminatedUnion():
    class _ParentWithNonDiscriminatedUnion(vm.VizroBaseModel):
        child: Union[ChildX, ChildY]

    return _ParentWithNonDiscriminatedUnion


class TestDiscriminatedUnion:
    def test_no_type_match(self, Parent):
        child = ChildZ()
        with pytest.raises(
            ValidationError, match="'type' does not match any of the expected tags: 'child_x', 'child_y'"
        ):
            Parent(child=child)

    def test_add_type_model_instantiation(self, Parent):
        Parent.add_type("child", ChildZ)
        parent = Parent(child=ChildZ())
        assert isinstance(parent.child, ChildZ)

    def test_add_type_dict_instantiation(self, Parent):
        Parent.add_type("child", ChildZ)
        parent = Parent(child={"type": "child_Z"})
        assert isinstance(parent.child, ChildZ)


class TestOptionalDiscriminatedUnion:
    # Optional[ChildType] does not work correctly as a discriminated union - pydantic turns it into a regular union.
    # Hence the validation error messages are not as expected. The tests of add_type pass because in practice a
    # discriminated union is not actually needed to achieve the desired behavior. The union is still a regular one
    # even after add_type.
    @pytest.mark.xfail
    def test_no_type_match(self, ParentWithOptional):
        child = ChildZ()
        with pytest.raises(ValidationError, match="No match for discriminator 'type' and value 'child_Z'"):
            ParentWithOptional(child=child)

    # The current error message is the non-discriminated union one.
    def test_no_type_match_current_behaviour(self, ParentWithOptional):
        child = ChildZ()
        with pytest.raises(
            ValidationError, match="'type' does not match any of the expected tags: 'child_x', 'child_y'"
        ):
            ParentWithOptional(child=child)

    def test_add_type_model_instantiation(self, ParentWithOptional):
        ParentWithOptional.add_type("child", ChildZ)
        parent = ParentWithOptional(child=ChildZ())
        assert isinstance(parent.child, ChildZ)

    def test_add_type_dict_instantiation(self, ParentWithOptional):
        ParentWithOptional.add_type("child", ChildZ)
        parent = ParentWithOptional(child={"type": "child_Z"})
        assert isinstance(parent.child, ChildZ)


class TestListDiscriminatedUnion:
    def test_no_type_match(self, ParentWithList):
        child = ChildZ()
        with pytest.raises(
            ValidationError, match="'type' does not match any of the expected tags: 'child_x', 'child_y'"
        ):
            ParentWithList(child=[child])

    def test_add_type_model_instantiation(self, ParentWithList):
        ParentWithList.add_type("child", ChildZ)
        parent = ParentWithList(child=[ChildZ()])
        assert isinstance(parent.child[0], ChildZ)

    def test_add_type_dict_instantiation(self, ParentWithList):
        ParentWithList.add_type("child", ChildZ)
        parent = ParentWithList(child=[{"type": "child_Z"}])
        assert isinstance(parent.child[0], ChildZ)


class TestParentForwardRefDiscriminatedUnion:
    def test_no_type_match(self, ParentWithForwardRef):
        child = ChildZ()
        with pytest.raises(
            ValidationError, match="'type' does not match any of the expected tags: 'child_x', 'child_y'"
        ):
            ParentWithForwardRef(child=child)

    def test_add_type_model_instantiation(self, ParentWithForwardRef, mocker):
        # Make it as if these are in vizro.models so that update_forward_refs call in add_type works on them.
        mocker.patch.dict(vm.__dict__, {"ChildXForwardRef": ChildX, "ChildYForwardRef": ChildY})
        ParentWithForwardRef.add_type("child", ChildZ)
        parent = ParentWithForwardRef(child=ChildZ())
        assert isinstance(parent.child, ChildZ)

    def test_add_type_dict_instantiation(self, ParentWithForwardRef, mocker):
        # Make it as if these are in vizro.models so that update_forward_refs call in add_type works on them.
        mocker.patch.dict(vm.__dict__, {"ChildXForwardRef": ChildX, "ChildYForwardRef": ChildY})
        ParentWithForwardRef.add_type("child", ChildZ)
        parent = ParentWithForwardRef(child={"type": "child_Z"})
        assert isinstance(parent.child, ChildZ)


class TestChildWithForwardRef:
    def test_no_type_match(self, Parent):
        # TODO: [MS] I am not sure why this worked before, but in my understanding,
        # we need to define the forward ref before rebuilding the model that contains it.
        ChildXForwardRef = ChildX  # noqa: F841
        ChildWithForwardRef.model_rebuild()
        child = ChildWithForwardRef()
        with pytest.raises(
            ValidationError, match="'type' does not match any of the expected tags: 'child_x', 'child_y'"
        ):
            Parent(child=child)

    def test_add_type_model_instantiation(self, Parent, mocker):
        # Make it as if these are in vizro.models so that update_forward_refs call in add_type works on them.
        mocker.patch.dict(vm.__dict__, {"ChildXForwardRef": ChildX})
        Parent.add_type("child", ChildWithForwardRef)
        parent = Parent(child=ChildWithForwardRef(grandchild=ChildX()))
        assert isinstance(parent.child, ChildWithForwardRef) and isinstance(parent.child.grandchild, ChildX)

    def test_add_type_dict_instantiation(self, Parent, mocker):
        # Make it as if these are in vizro.models so that update_forward_refs call in add_type works on them.
        mocker.patch.dict(vm.__dict__, {"ChildXForwardRef": ChildX})
        Parent.add_type("child", ChildWithForwardRef)
        parent = Parent(child={"type": "child_with_forward_ref", "grandchild": {}})
        assert isinstance(parent.child, ChildWithForwardRef) and isinstance(parent.child.grandchild, ChildX)


def test_no_type_match(ParentWithNonDiscriminatedUnion):
    with pytest.raises(ValueError, match="Field 'child' must be a discriminated union"):
        ParentWithNonDiscriminatedUnion.add_type("child", ChildZ)


class Model(vm.VizroBaseModel):
    type: Literal["model"] = "model"


class ModelWithFieldSetting(vm.VizroBaseModel):
    type: Literal["exclude_model"] = "exclude_model"
    title: str = Field(description="Title to be displayed.")
    foo: Optional[str] = Field(default=None, description="Foo field.", validate_default=True)

    # Set a field with regular validator
    @field_validator("foo")
    @classmethod
    def set_foo(cls, foo: Optional[str]) -> str:
        return foo or "long-random-thing"

    # Set a field with a pre=True root-validator -->
    # # this will not be caught by exclude_unset=True
    @model_validator(mode="before")
    @classmethod
    def set_id(cls, values):
        if "title" not in values:
            return values

        values.setdefault("id", values["title"])
        return values

    # Exclude field when id is the same as title
    @model_serializer(mode="wrap")
    def _serialize_id(self, nxt: SerializerFunctionWrapHandler, info: FieldSerializationInfo):
        result = nxt(self)
        if info.context is not None and info.context.get("add_name", False):
            result["__vizro_model__"] = self.__class__.__name__
        if self.title == self.id:
            result.pop("id", None)
            return result
        return result


class TestDict:
    def test_dict_no_args(self):
        model = Model(id="model_id")
        assert model.model_dump() == {"id": "model_id", "type": "model"}

    def test_dict_exclude_unset(self):
        model = Model(id="model_id")
        assert model.model_dump(exclude_unset=True) == {"id": "model_id"}

    def test_dict_exclude_id(self):
        model = Model()
        assert model.model_dump(exclude={"id"}) == {"type": "model"}

    def test_dict_exclude_type(self):
        model = Model(id="model_id")
        assert model.model_dump(exclude={"type"}) == {"id": "model_id"}

    def test_dict_exclude_in_model_unset_with_and_without_context(self):
        model = ModelWithFieldSetting(title="foo")
        assert model.model_dump(context={"add_name": True}, exclude_unset=True) == {
            "title": "foo",
            "__vizro_model__": "ModelWithFieldSetting",
        }

    def test_dict_exclude_in_model_no_args_with_and_without_context(self):
        model = ModelWithFieldSetting(title="foo")
        assert model.model_dump(context={"add_name": True}) == {
            "title": "foo",
            "type": "exclude_model",
            "__vizro_model__": "ModelWithFieldSetting",
            "foo": "long-random-thing",
        }


@pytest.fixture
def page_builtin_actions():
    return vm.Page(
        title="Page 1",
        components=[
            vm.Graph(figure=px.bar("iris", x="sepal_width", y="sepal_length")),
            vm.Button(
                text="Export data",
                actions=[
                    vm.Action(function=export_data()),
                    vm.Action(function=export_data()),
                ],
            ),
        ],
    )


@pytest.fixture
def page_two_captured_callables():
    @capture("graph")
    def chart(data_frame, hover_data: Optional[list[str]] = None):
        return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)

    @capture("graph")
    def chart2(data_frame, hover_data: Optional[list[str]] = None):
        return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)

    return vm.Page(
        title="Page 1",
        components=[
            vm.Graph(figure=chart(data_frame="iris")),
            vm.Graph(figure=chart2(data_frame="iris")),
        ],
    )


@pytest.fixture
def chart_dynamic():
    function_string = textwrap.dedent(
        """
        @capture("graph")
        def chart_dynamic(data_frame, hover_data: Optional[list[str]] = None):
            return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)
        """
    )

    result = {}
    exec(function_string, globals(), result)
    return result["chart_dynamic"]


@pytest.fixture
def complete_dashboard():
    @capture("graph")
    def chart(data_frame, hover_data: Optional[list[str]] = None):
        return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)

    page = vm.Page(
        title="Page 1",
        layout=vm.Grid(grid=[[0, 1], [2, 3], [4, -1]], row_min_height="100px"),
        components=[
            vm.Card(text="Foo"),
            vm.Graph(figure=px.bar("iris", x="sepal_width", y="sepal_length")),
            vm.Graph(figure=chart(data_frame="iris")),
            vm.AgGrid(figure=dash_ag_grid(data_frame="iris")),
            vm.Button(
                text="Export data",
                actions=[
                    vm.Action(function=export_data()),
                    vm.Action(function=export_data()),
                ],
            ),
        ],
        controls=[
            vm.Filter(
                column="species",
                selector=vm.Dropdown(
                    options=[{"label": "Setosa", "value": "setosa"}, {"label": "Virginica", "value": "virginica"}]
                ),
            )
        ],
    )

    dashboard = vm.Dashboard(title="Bar", pages=[page])

    return dashboard


expected_card = """############ Imports ##############
import vizro.models as vm


########### Model code ############
model = vm.Card(text="Foo")
"""


expected_graph = """############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Graph(figure=px.bar(data_frame="iris", x="sepal_width", y="sepal_length"))
"""


expected_graph_with_callable = """############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
from vizro.models.types import capture
from typing import Optional


####### Function definitions ######
@capture("graph")
def chart(data_frame, hover_data: Optional[list[str]] = None):
    return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Graph(figure=chart(data_frame="iris"))
"""


expected_builtin_actions = """############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Page(
    components=[
        vm.Graph(figure=px.bar(data_frame="iris", x="sepal_width", y="sepal_length")),
        vm.Button(text="Export data", actions=[va.export_data(), va.export_data()]),
    ],
    title="Page 1",
)
"""


excepted_graph_dynamic = """############ Imports ##############
import vizro.models as vm


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Graph(figure=chart_dynamic(data_frame="iris"))
"""


extra_callable = """@capture("graph")
def extra(data_frame, hover_data: Optional[list[str]] = None):
    return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)
"""


expected_code_with_extra_callable = """############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
from vizro.models.types import capture


####### Function definitions ######
@capture("graph")
def extra(data_frame, hover_data: Optional[list[str]] = None):
    return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)


########### Model code ############
model = vm.Card(text="Foo")
"""

expected_complete_dashboard = """############ Imports ##############
import vizro.plotly.express as px
import vizro.tables as vt
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from typing import Optional


####### Function definitions ######
@capture("graph")
def chart(data_frame, hover_data: Optional[list[str]] = None):
    return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Dashboard(
    pages=[
        vm.Page(
            components=[
                vm.Card(text="Foo"),
                vm.Graph(
                    figure=px.bar(data_frame="iris", x="sepal_width", y="sepal_length")
                ),
                vm.Graph(figure=chart(data_frame="iris")),
                vm.AgGrid(figure=vt.dash_ag_grid(data_frame="iris")),
                vm.Button(
                    text="Export data", actions=[va.export_data(), va.export_data()]
                ),
            ],
            title="Page 1",
            layout=vm.Grid(grid=[[0, 1], [2, 3], [4, -1]], row_min_height="100px"),
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Dropdown(
                        options=[
                            {"label": "Setosa", "value": "setosa"},
                            {"label": "Virginica", "value": "virginica"},
                        ]
                    ),
                )
            ],
        )
    ],
    title="Bar",
)
"""


class TestPydanticPython:
    def test_to_python_basic(self):
        card = vm.Card(text="Foo")
        result = card._to_python()
        assert result == expected_card

    def test_to_python_data_manager(self):
        # Test if data manager code lines are included correctly in output
        graph = vm.Graph(figure=px.bar("iris", x="sepal_width", y="sepal_length"))
        result = graph._to_python()
        assert result == expected_graph

    def test_to_python_captured_callable_chart_plus_extra_imports(self):
        # Test if captured callable is included correctly in output
        # Test if extra imports are included correctly in output (typing yes, pandas no)
        @capture("graph")
        def chart(data_frame, hover_data: Optional[list[str]] = None):
            return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)

        graph = vm.Graph(figure=chart(data_frame="iris"))
        result = graph._to_python(extra_imports={"from typing import Optional", "import pandas as pd"})
        assert result == expected_graph_with_callable

    def test_to_python_two_captured_callable_charts(self, page_two_captured_callables):
        # Test if two captured callables are included. Note that the order in which they are included is not guaranteed.
        result = page_two_captured_callables._to_python()
        assert "def chart(data_frame, hover_data: Optional[list[str]] = None):" in result
        assert "def chart2(data_frame, hover_data: Optional[list[str]] = None):" in result

    def test_to_python_builtin_actions(self, page_builtin_actions):
        # Test if built-in actions are included correctly in output, ie no ActionsChain model
        result = page_builtin_actions._to_python()
        assert result == expected_builtin_actions

    def test_to_python_no_source_code(self, chart_dynamic, caplog):
        # Check if to_python works if the source code is not available - here chart_dynamic is undefined
        caplog.set_level(logging.INFO)

        graph = vm.Graph(figure=chart_dynamic(data_frame="iris"))
        result = graph._to_python()
        assert "Could not extract" in caplog.records[0].message
        assert result == excepted_graph_dynamic

    def test_to_python_with_extra_callable(self):
        # Test if callable is included correctly in output
        card = vm.Card(text="Foo")
        result = card._to_python(extra_callable_defs={extra_callable})
        assert result == expected_code_with_extra_callable

    def test_to_python_complete_dashboard(self, complete_dashboard):
        # Test more complete and nested model
        result = complete_dashboard._to_python(extra_imports={"from typing import Optional"})
        assert result == expected_complete_dashboard


class TestAddingDuplicateDiscriminator:
    def test_add_same_model(self, Parent):
        """Test whether adding same model re-defined avoids pydantic discriminator error."""

        class MultipleChild(vm.VizroBaseModel):
            type: Literal["derived"] = "derived"

        Parent.add_type("child", MultipleChild)

        class MultipleChild(vm.VizroBaseModel):
            type: Literal["derived"] = "derived"

        Parent.add_type("child", MultipleChild)

    def test_add_duplicate_type(self, Parent):
        """Test whether adding model of same type avoids pydantic discriminator error."""

        class MultipleChild(ChildX):
            pass

        Parent.add_type("child", MultipleChild)
