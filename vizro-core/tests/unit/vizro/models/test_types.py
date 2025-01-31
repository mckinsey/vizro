import re

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import pytest
from pydantic import Field, ValidationError, field_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models.types import CapturedCallable, capture, validate_captured_callable


def positional_only_function(a, /):
    pass


def var_positional_function(*args):
    pass


@pytest.mark.parametrize("function", [positional_only_function, var_positional_function])
def test_invalid_parameter_kind(function):
    with pytest.raises(
        ValueError,
        match="CapturedCallable does not accept functions with positional-only or variadic positional parameters",
    ):
        CapturedCallable(function)


def positional_or_keyword_function(a, b, c):
    return a + b + c


def keyword_only_function(a, *, b, c):
    return a + b + c


def var_keyword_function(a, **kwargs):
    return a + kwargs["b"] + kwargs["c"]


@pytest.fixture
def captured_callable(request):
    return CapturedCallable(request.param, 1, b=2)


@pytest.mark.parametrize(
    "captured_callable", [positional_or_keyword_function, keyword_only_function, var_keyword_function], indirect=True
)
class TestCallKeywordArguments:
    def test_call_provide_required_argument(self, captured_callable):
        assert captured_callable(c=3) == 1 + 2 + 3

    def test_call_override_existing_arguments(self, captured_callable):
        assert captured_callable(a=5, b=2, c=6) == 5 + 2 + 6


@pytest.mark.parametrize("captured_callable", [positional_or_keyword_function], indirect=True)
def test_call_positional_arguments(captured_callable):
    assert captured_callable(3) == 1 + 2 + 3


@pytest.mark.parametrize(
    "captured_callable", [positional_or_keyword_function, keyword_only_function, var_keyword_function], indirect=True
)
class TestDunderMethods:
    def test_getitem_known_args(self, captured_callable):
        assert captured_callable["a"] == 1
        assert captured_callable["b"] == 2

    def test_getitem_unknown_args(self, captured_callable):
        with pytest.raises(KeyError):
            captured_callable["c"]

    def test_setitem(self, captured_callable):
        captured_callable["a"] = 2
        assert captured_callable["a"] == 2


@pytest.mark.parametrize(
    "captured_callable", [positional_or_keyword_function, keyword_only_function, var_keyword_function], indirect=True
)
def test_call_positional_and_keyword_supplied(captured_callable):
    with pytest.raises(ValueError, match="does not support calling with both positional and keyword arguments"):
        captured_callable(3, c=4)


@pytest.mark.parametrize(
    "captured_callable, expectation",
    [
        (positional_or_keyword_function, pytest.raises(TypeError, match="missing 1 required positional argument: 'c'")),
        (keyword_only_function, pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'c'")),
        (var_keyword_function, pytest.raises(KeyError, match="'c'")),
    ],
    indirect=["captured_callable"],
)
class TestCallMissingArgument:
    def test_call_missing_argument(self, captured_callable, expectation):
        with expectation:
            captured_callable()

    def test_call_is_memoryless(self, captured_callable, expectation):
        captured_callable(c=3)

        with expectation:
            captured_callable()


@pytest.mark.parametrize(
    "captured_callable, expectation",
    [
        (
            positional_or_keyword_function,
            pytest.raises(TypeError, match="takes 1 positional arguments but 2 were given"),
        ),
        (keyword_only_function, pytest.raises(TypeError, match="takes 0 positional arguments but 2 were given")),
        (var_keyword_function, pytest.raises(TypeError, match="takes 0 positional arguments but 2 were given")),
    ],
    indirect=["captured_callable"],
)
class TestCallPositionalArguments:
    def test_call_positional_arguments_invalid(self, captured_callable, expectation):
        with expectation:
            captured_callable(3, 4)


@pytest.mark.parametrize(
    "captured_callable, expectation",
    [
        (positional_or_keyword_function, pytest.raises(TypeError, match="got an unexpected keyword argument")),
        (keyword_only_function, pytest.raises(TypeError, match="got an unexpected keyword argument")),
        (var_keyword_function, pytest.raises(KeyError, match="'c'")),
    ],
    indirect=["captured_callable"],
)
def test_call_unknown_argument(captured_callable, expectation):
    with expectation:
        captured_callable(e=1)


def undecorated_function(a, b, c, d=4):
    return go.Figure()


@capture("action")
def decorated_action_function(a, b, c, d=4):
    return a + b + c + d


@capture("graph")
def decorated_graph_function(data_frame):
    return go.Figure()


@capture("graph")
def invalid_decorated_graph_function():
    return go.Figure()


class ModelWithAction(VizroBaseModel):
    # The import_path here makes it possible to import the above function using getattr(import_path, _target_).
    function: SkipJsonSchema[CapturedCallable] = Field(json_schema_extra={"mode": "action", "import_path": __name__})
    _validate_figure = field_validator("function", mode="before")(validate_captured_callable)


class ModelWithGraph(VizroBaseModel):
    # The import_path here makes it possible to import the above function using getattr(import_path, _target_).
    function: SkipJsonSchema[CapturedCallable] = Field(json_schema_extra={"mode": "graph", "import_path": __name__})
    _validate_figure = field_validator("function", mode="before")(validate_captured_callable)


class TestModelFieldPython:
    def test_decorated_action_function(self):
        model = ModelWithAction(function=decorated_action_function(a=1, b=2))
        assert model.function(c=3, d=4) == 1 + 2 + 3 + 4

    def test_decorated_graph_function(self):
        model = ModelWithGraph(function=decorated_graph_function(data_frame=pd.DataFrame()))
        assert model.function() == go.Figure()

    def test_undecorated_function(self):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "Invalid CapturedCallable. Supply a function imported from tests.unit.vizro.models.test_types or "
                "defined with decorator @capture('graph')."
            ),
        ):
            ModelWithGraph(function=undecorated_function(1, 2, 3))

    def test_wrong_mode(self):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "CapturedCallable was defined with @capture('action') rather than @capture('graph') and so "
                "is not compatible with the model."
            ),
        ):
            ModelWithGraph(function=decorated_action_function(a=1, b=2))


class TestCapture:
    def test_decorated_graph_function_missing_data_frame(self):
        with pytest.raises(ValueError, match="decorated_graph_function must supply a value to data_frame argument"):
            decorated_graph_function()

    def test_invalid_decorated_graph_function(self):
        with pytest.raises(ValueError, match="invalid_decorated_graph_function must have data_frame argument"):
            invalid_decorated_graph_function()


class TestModelFieldJSONConfig:
    def test_no_arguments(self):
        config = {"_target_": "decorated_action_function"}
        model = ModelWithAction(function=config)
        assert isinstance(model.function, CapturedCallable)
        assert model.function(a=1, b=2, c=3, d=4) == 1 + 2 + 3 + 4

    def test_some_arguments(self):
        config = {"_target_": "decorated_action_function", "a": 1, "b": 2}
        model = ModelWithAction(function=config)
        assert isinstance(model.function, CapturedCallable)
        assert model.function(c=3) == 1 + 2 + 3 + 4

    def test_all_arguments(self):
        config = {"_target_": "decorated_action_function", "a": 1, "b": 2, "c": 3}
        model = ModelWithAction(function=config)
        assert isinstance(model.function, CapturedCallable)
        assert model.function() == 1 + 2 + 3 + 4

    def test_decorated_graph_function(self):
        config = {"_target_": "decorated_graph_function", "data_frame": "data_source_name"}
        model = ModelWithGraph(function=config)
        assert model.function() == go.Figure()

    def test_no_target(self):
        config = {"a": 1, "b": 2}
        with pytest.raises(ValidationError, match="must contain the key '_target_'"):
            ModelWithGraph(function=config)

    def test_invalid_import(self):
        config = {"_target_": "invalid_function"}
        with pytest.raises(ValidationError, match="_target_=invalid_function cannot be imported"):
            ModelWithGraph(function=config)

    def test_invalid_arguments(self):
        config = {"_target_": "decorated_action_function", "e": 5}
        with pytest.raises(TypeError, match="got an unexpected keyword argument"):
            ModelWithGraph(function=config)

    def test_undecorated_function(self):
        config = {"_target_": "undecorated_function", "a": 1, "b": 2, "c": 3}
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "Invalid CapturedCallable. Supply a function imported from tests.unit.vizro.models.test_types or "
                "defined with decorator @capture('graph')."
            ),
        ):
            ModelWithGraph(function=config)

    def test_wrong_mode(self):
        config = {"_target_": "decorated_action_function", "a": 1, "b": 2}
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "CapturedCallable was defined with @capture('action') rather than @capture('graph') and so "
                "is not compatible with the model."
            ),
        ):
            ModelWithGraph(function=config)

    def test_invalid_import_path(self):
        class ModelWithInvalidModule(VizroBaseModel):
            # The import_path doesn't exist.
            function: CapturedCallable = Field(json_schema_extra={"mode": "graph", "import_path": "invalid.module"})

            _validate_figure = field_validator("function", mode="before")(validate_captured_callable)

        config = {"_target_": "decorated_graph_function", "data_frame": "data_source_name"}

        with pytest.raises(
            ValueError, match="_target_=decorated_graph_function cannot be imported from invalid.module."
        ):
            ModelWithInvalidModule(function=config)


@capture("graph")
def decorated_graph_function_with_template(data_frame, template=None):
    fig = go.Figure()
    if template is not None:
        fig.layout.template = template
    return fig


@capture("graph")
def decorated_graph_function_crash(data_frame):
    raise RuntimeError("Crash")


# The _pio_default_template context manager resets pio.templates.default on exit, but the fixture should do this also.
# This fixtures acts as if someone has set the pio.templates.default e.g. in a Jupyter notebook.
@pytest.fixture
def set_pio_default_template(request):
    old_default = pio.templates.default
    pio.templates.default = request.param
    yield request.param
    pio.templates.default = old_default


# The expected template is always the same as the template_argument for the cases of vizro_dark and vizro_light.
# For template=None and template="plotly" the expected template is the same as the globally set default template when
# it's vizro_dark/vizro_light and vizro_dark when it's set to plotly.
@pytest.mark.parametrize(
    "set_pio_default_template, template_argument, expected_template",
    [
        ("plotly", None, "vizro_dark"),
        ("plotly", "plotly", "vizro_dark"),
        ("plotly", "vizro_dark", "vizro_dark"),
        ("plotly", "vizro_light", "vizro_light"),
        ("vizro_dark", None, "vizro_dark"),
        ("vizro_dark", "plotly", "vizro_dark"),
        ("vizro_dark", "vizro_dark", "vizro_dark"),
        ("vizro_dark", "vizro_light", "vizro_light"),
        ("vizro_light", None, "vizro_light"),
        ("vizro_light", "plotly", "vizro_light"),
        ("vizro_light", "vizro_dark", "vizro_dark"),
        ("vizro_light", "vizro_light", "vizro_light"),
    ],
    indirect=["set_pio_default_template"],
)
def test_graph_templates(set_pio_default_template, template_argument, expected_template):
    graph = decorated_graph_function_with_template(pd.DataFrame(), template=template_argument)
    assert graph.layout.template == pio.templates[expected_template]
    # The default template should be unchanged after running the captured function.
    assert pio.templates.default == set_pio_default_template


@pytest.mark.parametrize("set_pio_default_template", ["plotly", "vizro_dark", "vizro_light"], indirect=True)
def test_graph_template_crash(set_pio_default_template):
    with pytest.raises(RuntimeError, match="Crash"):
        decorated_graph_function_crash(pd.DataFrame())
    # The default template should be unchanged even if the captured function crashes.
    assert pio.templates.default == set_pio_default_template
