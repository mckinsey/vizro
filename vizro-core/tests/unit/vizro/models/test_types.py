import re

import plotly.graph_objects as go
import plotly.io as pio
import pytest

try:
    from pydantic.v1 import Field, ValidationError
except ImportError:  # pragma: no cov
    from pydantic import Field, ValidationError

from vizro.models import VizroBaseModel
from vizro.models.types import CapturedCallable, capture


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
    function: CapturedCallable = Field(..., import_path=__name__, mode="action")


class ModelWithGraph(VizroBaseModel):
    # The import_path here makes it possible to import the above function using getattr(import_path, _target_).
    function: CapturedCallable = Field(..., import_path=__name__, mode="graph")


class TestModelFieldPython:
    def test_decorated_action_function(self):
        model = ModelWithAction(function=decorated_action_function(a=1, b=2))
        assert model.function(c=3, d=4) == 1 + 2 + 3 + 4

    def test_decorated_graph_function(self):
        model = ModelWithGraph(function=decorated_graph_function(data_frame=None))
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
        config = {"_target_": "decorated_graph_function", "data_frame": None}
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
        with pytest.raises(ValidationError, match="got an unexpected keyword argument"):
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
            function: CapturedCallable = Field(..., import_path="invalid.module", mode="graph")

        config = {"_target_": "decorated_graph_function", "data_frame": None}

        with pytest.raises(
            ValueError, match="_target_=decorated_graph_function cannot be imported from invalid.module."
        ):
            ModelWithInvalidModule(function=config)


@capture("graph")
def decorated_graph_function(data_frame):
    return go.Figure()


@capture("graph")
def decorated_graph_function_themed(data_frame, template):
    fig = go.Figure()
    fig.layout.template = template
    return fig


@capture("graph")
def decorated_graph_function_crash(data_frame):
    raise RuntimeError("Crash")


# @capture("graph")
# def decorated_graph_function(data_frame):
#     return px.

# @pytest.fixture(params=["vizro_dark", "vizro_light", "plotly"])
# def template(request):
#     return request.param


@pytest.fixture
def set_pio_default_template_dark():
    old_default = pio.templates.default
    pio.templates.default = "vizro_dark"
    yield
    pio.templates.default = old_default


@pytest.fixture
def set_pio_default_template_light():
    old_default = pio.templates.default
    pio.templates.default = "vizro_light"
    yield
    pio.templates.default = old_default


@pytest.fixture
def set_pio_default_template_plotly():
    old_default = pio.templates.default
    pio.templates.default = "plotly"
    yield
    pio.templates.default = old_default


class TestGraphTemplate:
    def test(self, set_pio_default_template_dark):
        graph = decorated_graph_function(None)
        assert graph.layout.template == pio.templates["vizro_dark"]
        assert pio.templates.default == "vizro_dark"

    def test2(self, set_pio_default_template_light):
        graph = decorated_graph_function(None)
        assert graph.layout.template == pio.templates["vizro_light"]
        assert pio.templates.default == "vizro_light"

    def test3(self, set_pio_default_template_plotly):
        graph = decorated_graph_function(None)
        assert graph.layout.template == pio.templates["vizro_dark"]
        assert pio.templates.default == "plotly"

    def test4(self, set_pio_default_template_dark):
        graph = decorated_graph_function_themed(None, "vizro_dark")
        assert graph.layout.template == pio.templates["vizro_dark"]
        assert pio.templates.default == "vizro_dark"

    def test5(self, set_pio_default_template_dark):
        graph = decorated_graph_function_themed(None, "vizro_light")
        assert graph.layout.template == pio.templates["vizro_light"]
        assert pio.templates.default == "vizro_dark"

    def test6(self, set_pio_default_template_dark):
        graph = decorated_graph_function_themed(None, "plotly")
        assert graph.layout.template == pio.templates["vizro_dark"]
        assert pio.templates.default == "vizro_dark"

    def test7(self, set_pio_default_template_light):
        graph = decorated_graph_function_themed(None, "vizro_dark")
        assert graph.layout.template == pio.templates["vizro_dark"]
        assert pio.templates.default == "vizro_light"

    def test8(self, set_pio_default_template_light):
        graph = decorated_graph_function_themed(None, "vizro_light")
        assert graph.layout.template == pio.templates["vizro_light"]
        assert pio.templates.default == "vizro_light"

    def test9(self, set_pio_default_template_light):
        graph = decorated_graph_function_themed(None, "plotly")
        assert graph.layout.template == pio.templates["vizro_light"]
        assert pio.templates.default == "vizro_light"

    def test10(self, set_pio_default_template_plotly):
        graph = decorated_graph_function_themed(None, "vizro_dark")
        assert graph.layout.template == pio.templates["vizro_dark"]
        assert pio.templates.default == "plotly"

    def test11(self, set_pio_default_template_plotly):
        graph = decorated_graph_function_themed(None, "vizro_light")
        assert graph.layout.template == pio.templates["vizro_light"]
        assert pio.templates.default == "plotly"

    def test12(self, set_pio_default_template_plotly):
        graph = decorated_graph_function_themed(None, "plotly")
        assert graph.layout.template == pio.templates["vizro_dark"]
        assert pio.templates.default == "plotly"

    # Could parametrise this 3 times too if can be bothered...
    def test13(self, set_pio_default_template_plotly):
        with pytest.raises(RuntimeError, match="Crash"):
            decorated_graph_function_crash(None)
        assert pio.templates.default == "plotly"
