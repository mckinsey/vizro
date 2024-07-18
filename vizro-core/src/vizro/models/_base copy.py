from typing import Any, List, Type, Union

try:
    from pydantic.v1 import BaseModel, Field, validator
    from pydantic.v1.fields import SHAPE_LIST, ModelField
    from pydantic.v1.typing import get_args, is_namedtuple
    from pydantic.v1.utils import ROOT_KEY, ValueItems, sequence_like
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, validator
    from pydantic.fields import SHAPE_LIST, ModelField
    from pydantic.typing import get_args

from enum import Enum

from typing_extensions import Annotated, no_type_check, Optional

from vizro.managers import model_manager
from vizro.models._models_utils import _log_call


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


    # @classmethod
    # @no_type_check
    # def _get_value(
    #     cls,
    #     v: Any,
    #     to_dict: bool,
    #     by_alias: bool,
    #     include: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']],
    #     exclude: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']],
    #     exclude_unset: bool,
    #     exclude_defaults: bool,
    #     exclude_none: bool,
    # ) -> Any:
    #     if isinstance(v, BaseModel):
    #         _add_key = "_add_key"
    #         _add_val = v.__class__.__name__
    #         if to_dict:
    #             v_dict = v.dict(
    #                 by_alias=by_alias,
    #                 exclude_unset=exclude_unset,
    #                 exclude_defaults=exclude_defaults,
    #                 include=include,
    #                 exclude=exclude,
    #                 exclude_none=exclude_none,
    #             )
    #             if ROOT_KEY in v_dict:
    #                 return v_dict[ROOT_KEY]
    #             # TODO!: Need to add ability to differentiate when to include the object name in the dict and when not to!!!
    #             v_dict[_add_key] = _add_val
    #             return v_dict
    #         else:
    #             return v.copy(include=include, exclude=exclude)
    #
    #     value_exclude = ValueItems(v, exclude) if exclude else None
    #     value_include = ValueItems(v, include) if include else None
    #
    #     if isinstance(v, dict):
    #         return {
    #             k_: cls._get_value(
    #                 v_,
    #                 to_dict=to_dict,
    #                 by_alias=by_alias,
    #                 exclude_unset=exclude_unset,
    #                 exclude_defaults=exclude_defaults,
    #                 include=value_include and value_include.for_element(k_),
    #                 exclude=value_exclude and value_exclude.for_element(k_),
    #                 exclude_none=exclude_none,
    #             )
    #             for k_, v_ in v.items()
    #             if (not value_exclude or not value_exclude.is_excluded(k_))
    #             and (not value_include or value_include.is_included(k_))
    #         }
    #
    #     elif sequence_like(v):
    #         seq_args = (
    #             cls._get_value(
    #                 v_,
    #                 to_dict=to_dict,
    #                 by_alias=by_alias,
    #                 exclude_unset=exclude_unset,
    #                 exclude_defaults=exclude_defaults,
    #                 include=value_include and value_include.for_element(i),
    #                 exclude=value_exclude and value_exclude.for_element(i),
    #                 exclude_none=exclude_none,
    #             )
    #             for i, v_ in enumerate(v)
    #             if (not value_exclude or not value_exclude.is_excluded(i))
    #             and (not value_include or value_include.is_included(i))
    #         )
    #
    #         return v.__class__(*seq_args) if is_namedtuple(v.__class__) else v.__class__(seq_args)
    #
    #     elif isinstance(v, Enum) and getattr(cls.Config, 'use_enum_values', False):
    #         return v.value
    #
    #     else:
    #         return v
    #
    # @staticmethod
    # def transform_dict(d):
    #     if isinstance(d, dict):
    #         if '_add_key' in d:
    #             # Prepare the string format by extracting '_add_key' and other content
    #             add_key_value = d.pop('_add_key')
    #             other_content = ", ".join(f"{key}={VizroBaseModel.transform_dict(value)}" for key, value in d.items())
    #             return f"{add_key_value}({other_content})"
    #         else:
    #             # Recurse through the dictionary
    #             return ", ".join(f"{key}={VizroBaseModel.transform_dict(value)}" for key, value in d.items())
    #     elif isinstance(d, list):
    #         # Recurse through the list, ensure it's formatted as a list but without quotes on strings
    #         return "[" + ", ".join(VizroBaseModel.transform_dict(item) for item in d) + "]"
    #     else:
    #         # Base case: if it's not a dictionary or list, return the item itself
    #         return repr(d)  # Use repr to ensure proper representation of strings and other data types

# Ideas
# - add through dict
# - similar to type, every new model has a field that we can insert through `include`
# - how about captured callable? include in self, then hide things in captured callable
# - unsure where the info lies: CapturedCallable (best case) or models with captured callable field


    # def dict_obj(self,**kwargs):
    #     d = self.dict(**kwargs)
    #     d["_add_key"] = self.__class__.__name__
    #     return VizroBaseModel.transform_dict(d)



    class Config:
        extra = "forbid"  # Good for spotting user typos and being strict.
        smart_union = True  # Makes unions work without unexpected coercion (will be the default in pydantic v2).
        validate_assignment = True  # Run validators when a field is assigned after model instantiation.
        copy_on_model_validation = "none"  # Don't copy sub-models. Essential for the model_manager to work correctly.


if __name__ == "__main__":
    class Country(VizroBaseModel):
        name: str
        phone_code: Optional[int] = 0


    class Address(VizroBaseModel):
        post_code: Optional[int]
        country: Country

    class Hobby(VizroBaseModel):
        name: str
        info: Optional[str] = "something cool!"

    class User(VizroBaseModel):
        first_name: str
        second_name: str
        address: Address
        hobbies: List[Hobby]


    foo = User(
        first_name='John',
        second_name='Doe',
        address=Address(
            post_code=123456,
            country=Country(
                name='USA',
                phone_code=1
            )
        ),
        hobbies=[
            Hobby(name='Programming'),
            Hobby(name='Gaming', info='Hell Yeah!!!'),
        ],
    )

    print(foo.dict_obj(exclude_unset = True))