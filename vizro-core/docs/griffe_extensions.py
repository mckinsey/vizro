"""Extensions we have written to help generate API reference docs."""

import griffe

logger = griffe.get_logger("griffe_dynamically_inspect")


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
