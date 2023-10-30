import plotly.express as plotly_express
import plotly.graph_objects as go
import pytest
from pydantic import Field, ValidationError

from vizro.charts._charts_utils import _DashboardReadyFigure
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
    "captured_callable",
    [positional_or_keyword_function, keyword_only_function, var_keyword_function],
    indirect=True,
)
class TestCall:
    def test_call_needs_keyword_arguments(self, captured_callable):
        with pytest.raises(TypeError, match="takes 1 positional argument but 2 were given"):
            captured_callable(2)

    def test_call_provide_required_argument(self, captured_callable):
        assert captured_callable(c=3) == 1 + 2 + 3

    def test_call_override_existing_arguments(self, captured_callable):
        assert captured_callable(a=5, b=2, c=6) == 5 + 2 + 6


@pytest.mark.parametrize(
    "captured_callable",
    [positional_or_keyword_function, keyword_only_function, var_keyword_function],
    indirect=True,
)
class TestDunderMethods:
    def test_getitem_known_args(self, captured_callable):
        assert captured_callable["a"] == 1
        assert captured_callable["b"] == 2

    def test_getitem_unknown_args(self, captured_callable):
        with pytest.raises(KeyError):
            captured_callable["c"]

    def test_delitem(self, captured_callable):
        del captured_callable["a"]

        with pytest.raises(KeyError):
            captured_callable["a"]


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
    return a + b + c + d


@capture("action")
def decorated_action_function(a, b, c, d=4):
    return a + b + c + d


@capture("graph")
def decorated_graph_function(data_frame):
    return go.Figure()


@capture("graph")
def decorated_graph_function_px(data_frame):
    return plotly_express.scatter(
        data_frame=data_frame,
        x="gdpPercap",
        y="lifeExp",
    )


@capture("graph")
def invalid_decorated_graph_function():
    return go.Figure()


class Model(VizroBaseModel):
    # The import_path here makes it possible to import the above function using getattr(import_path, _target_).
    function: CapturedCallable = Field(..., import_path=__import__(__name__))


class TestModelFieldPython:
    def test_decorated_action_function(self):
        model = Model(function=decorated_action_function(a=1, b=2))
        assert model.function(c=3, d=4) == 1 + 2 + 3 + 4

    def test_decorated_graph_function(self):
        model = Model(function=decorated_graph_function(data_frame=None))
        assert model.function() == go.Figure()

    def test_undecorated_function(self):
        with pytest.raises(ValidationError, match="provide a valid CapturedCallable object"):
            Model(function=undecorated_function(1, 2, 3))


class TestCapture:
    def test_decorated_df_standard_case(self, gapminder):
        fig = decorated_graph_function_px(gapminder)
        assert len(fig.data) > 0
        assert fig.__class__ == _DashboardReadyFigure

    def test_decorated_df_str(self):
        fig = decorated_graph_function_px("gapminder")
        assert fig == _DashboardReadyFigure()
        assert len(fig.data) == 0

    def test_decorated_graph_function_missing_data_frame(self):
        with pytest.raises(
            ValueError,
            match="decorated_graph_function must supply a value to data_frame argument",
        ):
            decorated_graph_function()

    def test_invalid_decorated_graph_function(self):
        with pytest.raises(
            ValueError,
            match="invalid_decorated_graph_function must have data_frame argument",
        ):
            invalid_decorated_graph_function()


class TestModelFieldJSONConfig:
    def test_no_arguments(self):
        config = {"_target_": "decorated_action_function"}
        model = Model(function=config)
        assert isinstance(model.function, CapturedCallable)
        assert model.function(a=1, b=2, c=3, d=4) == 1 + 2 + 3 + 4

    def test_some_arguments(self):
        config = {"_target_": "decorated_action_function", "a": 1, "b": 2}
        model = Model(function=config)
        assert isinstance(model.function, CapturedCallable)
        assert model.function(c=3) == 1 + 2 + 3 + 4

    def test_all_arguments(self):
        config = {"_target_": "decorated_action_function", "a": 1, "b": 2, "c": 3}
        model = Model(function=config)
        assert isinstance(model.function, CapturedCallable)
        assert model.function() == 1 + 2 + 3 + 4

    def test_decorated_graph_function(self):
        config = {"_target_": "decorated_graph_function", "data_frame": None}
        model = Model(function=config)
        assert model.function() == go.Figure()

    def test_no_target(self):
        config = {"a": 1, "b": 2}
        with pytest.raises(ValidationError, match="must contain the key '_target_'"):
            Model(function=config)

    def test_invalid_import(self):
        config = {"_target_": "invalid_function"}
        with pytest.raises(ValidationError, match="_target_=invalid_function cannot be imported"):
            Model(function=config)

    def test_invalid_arguments(self):
        config = {"_target_": "decorated_action_function", "e": 5}
        with pytest.raises(ValidationError, match="got an unexpected keyword argument"):
            Model(function=config)

    def test_undecorated_function(self):
        config = {"_target_": "undecorated_function", "a": 1, "b": 2, "c": 3}
        with pytest.raises(ValidationError, match="_target_=undecorated_function must be wrapped"):
            Model(function=config)
