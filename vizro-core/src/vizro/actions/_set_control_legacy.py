"""Deprecated `set_control` action alias. Use [`set_controls`][vizro.actions.set_controls] instead.

This alias is isolated in its own module (like `ag_grid.py` and `range_slider.py` for the deprecated models) so that
removing it in Vizro 1.0.0 is deleting a file rather than editing shared code.
"""

# TODO[1.0.0]: delete this entire file (the deprecated `set_control` alias). Also drop its import + `__all__` entry in
#  `actions/__init__.py`, its re-export in `models/__init__.py`, and the `set_control` Tag in the `ActionType` union in
#  `types.py`. Users migrate to `set_controls(controls=[...])`.

from typing import Literal

from pydantic import Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from typing_extensions import deprecated

from vizro.actions._set_control import set_controls
from vizro.models.types import ModelID


@deprecated(
    "`set_control` is deprecated and will not exist in Vizro 1.0.0 "
    "(https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/#set_control-action). "
    "Use `set_controls` with `controls` as a list of ids instead.",
    category=FutureWarning,
)
class set_control(set_controls):
    """Deprecated. Use [`set_controls`][vizro.actions.set_controls] with `controls` as a list of ids instead."""

    type: Literal["set_control"] = "set_control"  # type: ignore[assignment]
    control: ModelID | list[ModelID] = Field(
        description="Filter or Parameter component id(s) to be affected by the trigger. Provide a single id or a list "
        "of ids. Deprecated: use `set_controls` with `controls` instead."
    )
    # `controls` is required on `set_controls`, but this deprecated alias derives it from `control` (see below), so keep
    # it optional here and hide it from this alias's schema: users configure `control`, not `controls`.
    controls: SkipJsonSchema[ModelID | list[ModelID]] = Field(
        default=[], description="Populated from the deprecated `control` argument."
    )

    @model_validator(mode="before")
    @classmethod
    def _map_control_to_controls(cls, data):
        # Map the legacy `control` (single id or list) onto the canonical `controls` field before validation, so
        # `set_control(control=...)` satisfies the now-required `controls` without `set_controls` itself exposing an
        # optional `controls` default (which would let `set_controls()` validate only to fail later in pre_build).
        if isinstance(data, dict) and "control" in data:
            data = {**data, "controls": data["control"]}
        return data
