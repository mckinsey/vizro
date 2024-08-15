from typing import Any, List, Mapping, Optional, Set, Type, Union

try:
    from pydantic.v1 import BaseModel, Field, root_validator, validator
    from pydantic.v1.fields import SHAPE_LIST, ModelField
    from pydantic.v1.typing import get_args
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, validator
    from pydantic.fields import SHAPE_LIST, ModelField
    from pydantic.typing import get_args


from typing_extensions import Annotated

from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models._utils import (
    _concatenate_code,
    _dict_to_python,
    _extract_captured_callable_data_info,
    _extract_captured_callable_source,
)


class VizroBaseModel(BaseModel):
    """All models that are registered to the model manager should inherit from this class.

    Args:
        id (str): ID to identify model. Must be unique throughout the whole dashboard. Defaults to `""`.
            When no ID is chosen, ID will be automatically generated.

    """

    id: str = Field(
        "",
        description="ID to identify model. Must be unique throughout the whole dashboard."
        "When no ID is chosen, ID will be automatically generated.",
    )

    @validator("id", always=True)
    def set_id(cls, id) -> str:
        return id or model_manager._generate_id()

    @_log_call
    def __init__(self, **data: Any):
        """Adds this model instance to the model manager."""
        # Note this runs after the set_id validator, so self.id is available here. In pydantic v2 we should do this
        # using the new model_post_init method to avoid overriding __init__.
        super().__init__(**data)
        model_manager[self.id] = self

    @classmethod
    def add_type(cls, field_name: str, new_type: Type[Any]):
        """Adds a new type to an existing field based on a discriminated union.

        Args:
            field_name: Field that new type will be added to
            new_type: New type to add to discriminated union

        """

        def _add_to_discriminated_union(union):
            # Returning Annotated here isn't strictly necessary but feels safer because the new discriminated union
            # will then be annotated the same way as the old one.
            args = get_args(union)
            # args[0] is the original union, e.g. Union[Filter, Parameter]. args[1] is the FieldInfo annotated metadata.
            return Annotated[Union[args[0], new_type], args[1]]

        def _is_discriminated_union(field):
            # Really this should be done as follows:
            # return field.discriminator_key is not None
            # However, this does not work with Optional[DiscriminatedUnion]. See also TestOptionalDiscriminatedUnion.
            return hasattr(field.outer_type_, "__metadata__") and get_args(field.outer_type_)[1].discriminator

        field = cls.__fields__[field_name]
        sub_field = field.sub_fields[0] if field.shape == SHAPE_LIST else None

        if _is_discriminated_union(field):
            # Field itself is a non-optional discriminated union, e.g. selector: SelectorType or Optional[SelectorType].
            new_annotation = _add_to_discriminated_union(field.outer_type_)
        elif sub_field is not None and _is_discriminated_union(sub_field):
            # Field is a list of discriminated union e.g. components: List[ComponentType].
            new_annotation = List[_add_to_discriminated_union(sub_field.outer_type_)]  # type: ignore[misc]
        else:
            raise ValueError(
                f"Field '{field_name}' must be a discriminated union or list of discriminated union type. "
                "You probably do not need to call add_type to use your new type."
            )

        cls.__fields__[field_name] = ModelField(
            name=field.name,
            type_=new_annotation,
            class_validators=field.class_validators,
            model_config=field.model_config,
            default=field.default,
            default_factory=field.default_factory,
            required=field.required,
            final=field.final,
            alias=field.alias,
            field_info=field.field_info,
        )

        # We need to resolve all ForwardRefs again e.g. in the case of Page, which requires update_forward_refs in
        # vizro.models. The vm.__dict__.copy() is inspired by pydantic's own implementation of update_forward_refs and
        # effectively replaces all ForwardRefs defined in vizro.models.
        import vizro.models as vm

        cls.update_forward_refs(**vm.__dict__.copy())
        new_type.update_forward_refs(**vm.__dict__.copy())

    def dict(self, **kwargs):
        # Overwrite pydantic's own `dict` method to add __vizro_model__ to the dictionary.
        # To get exclude as an argument is a bit fiddly because this function is called recursively
        # inside pydantic, which sets exclude=None by default.
        if kwargs.get("exclude") is None:
            kwargs["exclude"] = self.__vizro_exclude_fields__()
        _dict = super().dict(**kwargs)
        # Inject __vizro_model__ into the dictionary - needed just for to_python.
        _dict["__vizro_model__"] = self.__class__.__name__
        return _dict

    # This is like pydantic's own __exclude_fields__ but safer to use (it looks like __exclude_fields__ no longer
    # exists in pydantic v2).
    # Root validators with pre=True are always included, even when exclude_default=True, and so this is needed
    # to potentially exclude fields set this way, like Page.id.
    def __vizro_exclude_fields__(self) -> Optional[Union[Set[str], Mapping[str, Any]]]:
        return None

    def _to_python(self, extra_imports: Optional[Set[str]] = None, extra_callable_defs: Set[str] = set()) -> str:
        """Converts a Vizro model to the Python code that would create it.

        Args:
            extra_imports: Extra imports to add to the Python code. Provide as a set of complete import strings.
            extra_callable_defs: Extra callable definitions to add to the Python code. Provide as a set of complete
                function definitions.

        Returns:
            str: Python code to create the Vizro model.

        """
        # Model
        model_dict = self.dict(exclude_unset=True)
        model_code = "model = " + _dict_to_python(model_dict)

        # Imports
        extra_imports_concat = "\n".join(extra_imports) if extra_imports else None

        # CapturedCallable definitions
        callable_defs_set = _extract_captured_callable_source() | extra_callable_defs
        callable_defs_concat = "\n".join(callable_defs_set) if callable_defs_set else None

        # Data Manager
        data_defs_list = _extract_captured_callable_data_info()
        data_defs_concat = "\n".join(data_defs_list) if data_defs_list else None

        return _concatenate_code(
            code=model_code,
            extra_imports=extra_imports_concat,
            callable_defs=callable_defs_concat,
            data_settings=data_defs_concat,
        )

    class Config:
        extra = "forbid"  # Good for spotting user typos and being strict.
        smart_union = True  # Makes unions work without unexpected coercion (will be the default in pydantic v2).
        validate_assignment = True  # Run validators when a field is assigned after model instantiation.
        copy_on_model_validation = "none"  # Don't copy sub-models. Essential for the model_manager to work correctly.


if __name__ == "__main__":
    import textwrap

    import vizro.models as vm
    import vizro.plotly.express as px
    from vizro import Vizro
    from vizro.actions import export_data
    from vizro.models.types import capture
    from vizro.tables import dash_ag_grid

    Vizro._reset()

    @capture("graph")
    def chart(data_frame, hover_data: Optional[List[str]] = None):
        return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)

    @capture("graph")
    def chart2(data_frame, hover_data: Optional[List[str]] = None):
        return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)

    page = vm.Page(
        title="Page 1",
        #     layout = vm.Layout(grid = [[0, 1],[2, 3], [4, 5]],row_min_height="100px"),
        components=[
            #         vm.Card(text="Foo"),
            vm.Graph(figure=px.bar("iris", x="sepal_width", y="sepal_length")),
                    vm.Graph(figure=chart(data_frame="iris")),
                    vm.Graph(figure=chart2(data_frame="iris")),
                    vm.AgGrid(figure=dash_ag_grid(data_frame="iris")),
            vm.Button(
                text="Export data",
                actions=[
                    vm.Action(function=export_data()),
                    vm.Action(function=export_data()),
                ],
            ),
        ],
            controls=[vm.Filter(column="species")],
    )

    dashboard = vm.Dashboard(title="Bar", pages=[page])

    extra_callable = textwrap.dedent(
        """    @capture("graph")
    def extra(data_frame, hover_data: Optional[List[str]] = None):
        return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)
    """
    )

    # print(dashboard.dict(exclude_unset=True))
    string = dashboard._to_python(
        extra_imports={"from typing import Optional,List"}, extra_callable_defs={extra_callable}
    )
    print(string)