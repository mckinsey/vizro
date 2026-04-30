"""Security regression tests for VULN-001 and VULN-002 fixes.

VULN-001: query_dataframe used eval() with only first-method validation,
          allowing chained method attacks (e.g. head().to_csv("/tmp/data")).
          Fixed by replacing eval() with a dispatch table of safe handlers.

VULN-002: SSE streaming endpoints accepted raw JSON and forwarded all extra
          fields as **kwargs (mass parameter assignment). Fixed by:
          - validating through _StreamingRequest Pydantic model with
            extra="ignore" so unknown JSON keys are dropped at parse time;
          - in _kwargs_for_generate_response, only forwarding payload_extras
            that the action declares by name (NOT via **kwargs).
          Both layers are exercised by tests below.
"""

import pandas as pd
import pytest

from vizro_experimental.chat.actions._base_chat_action import _kwargs_for_generate_response
from vizro_experimental.chat.actions.streaming_chat_action import _StreamingRequest
from vizro_experimental.chat.popup.dashboard_agent import (
    _SAFE_OPERATIONS,
    _safe_groupby_agg,
    _safe_nlargest,
    _safe_sort_values,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def sample_df():
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "Alice", "Bob"],
            "score": [90, 80, 70, 85, 95],
            "grade": ["A", "B", "C", "A", "A"],
        }
    )


# ---------------------------------------------------------------------------
# VULN-001: Dispatch table correctness
# ---------------------------------------------------------------------------
class TestSafeOperations:
    """Test handlers that have non-trivial logic (validation, allowlists)."""

    def test_all_operations_are_callable(self):
        """Every entry in the dispatch table must be a callable."""
        for name, handler in _SAFE_OPERATIONS.items():
            assert callable(handler), f"_SAFE_OPERATIONS['{name}'] is not callable"

    def test_sort_values_requires_by(self, sample_df):
        assert "Error" in _safe_sort_values(sample_df)

    def test_nlargest_requires_column(self, sample_df):
        assert "Error" in _safe_nlargest(sample_df)

    def test_groupby_requires_by(self, sample_df):
        assert "Error" in _safe_groupby_agg(sample_df)

    def test_groupby_rejects_dangerous_agg(self, sample_df):
        result = _safe_groupby_agg(sample_df, by="name", agg="to_csv")
        assert "Error" in result
        assert "not allowed" in result


# ---------------------------------------------------------------------------
# VULN-001: Attack vectors from the security review are impossible
# ---------------------------------------------------------------------------
class TestEvalAttackVectorsPrevented:
    """Confirm old eval() attack vectors are now impossible.

    The old eval(f"df.{operation}") accepted arbitrary code as long as the
    first method was allowlisted. The dispatch table only accepts plain names,
    so chained/malicious expressions can never match a key.
    """

    def test_dispatch_table_has_no_dangerous_operations(self):
        """The dispatch table must not contain operations that write files or execute code."""
        dangerous_names = {
            "to_csv",
            "to_json",
            "to_parquet",
            "to_pickle",
            "to_excel",
            "to_hdf",
            "to_sql",
            "to_feather",
            "to_stata",
            "to_clipboard",
            "pipe",
            "apply",
            "applymap",
            "eval",
            "exec",
            "query",
        }
        found = dangerous_names & set(_SAFE_OPERATIONS)
        assert not found, f"Dangerous operations in dispatch table: {found}"

    @pytest.mark.parametrize(
        "malicious_operation",
        [
            'head().to_csv("/tmp/exfiltrated_data.csv")',
            "head().pipe(exit)",
            'query("@__builtins__")',
            "__import__('os').system('ls')",
            "to_csv('/tmp/data.csv')",
        ],
        ids=[
            "chained-exfil",
            "chained-dos",
            "query-builtins",
            "import-os",
            "direct-to_csv",
        ],
    )
    def test_malicious_operations_rejected(self, malicious_operation):
        """Malicious operation strings must not match any key in the dispatch table."""
        cleaned = malicious_operation.strip().rstrip("()")
        assert cleaned not in _SAFE_OPERATIONS


# ---------------------------------------------------------------------------
# VULN-002: _StreamingRequest validation
# ---------------------------------------------------------------------------
class TestStreamingRequestValidation:
    """Verify _StreamingRequest rejects malformed payloads and isolates extra fields."""

    def test_missing_required_fields_raises(self):
        with pytest.raises(Exception):
            _StreamingRequest(prompt="hello")  # missing messages

        with pytest.raises(Exception):
            _StreamingRequest(messages=[])  # missing prompt

    def test_extra_fields_are_dropped(self):
        """Regression for VULN-002: unknown JSON keys must be dropped at validation.

        Earlier the model used ``extra="allow"`` so injected keys lived in
        ``model_extra`` and could leak into ``generate_response`` whenever the action
        signature happened to have ``**kwargs``. The model now uses ``extra="ignore"``
        — extras don't survive validation at all.
        """
        req = _StreamingRequest(
            prompt="hello",
            messages=[],
            model="gpt-4",
            injected="malicious",
        )
        assert req.prompt == "hello"
        assert req.messages == []
        # extra="ignore" leaves model_extra unset
        assert not req.model_extra
        # The injected key must not have leaked onto the model as an attribute either.
        assert getattr(req, "injected", None) is None


# ---------------------------------------------------------------------------
# VULN-002: payload_extras forwarding via **kwargs is not a wildcard
# ---------------------------------------------------------------------------
class TestKwargsForGenerateResponseDoesNotForwardExtrasViaVarKw:
    """_kwargs_for_generate_response must only forward extras the action declares by name.

    Earlier the helper would forward *all* payload_extras as soon as the action
    signature contained ``**kwargs``, re-opening the mass-parameter-assignment hole
    that ``_StreamingRequest`` was meant to close. It now ignores ``**kwargs`` for
    extras: only declared parameter names get bound.
    """

    def test_var_kw_action_does_not_receive_attacker_extras(self):
        def action(messages, **kwargs):
            return None

        out = _kwargs_for_generate_response(
            action,
            uploaded_files=None,
            payload_extras={"injected": "malicious", "model": "gpt-4"},
        )
        assert "injected" not in out
        assert "model" not in out

    def test_declared_param_still_receives_value(self):
        """Legitimate use case: extras DO bind when the action declares them by name."""

        def action(messages, model: str = "default", **kwargs):
            return None

        out = _kwargs_for_generate_response(
            action,
            uploaded_files=None,
            payload_extras={"model": "gpt-4", "injected": "malicious"},
        )
        assert out["model"] == "gpt-4"
        assert "injected" not in out
