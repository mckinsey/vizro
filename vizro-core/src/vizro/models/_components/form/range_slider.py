from typing import Annotated, Literal

from pydantic import AfterValidator, Field, conlist
from typing_extensions import deprecated

from vizro.models._components.form._form_utils import validate_range_value
from vizro.models._components.form.slider import Slider


@deprecated(
    "`RangeSlider` is deprecated and will not exist in Vizro 1.0.0 "
    "(https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/#rangeslider-model). "
    "Use `Slider` with `range=True` instead.",
    category=FutureWarning,
)
class RangeSlider(Slider):
    """Deprecated numeric range selector. Use [`Slider`][vizro.models.Slider] with `range=True` instead.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [How to use numerical selectors](../user-guides/selectors.md#numerical-selectors)

    """

    type: Literal["range_slider"] = "range_slider"  # type: ignore[assignment]
    # Lock to range mode: RangeSlider is exactly Slider(range=True), so `range=False` must be rejected rather than
    # silently building a single-handle slider still typed `range_slider`.
    range: Literal[True] = Field(default=True, description="Boolean flag for displaying range slider.")
    # Narrow the inherited `value` to the two-handle `[start, end]` form only. RangeSlider fixes range=True, so a scalar
    # value is rejected at runtime by Slider._validate_range_value_shape; dropping it here keeps the JSON schema honest.
    value: Annotated[  # type: ignore[valid-type]
        conlist(float, min_length=2, max_length=2) | None,
        AfterValidator(validate_range_value),
        Field(default=None, description="Default value: a `[start, end]` pair."),
    ]
