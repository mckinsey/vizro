"""Griffe extension for `@experimental`. Based on griffe-warning-deprecated."""

from __future__ import annotations

import ast
from typing import Any

from griffe import Class, Docstring, DocstringSectionAdmonition, ExprCall, Extension, Function, get_logger

logger = get_logger(__name__)
self_namespace = "griffe_experimental_decorator"
mkdocstrings_namespace = "mkdocstrings"

_decorators = {"vizro._vizro_utils.experimental"}


def _experimental(obj: Class | Function) -> str | None:
    for decorator in obj.decorators:
        if decorator.callable_path in _decorators and isinstance(decorator.value, ExprCall):
            first_arg = decorator.value.arguments[0]
            try:
                return ast.literal_eval(first_arg)  # type: ignore[arg-type]
            except ValueError:
                logger.debug("%s is not a static string", str(first_arg))
                return None
    return None


class ExperimentalDecoratorExtension(Extension):
    """Griffe extension for `@experimental`. Based on griffe-warning-deprecated."""

    def __init__(
        self,
        kind: str = "tip",
        title: str | None = "Experimental",
        label: str | None = "experimental",
    ) -> None:
        """Initialize the extension.

        Parameters:
            kind: Admonitions kind.
            title: Admonitions title.
            label: Label added to experimental objects.
        """
        super().__init__()
        self.kind = kind
        self.title = title or ""
        self.label = label

    def _insert_message(self, obj: Function | Class, message: str) -> None:
        title = self.title
        if not self.title:
            title, message = message, title
        if not obj.docstring:
            obj.docstring = Docstring("", parent=obj)
        sections = obj.docstring.parsed
        sections.insert(0, DocstringSectionAdmonition(kind=self.kind, text=message, title=title))

    def on_class_instance(self, *, cls: Class, **kwargs: Any) -> None:  # noqa: ARG002
        """Add section to docstrings of experimental classes."""
        if message := _experimental(cls):
            cls.experimental = message
            self._insert_message(cls, message)
            if self.label:
                cls.labels.add(self.label)

    def on_function_instance(self, *, func: Function, **kwargs: Any) -> None:  # noqa: ARG002
        """Add section to docstrings of experimental functions."""
        if message := _experimental(func):
            func.experimental = message
            self._insert_message(func, message)
            if self.label:
                func.labels.add(self.label)
