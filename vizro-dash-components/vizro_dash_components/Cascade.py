# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class Cascade(Component):
    """A Cascade component.


Keyword arguments:

- id (boolean | number | string | dict | list; optional)

- className (boolean | number | string | dict | list; optional)

- clearable (boolean | number | string | dict | list; optional)

- disabled (boolean | number | string | dict | list; optional)

- maxHeight (boolean | number | string | dict | list; optional)

- multi (boolean | number | string | dict | list; optional)

- options (boolean | number | string | dict | list; required)

- placeholder (boolean | number | string | dict | list; optional)

- searchable (boolean | number | string | dict | list; optional)

- setProps (boolean | number | string | dict | list; required)

- value (boolean | number | string | dict | list; optional)"""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'vizro_dash_components'
    _type = 'Cascade'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        options: typing.Optional[typing.Any] = None,
        value: typing.Optional[typing.Any] = None,
        multi: typing.Optional[typing.Any] = None,
        searchable: typing.Optional[typing.Any] = None,
        clearable: typing.Optional[typing.Any] = None,
        placeholder: typing.Optional[typing.Any] = None,
        disabled: typing.Optional[typing.Any] = None,
        maxHeight: typing.Optional[typing.Any] = None,
        className: typing.Optional[typing.Any] = None,
        style: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'className', 'clearable', 'disabled', 'maxHeight', 'multi', 'options', 'placeholder', 'searchable', 'setProps', 'style', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'clearable', 'disabled', 'maxHeight', 'multi', 'options', 'placeholder', 'searchable', 'setProps', 'style', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['options', 'setProps']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Cascade, self).__init__(**args)

setattr(Cascade, "__init__", _explicitize_args(Cascade.__init__))
