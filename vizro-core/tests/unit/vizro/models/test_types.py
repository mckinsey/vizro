import plotly.express as plotly_express
import plotly.graph_objects as go
import pytest
from pydantic import Field, ValidationError

from vizro.charts._charts_utils import _DashboardReadyFigure
from vizro.models import VizroBaseModel
from vizro.models.types import CapturedCallable, capture


@pytest.fixture
def varargs_function():
    def function(*args, b=2):
        return args[0] + b

    return CapturedCallable(function, 1)


@pytest.mark.xfail
# Known bug: *args doesn't work properly. Fix while keeping the more important test_varkwargs
# passing due to https://bugs.python.org/issue41745.
# Error raised is IndexError: tuple index out of range
def test_varargs(varargs_function):
    assert varargs_function(b=2) == 1 + 2


@pytest.fixture
def positional_only_function():
    def function(a, /, b):
        return a + b

    return CapturedCallable(function, 1)


@pytest.mark.xfail
# Known bug: position-only argument doesn't work properly. Fix while keeping the more important
# test_varkwargs passing due to https://bugs.python.org/issue41745.
# Error raised is TypeError: function got some positional-only arguments passed as keyword arguments: 'a'
def test_positional_only(positional_only_function):
    assert positional_only_function(b=2) == 1 + 2


@pytest.fixture
def keyword_only_function():
    def function(a, *, b):
        return a + b

    return CapturedCallable(function, 1)


def test_keyword_only(keyword_only_function):
    assert keyword_only_function(b=2) == 1 + 2


@pytest.fixture
def varkwargs_function():
    def function(a, b=2, **kwargs):
        return a + b + kwargs["c"]

    return CapturedCallable(function, 1)


def test_varkwargs(varkwargs_function):
    varkwargs_function(c=3, d=4) == 1 + 2 + 3


@pytest.fixture
def simple_function():
    def function(a, b, c, d=4):
        return a + b + c + d

    return CapturedCallable(function, 1, b=2)


class TestCall:
    def test_call_missing_argument(self, simple_function):
        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            simple_function()

    def test_call_needs_keyword_arguments(self, simple_function):
        with pytest.raises(TypeError, match="takes 1 positional argument but 2 were given"):
            simple_function(2)

    def test_call_provide_required_argument(self, simple_function):
        assert simple_function(c=3) == 1 + 2 + 3 + 4

    def test_call_override_existing_arguments(self, simple_function):
        assert simple_function(a=5, b=2, c=6) == 5 + 2 + 6 + 4

    def test_call_is_memoryless(self, simple_function):
        simple_function(c=3)

        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            simple_function()

    def test_call_unknown_argument(self, simple_function):
        with pytest.raises(TypeError, match="got an unexpected keyword argument"):
            simple_function(e=1)


class TestDunderMethods:
    def test_getitem_known_args(self, simple_function):
        assert simple_function["a"] == 1
        assert simple_function["b"] == 2

    def test_getitem_unknown_args(self, simple_function):
        with pytest.raises(KeyError):
            simple_function["c"]

        with pytest.raises(KeyError):
            simple_function["d"]

    def test_delitem(self, simple_function):
        del simple_function["a"]

        with pytest.raises(KeyError):
            simple_function["a"]


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
