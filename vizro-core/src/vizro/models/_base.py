from collections.abc import Mapping
from contextlib import contextmanager
from typing import Annotated, Any, Optional, Union

try:
    from pydantic.v1 import BaseModel, Field, validator
    from pydantic.v1.fields import SHAPE_LIST, ModelField
    from pydantic.v1.typing import get_args
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, validator
    from pydantic.fields import SHAPE_LIST, ModelField
    from pydantic.typing import get_args


import inspect
import logging
import textwrap

import autoflake
import black

from vizro.managers import model_manager
from vizro.models._models_utils import REPLACEMENT_STRINGS, _log_call

ACTIONS_CHAIN = "ActionsChain"
ACTION = "actions"

TO_PYTHON_TEMPLATE = """
############ Imports ##############
import vizro.plotly.express as px
import vizro.tables as vt
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro
from vizro.models.types import capture
from vizro.managers import data_manager
{extra_imports}

{callable_defs_template}
{data_settings_template}

########### Model code ############
{code}
"""

CALLABLE_TEMPLATE = """
####### Function definitions ######
{callable_defs}
"""

DATA_TEMPLATE = """
####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
{data_setting}
"""

# Global variable to dictate whether VizroBaseModel.dict should be patched to work for _to_python.
# This is always False outside the _patch_vizro_base_model_dict context manager to ensure that, unless explicitly
# called for, dict behavior is unmodified from pydantic's default.
_PATCH_VIZRO_BASE_MODEL_DICT = False


@contextmanager
def _patch_vizro_base_model_dict():
    global _PATCH_VIZRO_BASE_MODEL_DICT  # noqa
    _PATCH_VIZRO_BASE_MODEL_DICT = True
    try:
        yield
    finally:
        _PATCH_VIZRO_BASE_MODEL_DICT = False


def _format_and_lint(code_string: str) -> str:
    # Tracking https://github.com/astral-sh/ruff/issues/659 for proper Python API
    # Good example: https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
    # While we wait for the API, we can use autoflake and black to process code strings

    removed_imports = autoflake.fix_code(code_string, remove_all_unused_imports=True)
    # Black doesn't yet have a Python API, so format_str might not work at some point in the future.
    # https://black.readthedocs.io/en/stable/faq.html#does-black-have-an-api
    formatted = black.format_str(removed_imports, mode=black.Mode())
    return formatted


def _dict_to_python(object: Any) -> str:
    from vizro.models.types import CapturedCallable

    if isinstance(object, dict) and "__vizro_model__" in object:
        __vizro_model__ = object.pop("__vizro_model__")

        # This is required to back-engineer the actions chains. It is easier to handle in the string conversion here
        # than in the dict creation, because we end up with nested lists when being forced to return a list of actions.
        # If we handle it in dict of vm.BaseModel, then we created an unexpected dict return.
        if __vizro_model__ == ACTIONS_CHAIN:
            action_data = object[ACTION]
            return ", ".join(_dict_to_python(item) for item in action_data)
        else:
            # This is very similar to doing repr but includes the vm. prefix and calls _object_to_python_code
            # rather than repr recursively.
            fields = ", ".join(f"{field_name}={_dict_to_python(value)}" for field_name, value in object.items())
            return f"vm.{__vizro_model__}({fields})"
    elif isinstance(object, dict):
        fields = ", ".join(f"'{field_name}': {_dict_to_python(value)}" for field_name, value in object.items())
        return "{" + fields + "}"
    elif isinstance(object, list):
        # Need to do this manually to avoid extra quotation marks that arise when doing repr(list).
        code_string = ", ".join(_dict_to_python(item) for item in object)
        return f"[{code_string}]"
    elif isinstance(object, CapturedCallable):
        return object.__repr_clean__()
    else:
        return repr(object)


# The two extract helper functions may not work when we refactor the model_manager to work differently when models
# are created. An alternative approach to iterating through the model_manager is to recurse through the object as
# is done in the _dict_to_python function.
# Note also that these functions find also unintended model_manager additions, a known but accepted limitation.
def _extract_captured_callable_source() -> set[str]:
    from vizro.models.types import CapturedCallable

    captured_callable_sources = set()
    for model_id in model_manager:
        for _, value in model_manager[model_id]:
            if isinstance(value, CapturedCallable) and not any(
                # Check to see if the captured callable does use a cleaned module string, if yes then
                # we can assume that the source code can be imported via Vizro, and thus does not need to be defined
                value.__repr_clean__().startswith(new)
                for _, new in REPLACEMENT_STRINGS.items()
            ):
                try:
                    source = textwrap.dedent(inspect.getsource(value._function))
                    captured_callable_sources.add(source)
                except OSError:
                    # OSError is raised when the source code is not available. This is expected
                    # for built-in functions or dynamically defined functions (via exec or eval).
                    logging.warning(f"Could not extract source for {value._function}. Definition will not be included.")
                    pass
    return captured_callable_sources


def _extract_captured_callable_data_info() -> set[str]:
    from vizro.models.types import CapturedCallable

    return {
        f'# data_manager["{value["data_frame"]}"] = ===> Fill in here <==='
        for model_id in model_manager
        for _, value in model_manager[model_id]
        if isinstance(value, CapturedCallable)
        if "data_frame" in value._arguments
    }


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
    def add_type(cls, field_name: str, new_type: type[Any]):
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
            # Field is a list of discriminated union e.g. components: list[ComponentType].
            new_annotation = list[_add_to_discriminated_union(sub_field.outer_type_)]  # type: ignore[misc]
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
        global _PATCH_VIZRO_BASE_MODEL_DICT  # noqa
        if not _PATCH_VIZRO_BASE_MODEL_DICT:
            # Whenever dict is called outside _patch_vizro_base_model_dict, we don't modify the behavior of the dict.
            return super().dict(**kwargs)

        # When used in _to_python, we overwrite pydantic's own `dict` method to add __vizro_model__ to the dictionary
        # and to exclude fields specified dynamically in __vizro_exclude_fields__.
        # To get exclude as an argument is a bit fiddly because this function is called recursively inside pydantic,
        # which sets exclude=None by default.
        if kwargs.get("exclude") is None:
            kwargs["exclude"] = self.__vizro_exclude_fields__()
        _dict = super().dict(**kwargs)
        _dict["__vizro_model__"] = self.__class__.__name__
        return _dict

    # This is like pydantic's own __exclude_fields__ but safer to use (it looks like __exclude_fields__ no longer
    # exists in pydantic v2).
    # Root validators with pre=True are always included, even when exclude_default=True, and so this is needed
    # to potentially exclude fields set this way, like Page.id.
    def __vizro_exclude_fields__(self) -> Optional[Union[set[str], Mapping[str, Any]]]:
        return None

    def _to_python(
        self, extra_imports: Optional[set[str]] = None, extra_callable_defs: Optional[set[str]] = None
    ) -> str:
        """Converts a Vizro model to the Python code that would create it.

        Args:
            extra_imports: Extra imports to add to the Python code. Provide as a set of complete import strings.
            extra_callable_defs: Extra callable definitions to add to the Python code. Provide as a set of complete
                function definitions.

        Returns:
            str: Python code to create the Vizro model.

        Examples:
            Simple usage example with card model.

            >>> import vizro.models as vm
            >>> card = vm.Card(text="Hello, world!")
            >>> print(card._to_python())

            Further options include adding extra imports and callable definitions. These will be included in the
            returned Python string.

            >>> print(
            ...     card._to_python(
            ...         extra_imports={"from typing import Optional"},
            ...         extra_callable_defs={"def test(foo: Optional[str]): return foo"},
            ...     )
            ... )

        """
        # Imports
        extra_imports_concat = "\n".join(extra_imports) if extra_imports else None

        # CapturedCallable definitions - NOTE that order is not guaranteed
        callable_defs_set = _extract_captured_callable_source() | (extra_callable_defs or set())
        callable_defs_concat = "\n".join(callable_defs_set) if callable_defs_set else None

        # Data Manager
        data_defs_set = _extract_captured_callable_data_info()
        data_defs_concat = "\n".join(data_defs_set) if data_defs_set else None

        # Model code
        with _patch_vizro_base_model_dict():
            model_dict = self.dict(exclude_unset=True)

        model_code = "model = " + _dict_to_python(model_dict)

        # Concatenate and lint code
        callable_defs_template = (
            CALLABLE_TEMPLATE.format(callable_defs=callable_defs_concat) if callable_defs_concat else ""
        )
        data_settings_template = DATA_TEMPLATE.format(data_setting=data_defs_concat) if data_defs_concat else ""
        unformatted_code = TO_PYTHON_TEMPLATE.format(
            code=model_code,
            extra_imports=extra_imports_concat or "",
            callable_defs_template=callable_defs_template,
            data_settings_template=data_settings_template,
        )
        try:
            return _format_and_lint(unformatted_code)
        except Exception:
            logging.exception("Code formatting failed; returning unformatted code")
            return unformatted_code

    class Config:
        extra = "forbid"  # Good for spotting user typos and being strict.
        smart_union = True  # Makes unions work without unexpected coercion (will be the default in pydantic v2).
        validate_assignment = True  # Run validators when a field is assigned after model instantiation.
        copy_on_model_validation = "none"  # Don't copy sub-models. Essential for the model_manager to work correctly.
