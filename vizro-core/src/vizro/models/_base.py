import inspect
import logging
import textwrap
from typing import Annotated, Any, Optional, Union, cast, get_args, get_origin

import autoflake
import black
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    model_serializer,
)
from pydantic.fields import FieldInfo

from vizro.managers import model_manager
from vizro.models._models_utils import REPLACEMENT_STRINGS, _log_call
from vizro.models.types import ModelID

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
    import vizro.actions as va
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
            # Always use built-in actions from the vizro.actions (va) namespace, not vizro.models (vm).
            # Enforces explicit namespacing to avoid ambiguity between built-in actions.
            namespace = "va" if __vizro_model__ in dir(va) else "vm"
            return f"{namespace}.{__vizro_model__}({fields})"

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
                for new in REPLACEMENT_STRINGS.values()
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


def _add_type_to_union(union: type[Any], new_type: type[Any]):  # TODO[mypy]: not sure how to type the return type
    args = get_args(union)
    all_types = args + (new_type,)  # noqa: RUF005 #as long as we support Python 3.9, we can't use the new syntax
    # The below removes duplicates by type, which would trigger a pydantic error (TypeError: Value 'xxx'
    # for discriminator 'type' mapped to multiple choices) otherwise.
    # We get the type value by accessing the type objects model_fields attribute, which is a dict of the fields
    # of the model. Since in Vizro we always define the type with a default value (and don't change it), the default
    # value of the type field is the only possible `type`.
    # Last added type will be the one that is kept - this is replicating V1 behavior that would other raise an error
    # in V2, and thus we are defining NEW behavior here. This works by using .values(), which extract values by
    # insertion order (since Python 3.7), thus the last added type will be the one that is kept.
    unique_types = tuple({t.model_fields["type"].default: t for t in all_types}.values())
    return Union[unique_types]


def _add_type_to_annotated_union(union, new_type: type[Any]):  # TODO[mypy]: not sure how to type the return type
    args = get_args(union)
    return Annotated[_add_type_to_union(args[0], new_type), args[1]]


def _is_discriminated_union_via_field_info(field: FieldInfo) -> bool:
    if hasattr(field, "annotation") and field.annotation is None:
        raise ValueError("Field annotation is None")
    return hasattr(field, "discriminator") and field.discriminator is not None


def _is_discriminated_union_via_annotation(annotation) -> bool:
    if get_origin(annotation) is not Annotated:
        return False
    metadata = get_args(annotation)[1:]
    return hasattr(metadata[0], "discriminator")


def _is_not_annotated(field: type[Any]) -> bool:
    return get_origin(field) is not None and get_origin(field) is not Annotated


def _add_type_to_annotated_union_if_found(
    type_annotation: type[Any], additional_type: type[Any], field_name: str
) -> type[Any]:
    def _split_types(type_annotation: type[Any]) -> type[Any]:
        outer_type = get_origin(type_annotation)
        inner_types = get_args(type_annotation)  # TODO[MS]:  what if multiple, or what if not first?
        if outer_type is None or len(inner_types) < 1:
            raise ValueError("Unsupported annotation type")
        if len(inner_types) > 1:
            return outer_type[
                _add_type_to_annotated_union_if_found(inner_types[0], additional_type, field_name),
                inner_types[1],
            ]
        return outer_type[_add_type_to_annotated_union_if_found(inner_types[0], additional_type, field_name)]

    if _is_not_annotated(type_annotation):
        return _split_types(type_annotation)
    elif _is_discriminated_union_via_annotation(type_annotation):
        return _add_type_to_annotated_union(type_annotation, additional_type)
    else:
        raise ValueError(
            f"Field '{field_name}' must be a discriminated union or list of discriminated union type. "
            "You probably do not need to call add_type to use your new type."
        )


def set_id(id: ModelID) -> ModelID:
    return id or model_manager._generate_id()


class VizroBaseModel(BaseModel):
    """All models that are registered to the model manager should inherit from this class.

    Args:
        id (ModelID): ID to identify model. Must be unique throughout the whole dashboard. Defaults to `""`.
            When no ID is chosen, ID will be automatically generated.

    """

    id: Annotated[
        ModelID,
        AfterValidator(set_id),
        Field(
            default="",
            description="ID to identify model. Must be unique throughout the whole dashboard."
            "When no ID is chosen, ID will be automatically generated.",
            validate_default=True,
        ),
    ]

    @_log_call
    def model_post_init(self, context: Any) -> None:
        model_manager[self.id] = self

    # Previously in V1, we used to have an overwritten `.dict` method, that would add __vizro_model__ to the dictionary
    # if called in the correct context.
    # In addition, it was possible to exclude fields specified in __vizro_exclude_fields__.
    # This was like pydantic's own __exclude_fields__ but this is not possible in V2 due to the non-recursive nature of
    # the model_dump method. Now this serializer allows to add the model name to the dictionary when serializing the
    # model if called with context {"add_name": True}.
    # Excluding specific fields is now done via overwriting this serializer (see e.g. Page model).
    # Useful threads that were started:
    # https://stackoverflow.com/questions/79272335/remove-field-from-all-nested-pydantic-models
    # https://github.com/pydantic/pydantic/issues/11099
    @model_serializer(mode="wrap")
    def serialize(
        self,
        handler: SerializerFunctionWrapHandler,
        info: SerializationInfo,
    ) -> dict[str, Any]:
        result = handler(self)
        if info.context is not None and info.context.get("add_name", False):
            result["__vizro_model__"] = self.__class__.__name__
        return result

    @classmethod
    def add_type(cls, field_name: str, new_type: type[Any]):
        """Adds a new type to an existing field based on a discriminated union.

        Args:
            field_name: Field that new type will be added to
            new_type: New type to add to discriminated union

        """
        field = cls.model_fields[field_name]
        old_type = cast(type[Any], field.annotation)
        new_annotation = (
            _add_type_to_union(old_type, new_type)
            if _is_discriminated_union_via_field_info(field)
            else _add_type_to_annotated_union_if_found(old_type, new_type, field_name)
        )
        cls.model_fields[field_name] = FieldInfo.merge_field_infos(field, annotation=new_annotation)

        # We need to resolve all ForwardRefs again e.g. in the case of Page, which requires update_forward_refs in
        # vizro.models. The vm.__dict__.copy() is inspired by pydantic's own implementation of update_forward_refs and
        # effectively replaces all ForwardRefs defined in vizro.models.
        import vizro.models as vm

        cls.model_rebuild(force=True, _types_namespace=vm.__dict__.copy())
        new_type.model_rebuild(force=True, _types_namespace=vm.__dict__.copy())

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
        model_dict = self.model_dump(context={"add_name": True}, exclude_unset=True)

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

    model_config = ConfigDict(
        extra="forbid",  # Good for spotting user typos and being strict.
        validate_assignment=True,  # Run validators when a field is assigned after model instantiation.
    )
