"""Extensions we have written to help generate API reference docs."""

import griffe

logger = griffe.get_logger("griffe_dynamically_inspect")
filter_logger = griffe.get_logger("griffe_filter_private_attrs")


class DynamicallyInspect(griffe.Extension):
    """An extension to dynamically inspect just a few specific paths.

    This is needed so that documentation for vizro.figures.kpi_card and vizro.figures.kpi_card_reference can be
    generated correctly. Based on https://mkdocstrings.github.io/griffe/guide/users/how-to/selectively-inspect/.

    See https://github.com/mkdocstrings/griffe/issues/385 for additional context.
    """

    def __init__(self, paths: list[str]):
        """Specifies paths to dynamically inspect."""
        self.paths = paths

    def on_instance(self, *, obj: griffe.Object, **kwargs):  # noqa: D102
        if obj.path not in self.paths:
            return

        try:
            # Strangely we seem to need to do the dynamic import even though we don't use the result anywhere.
            # Otherwise the below griffe.inspect gives mkdocstrings: vizro.figures could not be found.
            griffe.dynamic_import(obj.path)
        except ImportError as error:
            logger.warning(f"Could not import {obj.path}: {error}")
            return

        logger.info("Dynamically inspecting '%s'", obj.path)
        inspected_module = griffe.inspect(obj.module.path, filepath=obj.filepath)
        obj.parent.set_member(obj.name, inspected_module[obj.name])


class FilterPrivateAttrs(griffe.Extension):
    """An extension to filter out private members from Pydantic model documentation.

    This filters out:
    - Attributes defined with PrivateAttr()
    - The 'type' discriminator field
    - Any methods/validators starting with underscore (e.g. _make_actions_chain)
    """

    def __init__(self, **kwargs):
        """Accept kwargs for griffe compatibility."""

    def _filter_private_attrs(self, cls: griffe.Class) -> None:
        """Filter out private members from a Pydantic model class."""
        try:
            from pydantic import BaseModel

            python_obj = griffe.dynamic_import(cls.path)
            if python_obj is None or not issubclass(python_obj, BaseModel):
                return

            private_attrs = getattr(python_obj, "__private_attributes__", {})
            for name in list(cls.members.keys()):
                if name in private_attrs:
                    cls.del_member(name)
                    filter_logger.info(f"Filtered out PrivateAttr '{name}' from {cls.path}")
                elif name == "type":
                    cls.del_member(name)
                    filter_logger.info(f"Filtered out 'type' field from {cls.path}")
                elif name.startswith("_") and not name.startswith("__"):
                    cls.del_member(name)
                    filter_logger.info(f"Filtered out private member '{name}' from {cls.path}")
        except (ImportError, AttributeError, TypeError):
            pass

    def on_class_members(self, *, cls: griffe.Class, **kwargs):
        """Filter out PrivateAttr members when class members are collected."""
        self._filter_private_attrs(cls)

    def on_instance(self, *, obj: griffe.Object, **kwargs):
        """Filter out PrivateAttr members after all processing is complete."""
        if isinstance(obj, griffe.Class):
            self._filter_private_attrs(obj)
