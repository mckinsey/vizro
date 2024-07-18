from typing import Any, List, Type, Union, Dict, Mapping
from collections import defaultdict

try:
    from pydantic.v1 import BaseModel, Field, validator, root_validator
    from pydantic.v1.fields import SHAPE_LIST, ModelField
    from pydantic.v1.typing import get_args
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, validator, root_validator
    from pydantic.fields import SHAPE_LIST, ModelField
    from pydantic.typing import get_args

from black import FileMode, format_str
from typing_extensions import Annotated

from vizro.managers import model_manager
from vizro.models._models_utils import _log_call

def _update_selective(supplied: Any, defaults: Any, select_key: str) -> Any:
    if isinstance(supplied, Mapping) and isinstance(defaults, Mapping):
        supplied = defaultdict(dict, supplied)
        for default_key, default_value in defaults.items():
            if isinstance(default_value, Mapping):
                supplied[default_key] = _update_selective(supplied.get(default_key, {}), default_value,select_key)
            elif isinstance(default_value, list):
                if default_key not in supplied or not isinstance(supplied[default_key], list):
                    supplied[default_key] = default_value
                else:
                    for i, item in enumerate(default_value):
                        if i < len(supplied[default_key]) and isinstance(item, Mapping):
                            supplied[default_key][i] = _update_selective(supplied[default_key][i], item,select_key)
                        elif i >= len(supplied[default_key]):
                            supplied[default_key].append(item)
            elif default_key == select_key:
                supplied.setdefault(default_key, default_value)
            else:
                pass
        return dict(supplied)
    elif isinstance(supplied, list) and isinstance(defaults, list):
        for i, item in enumerate(defaults):
            if i < len(supplied) and isinstance(item, Mapping):
                supplied[i] = _update_selective(supplied[i], item,select_key)
            elif i >= len(supplied):
                supplied.append(item)
        return supplied
    else:
        return supplied


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
    model_name: str = Field("", description="Name of the model.")
    _private_attr: str = ""

    # @root_validator(pre=True)
    # def set_model_name(cls, values):
    #     if "title" not in values:
    #         return values

    #     values.setdefault("model_name", cls.__name__)
    #     return values

    @validator("id", always=True)
    def set_id(cls, id) -> str:
        return id or model_manager._generate_id()

    @validator("model_name",always=True)
    def set_model_name(cls, v) -> str:
        return cls.__name__

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

    @staticmethod
    def transform_dict(d):
        if isinstance(d, dict):
            if "model_name" in d:
                # Prepare the string format by extracting '_add_key' and other content
                model_name = d.pop("model_name")
                other_content = ", ".join(f"{key}={VizroBaseModel.transform_dict(value)}" for key, value in d.items())
                return f"{model_name}({other_content})"
            else:
                # Recurse through the dictionary
                return ", ".join(f"{key}={VizroBaseModel.transform_dict(value)}" for key, value in d.items())
        elif isinstance(d, list):
            # Recurse through the list, ensure it's formatted as a list but without quotes on strings
            return "[" + ", ".join(VizroBaseModel.transform_dict(item) for item in d) + "]"
        else:
            # Base case: if it's not a dictionary or list, return the item itself
            return repr(d)  # Use repr to ensure proper representation of strings and other data types

    def to_python(self):
        d = self.dict(exclude_defaults=True)
        d2 = self.dict(exclude_unset=True)
        d3 = _update_selective(d2,d,"model_name")
        # print(d3)
        return format_str(VizroBaseModel.transform_dict(d3), mode=FileMode(line_length=88))

    class Config:
        extra = "forbid"  # Good for spotting user typos and being strict.
        smart_union = True  # Makes unions work without unexpected coercion (will be the default in pydantic v2).
        validate_assignment = True  # Run validators when a field is assigned after model instantiation.
        copy_on_model_validation = "none"  # Don't copy sub-models. Essential for the model_manager to work correctly.


if __name__ == "__main__":
    import vizro.plotly.express as px
    from vizro.managers import data_manager
    from vizro.models import *


    from collections import defaultdict
    from typing import Any, Dict, Mapping
    # For the plot prints - needs to transfer somewhere

    # data_manager["iris"] = px.data.iris()

    page = Page(
        title="Page 1",
        components=[Card(text="Foo"), Graph(figure=px.bar("iris", x="sepal_width", y="sepal_length"))],
        controls=[Filter(column="species")],
    )

    dashboard = Dashboard(title="Bar", pages=[page])


    print(dashboard.to_python())
    # @capture("ag_grid")
    # def my_custom_aggrid(data_frame,chosen_columns: List[str]):
    #     """Custom ag_grid."""
    #     return AgGrid(
    #         columnDefs=[{"field": col} for col in chosen_columns], rowData=data_frame.to_dict("records")
    #     )



    # d00 = {
    #         "str0": "1",
    #         "str0_2": "2",
    #         }
    # d0 = {
    #         "str0": "1",
    #         "str0_2": "2",
    #         "model_name":"000",
    #         "nonesense":"42"
    #         }

    # d1 = {
    #     "str1": "foo",
    #     "str1_1": "bar",
    #     "dict1": {
    #         "str2": "baz",
    #         "str2_2": "boz"
    #         },
    #     "list1" : [d00]
    #     }

    # d2 = {
    #     "str1": "foo",
    #     "str1_1": "bar",
    #     "model_name":"XXX",
    #     "nonesense":"YYY",
    #     "dict1": {
    #         "str2": "baz",
    #         "str2_2": "boz",
    #         "model_name":"ZZZ",
    #         "nonesense":"ZZZ"
    #         },
    #     "list1":[d0]
    #     }
