import griffe

logger = griffe.get_logger("griffe_dynamically_inspect")


class DynamicallyInspect(griffe.Extension):
    """An extension to dynamically inspect just a few specific paths.
    This is needed so that documentation for vizro.figures.kpi_card and vizro.figures.kpi_card_reference can be
    generated correctly. Based on https://mkdocstrings.github.io/griffe/guide/users/how-to/selectively-inspect/.

    See https://github.com/mkdocstrings/griffe/issues/385 for additional context.
    """

    def __init__(self, paths: list[str]):
        self.paths = paths

    def on_instance(self, *, obj: griffe.Object, **kwargs):
        if obj.path not in self.paths:
            return

        logger.info("Dynamically inspecting '%s'", obj.path)
        inspected_module = griffe.inspect(obj.module.path, filepath=obj.filepath)
        obj.parent.set_member(obj.name, inspected_module[obj.name])
