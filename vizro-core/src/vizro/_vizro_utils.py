"""Contains utilities for the implementation of vizro components."""

import sys
import typing
import warnings
from collections import defaultdict
from collections.abc import Mapping
from typing import Any


def _set_defaults_nested(supplied: Mapping[str, Any], defaults: Mapping[str, Any]) -> dict[str, Any]:
    supplied = defaultdict(dict, supplied)
    for default_key, default_value in defaults.items():
        if isinstance(default_value, Mapping):
            supplied[default_key] = _set_defaults_nested(supplied[default_key], default_value)
        else:
            supplied.setdefault(default_key, default_value)
    return dict(supplied)


_T = typing.TypeVar("_T")


# This is copied directly from typing_extensions.deprecated with the following changes:
#  - renamed deprecated to experimental
#  - default category is FutureWarning rather than DeprecationWarning
#  - updated docstring
class experimental:
    """Indicate that a class, function or overload is experimental.

    Usage:

        @experimental("Feature is experimental")
        class A:
            pass

        @overload
        @deprecated("int support is experimental")
        def g(x: int) -> int: ...
        @overload
        def g(x: str) -> int: ...

    The warning specified by *category* will be emitted at runtime
    on use of experimental objects. For functions, that happens on calls;
    for classes, on instantiation and on creation of subclasses.
    If the *category* is ``None``, no warning is emitted at runtime.
    The *stacklevel* determines where the
    warning is emitted. If it is ``1`` (the default), the warning
    is emitted at the direct caller of the deprecated object; if it
    is higher, it is emitted further up the stack.

    The experimental message passed to the decorator is saved in the
    ``__experimental__`` attribute on the decorated object.
    If applied to an overload, the decorator
    must be after the ``@overload`` decorator for the attribute to
    exist on the overload as returned by ``get_overloads()``.
    """

    def __init__(
        self,
        message: str,
        /,
        *,
        category: typing.Optional[typing.Type[Warning]] = FutureWarning,
        stacklevel: int = 1,
    ) -> None:
        if not isinstance(message, str):
            raise TypeError(f"Expected an object of type str for 'message', not {type(message).__name__!r}")
        self.message = message
        self.category = category
        self.stacklevel = stacklevel

    def __call__(self, arg: _T, /) -> _T:
        # Make sure the inner functions created below don't
        # retain a reference to self.
        msg = self.message
        category = self.category
        stacklevel = self.stacklevel
        if category is None:
            arg.__experimental__ = msg
            return arg
        elif isinstance(arg, type):
            import functools
            from types import MethodType

            original_new = arg.__new__

            @functools.wraps(original_new)
            def __new__(cls, /, *args, **kwargs):
                if cls is arg:
                    warnings.warn(msg, category=category, stacklevel=stacklevel + 1)
                if original_new is not object.__new__:
                    return original_new(cls, *args, **kwargs)
                # Mirrors a similar check in object.__new__.
                elif cls.__init__ is object.__init__ and (args or kwargs):
                    raise TypeError(f"{cls.__name__}() takes no arguments")
                else:
                    return original_new(cls)

            arg.__new__ = staticmethod(__new__)

            original_init_subclass = arg.__init_subclass__
            # We need slightly different behavior if __init_subclass__
            # is a bound method (likely if it was implemented in Python)
            if isinstance(original_init_subclass, MethodType):
                original_init_subclass = original_init_subclass.__func__

                @functools.wraps(original_init_subclass)
                def __init_subclass__(*args, **kwargs):
                    warnings.warn(msg, category=category, stacklevel=stacklevel + 1)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = classmethod(__init_subclass__)
            # Or otherwise, which likely means it's a builtin such as
            # object's implementation of __init_subclass__.
            else:

                @functools.wraps(original_init_subclass)
                def __init_subclass__(*args, **kwargs):
                    warnings.warn(msg, category=category, stacklevel=stacklevel + 1)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = __init_subclass__

            arg.__experimental__ = __new__.__experimental__ = msg
            __init_subclass__.__experimental__ = msg
            return arg
        elif callable(arg):
            import asyncio.coroutines
            import functools
            import inspect

            @functools.wraps(arg)
            def wrapper(*args, **kwargs):
                warnings.warn(msg, category=category, stacklevel=stacklevel + 1)
                return arg(*args, **kwargs)

            if asyncio.coroutines.iscoroutinefunction(arg):
                if sys.version_info >= (3, 12):
                    wrapper = inspect.markcoroutinefunction(wrapper)
                else:
                    wrapper._is_coroutine = asyncio.coroutines._is_coroutine

            arg.__experimental__ = wrapper.__experimental__ = msg
            return wrapper
        else:
            raise TypeError(
                f"@experimental decorator with non-None category must be applied to a class or callable, not {arg!r}"
            )
