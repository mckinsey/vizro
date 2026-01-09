import pandas as pd
import pytest

from vizro_ai._vizro_ai import VizroAI


def test_vizro_ai_init_raises():
    with pytest.warns(DeprecationWarning), pytest.raises(RuntimeError, match="deprecated"):
        VizroAI()


def test_vizro_ai_plot_raises():
    instance = object.__new__(VizroAI)
    with pytest.raises(RuntimeError, match="deprecated"):
        instance.plot(pd.DataFrame(), "test")


def test_vizro_ai_dashboard_raises():
    instance = object.__new__(VizroAI)
    with pytest.raises(RuntimeError, match="deprecated"):
        instance.dashboard([pd.DataFrame()], "test")
