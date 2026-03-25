# AUTO GENERATED FILE - DO NOT EDIT

import typing
from typing import Literal  # noqa: F401

from dash.development.base_component import Component, _explicitize_args

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]

NumberType = typing.Union[typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex]


class Cascade(Component):
    """A Cascade component.

    Keyword Arguments:
    - id (boolean | number | string | dict | list; optional)

    - className (boolean | number | string | dict | list; optional)

    - clearable (boolean | number | string | dict | list; optional)

    - disabled (boolean | number | string | dict | list; optional)

    - maxHeight (boolean | number | string | dict | list; optional)

    - multi (boolean | number | string | dict | list; optional)

    - options (boolean | number | string | dict | list; required)

    - persisted_props (boolean | number | string | dict | list; optional)

    - persistence (boolean | number | string | dict | list; optional)

    - persistence_type (boolean | number | string | dict | list; optional)

    - placeholder (boolean | number | string | dict | list; optional)

    - searchable (boolean | number | string | dict | list; optional)

    - setProps (boolean | number | string | dict | list; optional)

    - value (boolean | number | string | dict | list; optional)
    """

    _children_props: list[str] = []
    _base_nodes = ["children"]
    _namespace = "vizro_dash_components"
    _type = "Cascade"

    def __init__(
        self,
        id: str | dict | None = None,
        options: typing.Any | None = None,
        value: typing.Any | None = None,
        multi: typing.Any | None = None,
        searchable: typing.Any | None = None,
        clearable: typing.Any | None = None,
        placeholder: typing.Any | None = None,
        disabled: typing.Any | None = None,
        maxHeight: typing.Any | None = None,
        className: typing.Any | None = None,
        style: typing.Any | None = None,
        persistence: typing.Any | None = None,
        persisted_props: typing.Any | None = None,
        persistence_type: typing.Any | None = None,
        **kwargs,
    ):
        self._prop_names = [
            "id",
            "className",
            "clearable",
            "disabled",
            "maxHeight",
            "multi",
            "options",
            "persisted_props",
            "persistence",
            "persistence_type",
            "placeholder",
            "searchable",
            "setProps",
            "style",
            "value",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "className",
            "clearable",
            "disabled",
            "maxHeight",
            "multi",
            "options",
            "persisted_props",
            "persistence",
            "persistence_type",
            "placeholder",
            "searchable",
            "setProps",
            "style",
            "value",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ["options"]:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")

        super().__init__(**args)


setattr(Cascade, "__init__", _explicitize_args(Cascade.__init__))
