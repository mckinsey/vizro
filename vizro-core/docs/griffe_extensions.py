"""Extensions we have written to help generate API reference docs."""

import griffe
from pydantic import BaseModel
from pydantic.fields import FieldInfo, PydanticUndefined

logger = griffe.get_logger("griffe_dynamically_inspect")
pydantic_logger = griffe.get_logger("griffe_pydantic_docs")


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


class PydanticDocsCleaner(griffe.Extension):
    """Clean up Pydantic model documentation.

    This extension:
    1. Filters out private members (PrivateAttr, 'type' field, underscore-prefixed methods)
    2. Excludes pydantic fields from TOC while keeping them renderable in tables
    """

    def __init__(self, **kwargs):
        """Accept kwargs for griffe compatibility."""

    def _filter_private_attrs(self, cls: griffe.Class) -> None:
        """Filter out private members from a Pydantic model class."""

        python_obj = griffe.dynamic_import(cls.path)
        if python_obj is None or not issubclass(python_obj, BaseModel):
            return

        private_attrs = getattr(python_obj, "__private_attributes__", {})
        for name in list(cls.members.keys()):
            if name in private_attrs:
                cls.del_member(name)
                pydantic_logger.info(f"Filtered out PrivateAttr '{name}' from {cls.path}")
            elif name == "type":
                cls.del_member(name)
                pydantic_logger.info(f"Filtered out 'type' field from {cls.path}")
            elif name.startswith("_") and not name.startswith("__"):
                cls.del_member(name)
                pydantic_logger.info(f"Filtered out private member '{name}' from {cls.path}")

    def on_class_members(self, *, cls: griffe.Class, **kwargs):
        """Filter out PrivateAttr members when class members are collected."""
        self._filter_private_attrs(cls)

    def on_instance(self, *, obj: griffe.Object, **kwargs):
        """Filter out PrivateAttr members after all processing is complete."""
        if isinstance(obj, griffe.Class):
            self._filter_private_attrs(obj)

    def _enrich_field_metadata(self, cls: griffe.Class) -> None:
        """Enrich field metadata for defaults/required from model_fields.

        griffe-pydantic's static analysis doesn't handle SkipJsonSchema patterns reliably,
        so we dynamically import the model and extract defaults from model_fields.
        We also record explicit `required` to distinguish from default=None.
        """

        python_obj = griffe.dynamic_import(cls.path)

        if python_obj is None or not issubclass(python_obj, BaseModel):
            return

        model_fields = getattr(python_obj, "model_fields", {})
        for name, member in cls.members.items():
            if not hasattr(member, "labels") or "pydantic-field" not in member.labels:
                continue
            field_info = model_fields.get(name)
            if field_info is None or not isinstance(field_info, FieldInfo):
                continue

            required = field_info.is_required()
            default_display = None
            if not required:
                if field_info.default is not PydanticUndefined:
                    default_display = repr(field_info.default)
                elif field_info.default_factory is not None:
                    factory = field_info.default_factory
                    factory_name = getattr(factory, "__name__", None)
                    if factory_name:
                        default_display = f"default_factory={factory_name}"
                    else:
                        default_display = f"default_factory={factory!r}"

            member.extra.setdefault("vizro_pydantic", {})
            member.extra["vizro_pydantic"]["required"] = required
            member.extra["vizro_pydantic"]["default_display"] = default_display

    def _exclude_fields_from_toc(self, cls: griffe.Class) -> None:
        """Store fields and remove from members to exclude from TOC."""
        if "pydantic-model" not in cls.labels:
            return

        # Enrich defaults/required before storing fields
        self._enrich_field_metadata(cls)

        # Collect pydantic fields
        stored_fields = {}
        fields_to_remove = []
        for name, member in list(cls.members.items()):
            if hasattr(member, "labels") and "pydantic-field" in member.labels:
                stored_fields[name] = member
                fields_to_remove.append(name)

        if stored_fields:
            # Store fields for template access
            cls.extra.setdefault("griffe_pydantic", {})["_stored_fields"] = stored_fields

            # Remove from members (prevents TOC listing)
            for name in fields_to_remove:
                cls.del_member(name)
                pydantic_logger.info(f"Excluded field '{name}' from TOC for {cls.path}")

    def on_package(self, *, pkg: griffe.Module, **kwargs):
        """Process all classes after package is fully loaded (after griffe_pydantic runs)."""
        self._process_module_recursive(pkg)

    def _process_module_recursive(self, module: griffe.Module) -> None:
        """Recursively process all modules and classes."""
        for member in list(module.members.values()):
            if isinstance(member, griffe.Alias):
                continue  # Skip aliases to avoid resolution errors
            if isinstance(member, griffe.Class):
                self._exclude_fields_from_toc(member)
            elif isinstance(member, griffe.Module):
                self._process_module_recursive(member)
