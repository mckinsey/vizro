from typing import List, Literal, Optional, Union

import pytest
from pydantic import Field, ValidationError
from typing_extensions import Annotated

import vizro.models as vm


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
    # e.g. Page.controls: List[ControlType] and Page.components: List[ComponentType]
    class _ParentWithList(vm.VizroBaseModel):
        child: List[ChildType]

    return _ParentWithList


@pytest.fixture()
def ParentWithForwardRef():
    class _ParentWithForwardRef(vm.VizroBaseModel):
        child: Annotated[Union["ChildXForwardRef", "ChildYForwardRef"], Field(discriminator="type")]  # noqa: F821

    _ParentWithForwardRef.update_forward_refs(ChildXForwardRef=ChildX, ChildYForwardRef=ChildY)
    return _ParentWithForwardRef


@pytest.fixture()
def ParentWithNonDiscriminatedUnion():
    class _ParentWithNonDiscriminatedUnion(vm.VizroBaseModel):
        child: Union[ChildX, ChildY]

    return _ParentWithNonDiscriminatedUnion


class TestDiscriminatedUnion:
    def test_no_type_match(self, Parent):
        child = ChildZ()
        with pytest.raises(ValidationError, match="No match for discriminator 'type' and value 'child_Z'"):
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
        with pytest.raises(ValidationError, match="unexpected value; permitted: 'child_x'"):
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
        with pytest.raises(ValidationError, match="No match for discriminator 'type' and value 'child_Z'"):
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
        with pytest.raises(ValidationError, match="No match for discriminator 'type' and value 'child_Z'"):
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
        child = ChildWithForwardRef()
        with pytest.raises(
            ValidationError, match="No match for discriminator 'type' and value 'child_with_forward_ref'"
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
