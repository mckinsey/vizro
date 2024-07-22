import pandas as pd
import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError


class TestConfig:
    """Test GraphState config creation"""

    @pytest.mark.parametrize(
        "dataframes, output_error",
        [
            (pd.DataFrame(), "dfs must be a list"),
            ([pd.DataFrame(), {}], "Each element in dfs must be a Pandas DataFrame"),
        ],
    )
    def test_check_dataframes(self, dataframes, output_error):
        with pytest.raises(ValidationError, match=output_error):
            pass
