"""Code powering the plot command.

Vizro-AI turns a natural-language request into a declarative chart *specification*
(`BaseChartPlan`), then renders it with trusted `plotly.express` code. The model fills the
spec's fields — chart type, column encodings, styling — it never writes or returns Python. So
there is no `exec()` of model output and nothing to safeguard: a chart is produced by our own
reviewed `build_figure`, and the figure can be serialized to JSON for a frontend to render.

Vizro-AI does not manipulate data. The dataframe you pass in must already be in the shape you
want to plot (aggregation, filtering, sorting done upstream, e.g. in SQL); Vizro-AI maps its
columns to a chart. The chart grammar (which chart types exist and which arguments each accepts)
is derived by introspecting `plotly.express`, so new plotly releases expose new charts with no
change here.
"""

import inspect
import math
from collections.abc import Callable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.express._core import all_attrables
from pydantic import BaseModel, ConfigDict, Field, JsonValue, create_model, field_validator, model_validator

CUSTOM_CHART_NAME = "custom_chart"


# --------------------------------------------------------------------------------------
# Chart grammar, derived from plotly express by introspection.
# --------------------------------------------------------------------------------------
# Which plotly-express arguments map to dataframe columns — read from plotly's own classification
# (`plotly.express._core.all_attrables`) so the grammar stays correct across plotly versions.
# `_core` is a private plotly module: if a future plotly release moves it, the import above fails
# loudly instead of silently using a stale list. Everything else a chart accepts is styling.
COLUMN_ENCODINGS = frozenset(all_attrables)
# Map/geo charts need coordinates or provider tokens, so they can't be driven from an arbitrary
# dataframe and are excluded from the discovered grammar.
_MAP_LIKE = ("mapbox", "geo", "choropleth")


def _is_dataframe_chart(obj: object) -> bool:
    """A plotly-express chart builder takes `data_frame` as its first argument."""
    try:
        params = list(inspect.signature(obj).parameters)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    return bool(params) and params[0] == "data_frame"


def _discover_chart_builders() -> dict[str, object]:
    return {
        name: getattr(px, name)
        for name in dir(px)
        if not (name.startswith("_") or name.endswith("_map") or any(tok in name for tok in _MAP_LIKE))
        and _is_dataframe_chart(getattr(px, name))
    }


CHART_BUILDERS = _discover_chart_builders()
CHART_TYPES = sorted(CHART_BUILDERS)


def _check_chart_type(chart_type: str) -> None:
    if chart_type not in CHART_BUILDERS:
        raise ValueError(f"Unknown chart_type {chart_type!r}. Choose one of: {CHART_TYPES}.")


def _signature_params(chart_type: str) -> set[str]:
    return set(inspect.signature(CHART_BUILDERS[chart_type]).parameters)  # type: ignore[arg-type]


def allowed_encodings(chart_type: str) -> set[str]:
    """Column-mapping arguments valid for a chart type — derived from its plotly signature."""
    return COLUMN_ENCODINGS & _signature_params(chart_type)


def styling_options(chart_type: str) -> set[str]:
    """Non-column styling arguments valid for a chart type — derived from its plotly signature.

    `labels` and `title` are excluded because they have dedicated fields on the plan; every
    setting has exactly one home, so a plan can never say the same thing twice.
    """
    return _signature_params(chart_type) - COLUMN_ENCODINGS - {"data_frame", "labels", "title"}


def _contains_non_finite(value: object) -> bool:
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, (list, tuple)):
        return any(_contains_non_finite(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_non_finite(item) for item in value.values())
    return False


# --------------------------------------------------------------------------------------
# Trusted rendering — plotly express only. The only place a figure is built; no data reshaping.
# --------------------------------------------------------------------------------------
def _plan_problems(plan: "BaseChartPlan") -> list[str]:
    """Key-validity problems of a plan, knowable without data."""
    valid_encodings = allowed_encodings(plan.chart_type)
    valid_options = styling_options(plan.chart_type)
    errors = [
        f"'{key}' is not a valid encoding for '{plan.chart_type}'. Valid: {sorted(valid_encodings)}."
        for key in plan.encodings
        if key not in valid_encodings
    ]
    errors += [
        f"'{key}' is not a valid option for '{plan.chart_type}'. Valid: {sorted(valid_options)}."
        for key in plan.options
        if key not in valid_options
    ]
    return errors


def _plan_kwargs(plan: "BaseChartPlan") -> dict:
    """The plotly-express keyword arguments a plan describes.

    The single source used by both `build_figure` and `render_px_code`, so the rendered figure
    and the templated code cannot diverge. Invalid keys raise instead of being dropped, so a
    wrong plan fails loudly (a retryable error) rather than rendering a silently wrong chart.
    """
    _check_chart_type(plan.chart_type)
    problems = _plan_problems(plan)
    if problems:
        raise ValueError(" ".join(problems))
    # Encodings, options, labels and title are disjoint by construction: encodings keys must be
    # column-mapping arguments, options keys must be styling arguments minus labels/title.
    kwargs: dict = dict(plan.encodings)
    kwargs.update(plan.options)
    if plan.labels:
        kwargs["labels"] = plan.labels
    if plan.title:
        kwargs["title"] = plan.title
    return kwargs


def build_figure(plan: "BaseChartPlan", data_frame: pd.DataFrame, **overrides) -> go.Figure:
    """Turn a chart plan into a Plotly figure. This is the whole 'execution' — no `exec()`.

    `data_frame` must already be in the shape to plot; Vizro-AI does not transform data.
    `overrides` are plotly-express keyword arguments applied on top of the plan (they win), so
    reusable chart functions can honor per-call customizations such as ``title=``.
    """
    kwargs = _plan_kwargs(plan)
    kwargs.update(overrides)
    return CHART_BUILDERS[plan.chart_type](data_frame, **kwargs)  # type: ignore[operator]


def validate_against_data(plan: "BaseChartPlan", data_frame: pd.DataFrame) -> list[str]:
    """Return human-readable problems with a plan against the data, or [] if it is valid."""
    try:
        _check_chart_type(plan.chart_type)
    except ValueError as e:
        return [str(e)]
    columns = set(data_frame.columns)
    errors = _plan_problems(plan)
    errors += [f"Column '{col}' is not in the data." for col in plan.referenced_columns() if col not in columns]
    # plotly silently ignores label keys that match nothing, so a typo'd relabel would otherwise
    # vanish. 'value'/'variable'/'count' are legitimate synthetic wide-form/histogram keys.
    errors += [
        f"Label key '{key}' does not match a dataframe column."
        for key in plan.labels
        if key not in columns and key not in {"value", "variable", "count"}
    ]
    return list(dict.fromkeys(errors))


def render_px_code(plan: "BaseChartPlan", chart_name: str = CUSTOM_CHART_NAME, vizro: bool = False) -> str:
    """Template the plotly-express code equivalent to `build_figure`. A derived string; never executed.

    Built from the same kwargs as the rendered figure, so the code and the figure cannot diverge.
    """
    if not chart_name.isidentifier():
        raise ValueError(f"chart_name {chart_name!r} must be a valid Python identifier.")
    parts = [f"{k}={v!r}" for k, v in _plan_kwargs(plan).items()]
    call = f"px.{plan.chart_type}(data_frame{', ' + ', '.join(parts) if parts else ''})"
    if vizro:
        # A standard plotly-express chart drops straight into vm.Graph via vizro.plotly.express.
        # `@capture('graph')` is only for *custom* charts (post-update / customization), which we
        # never produce, so it is not used here.
        imports = "import vizro.plotly.express as px"
        usage = f"# Use in a dashboard: vm.Graph(figure={chart_name}(data_frame))\n"
    else:
        imports = "import plotly.express as px"
        usage = ""
    return f"{imports}\n\n\n{usage}def {chart_name}(data_frame):\n    return {call}\n"


def _vizro_px_builder(chart_type: str) -> Callable[..., go.Figure]:
    """The vizro.plotly.express counterpart of a chart builder (Vizro-themed, vm.Graph-ready)."""
    try:
        import vizro.plotly.express as vizro_px
    except ImportError as e:
        raise RuntimeError("Please install `vizro` to use Vizro features — `pip install vizro`") from e
    return getattr(vizro_px, chart_type)


# --------------------------------------------------------------------------------------
# Chart plan models. Same public names as before; fields are now a declarative spec, and
# materialising a chart runs trusted `build_figure`, not `exec()` of model output.
# --------------------------------------------------------------------------------------
class BaseChartPlan(BaseModel):
    """Base chart plan describing a chart declaratively (no code).

    The model fills these fields; a chart is produced by trusted `plotly.express` code via
    `build_figure`. `figure()` / `to_figure_json()` give a rendered figure (or JSON for a
    frontend); `code` / `code_vizro` give the equivalent plotly-express code as a string.
    Vizro-AI does not reshape data — pass a dataframe already in the shape you want to plot.
    """

    # extra="forbid" turns misplaced top-level keys (e.g. a flat {"x": ..., "y": ...} instead of
    # nesting under encodings — a common LLM shape error) into retryable validation errors
    # instead of pydantic silently dropping them and leaving an empty plan.
    model_config = ConfigDict(extra="forbid")

    chart_type: str = Field(description=f"Plotly-express chart type. One of: {', '.join(CHART_TYPES)}.")
    encodings: dict[str, str | list[str]] = Field(
        default_factory=dict,
        description=(
            "Map plotly-express column arguments to columns of the (already-shaped) data, e.g. "
            '{"x": "year", "y": "gdp", "color": "continent"}. For a pie use "names" and "values". '
            'A few arguments (e.g. "path", "dimensions") take a list of columns.'
        ),
    )
    title: str = Field("", description="Chart title.")
    labels: dict[str, str] = Field(
        default_factory=dict,
        description='Optional axis/legend label overrides, keyed by column name, e.g. {"gdp": "GDP per capita"}.',
    )
    options: dict[str, JsonValue] = Field(
        default_factory=dict,
        description=(
            "Other plotly-express styling arguments, e.g. "
            '{"barmode": "group", "log_y": true, "range_y": [0, 100], "color_discrete_sequence": ["#00b4ff"]}.'
        ),
    )

    @field_validator("chart_type")
    @classmethod
    def _known_chart_type(cls, v: str) -> str:
        _check_chart_type(v)
        return v

    @field_validator("options")
    @classmethod
    def _finite_options(cls, v: dict[str, JsonValue]) -> dict[str, JsonValue]:
        # JSON parsing accepts NaN/Infinity into floats, but no plotly argument uses them and
        # their repr ('nan') would not round-trip through the templated code.
        bad = sorted(key for key, value in v.items() if _contains_non_finite(value))
        if bad:
            raise ValueError(f"Options {bad} contain non-finite numbers (NaN/Infinity).")
        return v

    def referenced_columns(self) -> list[str]:
        """Every dataframe column this plan relies on."""
        cols: list[str] = []
        for value in self.encodings.values():
            cols.extend([value] if isinstance(value, str) else value)
        return list(dict.fromkeys(cols))

    def figure(self, data_frame: pd.DataFrame, **kwargs) -> go.Figure:
        """Render the plan to a Plotly figure with trusted code (no `exec()`).

        Keyword arguments are plotly-express overrides applied on top of the plan.
        """
        return build_figure(self, data_frame, **kwargs)

    def to_figure_json(self, data_frame: pd.DataFrame) -> str:
        """Render and serialize to Plotly figure JSON — inert data a frontend can render."""
        return self.figure(data_frame).to_json()

    def get_chart_function(self, chart_name: str = CUSTOM_CHART_NAME, vizro: bool = False) -> Callable[..., go.Figure]:
        """Return a reusable callable ``(data_frame, **kwargs) -> go.Figure`` that renders this plan.

        No code is executed: the returned function builds the figure from the plan with trusted
        plotly-express code. Keyword arguments are plotly-express overrides applied on top of
        the plan (e.g. ``title="..."``), so they must be arguments the chart type accepts.

        With ``vizro=True`` the figure is built with `vizro.plotly.express`, so it is
        Vizro-themed and drops straight into ``vm.Graph`` — including Vizro dashboard code
        export, which serializes it as a plain ``px.<chart>(...)`` call.

        Example:
            ```python
            chart_func = result.output.get_chart_function()
            fig = chart_func(df, title="My title")
            ```
        """
        if not chart_name.isidentifier():
            raise ValueError(f"chart_name {chart_name!r} must be a valid Python identifier.")
        builder = _vizro_px_builder(self.chart_type) if vizro else CHART_BUILDERS[self.chart_type]
        plan = self

        def chart(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
            merged = _plan_kwargs(plan)
            merged.update(kwargs)
            return builder(data_frame, **merged)  # type: ignore[operator]

        chart.__name__ = chart_name
        return chart

    @property
    def chart_function(self) -> Callable[..., go.Figure]:
        """A callable that renders a pure Plotly figure from a dataframe (kwargs are overrides)."""
        return self.get_chart_function(chart_name=CUSTOM_CHART_NAME, vizro=False)

    @property
    def vizro_chart_function(self) -> Callable[..., go.Figure]:
        """A callable that renders a Vizro-themed, `vm.Graph`-ready figure from a dataframe."""
        return self.get_chart_function(chart_name=CUSTOM_CHART_NAME, vizro=True)

    @property
    def code(self) -> str:
        """The equivalent pure-Plotly code as a string (templated from the plan; never executed)."""
        return render_px_code(self)

    @property
    def code_vizro(self) -> str:
        """The equivalent Vizro-compatible chart code as a string (never executed)."""
        return render_px_code(self, vizro=True)


class ChartPlan(BaseChartPlan):
    """Extended chart plan with an explanatory field."""

    chart_insights: str = Field(
        description="""
        Insights to what the chart explains or tries to show.
        Ideally concise and between 30 and 60 words.""",
    )


class ChartPlanFactory:
    def __new__(cls, data_frame: pd.DataFrame, chart_plan: type[BaseChartPlan] = ChartPlan) -> type[BaseChartPlan]:
        """Create a chart plan model that validates the plan against `data_frame` (no execution).

        Validation checks the plan's keys and referenced columns against the data and
        test-renders it with `build_figure` — it never runs model-authored code.

        Args:
            data_frame: DataFrame to validate against.
            chart_plan: Chart plan model to add validation to.

        Returns:
            Chart plan model with data-aware validation.
        """
        # Validate against a small sample: it has the same columns and dtypes, so the checks are
        # identical, but a huge frame is neither rendered on every validation nor kept alive for
        # the lifetime of the returned class.
        sample_rows = 10
        sample = data_frame if len(data_frame) <= sample_rows else data_frame.sample(sample_rows, replace=True)

        def _validate(self: BaseChartPlan) -> BaseChartPlan:
            errors = validate_against_data(self, sample)
            if errors:
                raise ValueError("The chart plan does not fit the data: " + " ".join(errors))
            try:
                build_figure(self, sample)
            except Exception as e:
                raise ValueError(f"The chart plan could not be rendered (<{type(e).__name__}: {e}>).") from e
            return self

        return create_model(
            "ChartPlanDynamic",
            __base__=chart_plan,
            __validators__={"validate_against_data": model_validator(mode="after")(_validate)},
        )
