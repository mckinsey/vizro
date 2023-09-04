"""Fixtures for themes tests."""
import numpy as np
import pandas as pd
import pytest

import vizro._themes as themes


@pytest.fixture
def template():
    """Fixture for template."""
    yield np.random.choice([themes.dark, themes.light], 1)[0]


@pytest.fixture
def chart_data():
    """Fixture for chart data."""
    data_points = np.random.randint(0, 100, 1, dtype=int)
    data = pd.DataFrame(
        {
            "x": np.random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"], data_points),
            "y": np.random.normal(0, 200, data_points),
        }
    )
    yield data
