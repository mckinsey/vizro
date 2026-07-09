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
from collections.abc import Callable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.express._core import all_attrables
from pydantic import BaseModel, Field, create_model, field_validator, model_validator

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

Scalar = str | int | float | bool


def _signature_params(chart_type: str) -> set[str]:
    return set(inspect.signature(CHART_BUILDERS[chart_type]).parameters)  # type: ignore[arg-type]


def allowed_encodings(chart_type: str) -> set[str]:
    """Column-mapping arguments valid for a chart type — derived from its plotly signature."""
    return COLUMN_ENCODINGS & _signature_params(chart_type)


def styling_options(chart_type: str) -> set[str]:
    """Non-column styling arguments valid for a chart type — derived from its plotly signature."""
    return _signature_params(chart_type) - COLUMN_ENCODINGS - {"data_frame"}


# --------------------------------------------------------------------------------------
# Trusted rendering — plotly express only. The only place a figure is built; no data reshaping.
# --------------------------------------------------------------------------------------
def build_figure(plan: "BaseChartPlan", data_frame: pd.DataFrame) -> go.Figure:
    """Turn a chart plan into a Plotly figure. This is the whole 'execution' — no `exec()`.

    `data_frame` must already be in the shape to plot; Vizro-AI does not transform data.
    """
    if plan.chart_type not in CHART_BUILDERS:
        raise ValueError(f"Unknown chart_type {plan.chart_type!r}. Choose one of: {CHART_TYPES}")
    builder = CHART_BUILDERS[plan.chart_type]
    valid = _signature_params(plan.chart_type)
    kwargs: dict = {k: v for k, v in plan.encodings.items() if k in valid}
    kwargs.update({k: v for k, v in plan.options.items() if k in valid})
    if plan.labels and "labels" in valid:
        kwargs["labels"] = plan.labels
    if plan.title and "title" in valid:
        kwargs["title"] = plan.title
    return builder(data_frame, **kwargs)  # type: ignore[operator]


def validate_against_data(plan: "BaseChartPlan", data_frame: pd.DataFrame) -> list[str]:
    """Return human-readable problems with a plan against the data, or [] if it is valid."""
    if plan.chart_type not in CHART_BUILDERS:
        return [f"Unknown chart_type {plan.chart_type!r}. Choose one of: {CHART_TYPES}."]
    columns = set(data_frame.columns)
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
    errors += [f"Column '{col}' is not in the data." for col in plan.referenced_columns() if col not in columns]
    return list(dict.fromkeys(errors))


def render_px_code(plan: "BaseChartPlan", chart_name: str = CUSTOM_CHART_NAME, vizro: bool = False) -> str:
    """Template equivalent plotly-express code from a plan. A derived string; never executed."""
    parts = [f"{k}={v!r}" for k, v in plan.encodings.items()]
    parts += [f"{k}={v!r}" for k, v in plan.options.items()]
    if plan.labels:
        parts.append(f"labels={plan.labels!r}")
    if plan.title:
        parts.append(f"title={plan.title!r}")
    call = f"px.{plan.chart_type}(data_frame{', ' + ', '.join(parts) if parts else ''})"
    if vizro:
        # A standard plotly-express chart drops straight into vm.Graph via vizro.plotly.express.
        # `@capture('graph')` is only for *custom* charts (post-update / customization), which we
        # never produce, so it is not used here.
        return f"import vizro.plotly.express as px\n\n# use in a dashboard: vm.Graph(figure=figure)\nfigure = {call}\n"
    return f"import plotly.express as px\n\n\ndef {chart_name}(data_frame):\n    return {call}\n"


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
    labels: dict[str, str] = Field(default_factory=dict, description="Optional axis/legend label overrides.")
    options: dict[str, Scalar] = Field(
        default_factory=dict,
        description='Other plotly-express styling arguments, e.g. {"barmode": "group", "log_y": true}.',
    )

    @field_validator("chart_type")
    @classmethod
    def _known_chart_type(cls, v: str) -> str:
        if v not in CHART_BUILDERS:
            raise ValueError(f"Unknown chart_type {v!r}. Choose one of: {CHART_TYPES}")
        return v

    def referenced_columns(self) -> list[str]:
        """Every dataframe column this plan relies on."""
        cols: list[str] = []
        for value in self.encodings.values():
            cols.extend([value] if isinstance(value, str) else value)
        return list(dict.fromkeys(cols))

    def figure(self, data_frame: pd.DataFrame) -> go.Figure:
        """Render the plan to a Plotly figure with trusted code (no `exec()`)."""
        return build_figure(self, data_frame)

    def to_figure_json(self, data_frame: pd.DataFrame) -> str:
        """Render and serialize to Plotly figure JSON — inert data a frontend can render."""
        return self.figure(data_frame).to_json()

    def get_chart_function(self, chart_name: str = CUSTOM_CHART_NAME, vizro: bool = False) -> Callable[..., go.Figure]:
        """Return a reusable callable ``(data_frame, **kwargs) -> go.Figure`` that renders this plan.

        No code is executed: the returned function calls the trusted `build_figure`. With
        ``vizro=True`` it is wrapped as a Vizro `@capture('graph')` function for dashboards.

        Example:
            ```python
            chart_func = result.output.get_chart_function()
            fig = chart_func(df)
            ```
        """
        plan = self

        def chart(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
            return build_figure(plan, data_frame)

        chart.__name__ = chart_name
        if not vizro:
            return chart
        try:
            from vizro.models.types import capture
        except ModuleNotFoundError as e:
            raise RuntimeError("Please install `vizro` to use Vizro features — `pip install vizro`") from e
        return capture("graph")(chart)

    @property
    def chart_function(self) -> Callable[..., go.Figure]:
        """A callable that renders a pure Plotly figure from a dataframe."""
        return self.get_chart_function(chart_name=CUSTOM_CHART_NAME, vizro=False)

    @property
    def vizro_chart_function(self) -> Callable[..., go.Figure]:
        """A Vizro-compatible (`@capture('graph')`) callable that renders the figure."""
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

        Validation checks that referenced columns exist and that the plan renders with
        `build_figure` — it never runs model-authored code.

        Args:
            data_frame: DataFrame to validate against.
            chart_plan: Chart plan model to add validation to.

        Returns:
            Chart plan model with data-aware validation.
        """

        def _validate(self: BaseChartPlan) -> BaseChartPlan:
            errors = validate_against_data(self, data_frame)
            if errors:
                raise ValueError("The chart plan does not fit the data: " + " ".join(errors))
            try:
                build_figure(self, data_frame)
            except Exception as e:
                raise ValueError(f"The chart plan could not be rendered (<{type(e).__name__}: {e}>).")
            return self

        return create_model(
            "ChartPlanDynamic",
            __base__=chart_plan,
            __validators__={"validate_against_data": model_validator(mode="after")(_validate)},
        )
