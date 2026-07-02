import re

import pytest

from vizro_ai.agents._utils._safeguard import (
    VizroAICodeExecutionWarning,
    _safeguard_check,
    warn_code_execution_is_best_effort,
)


class TestMaliciousImports:
    @pytest.mark.parametrize("package", ["sys", "pickle", "os", "subprocess", "eval", "exec", "compile", "open"])
    def test_malicious_import(self, package):
        code = f"import {package}"

        with pytest.raises(
            Exception, match=f"Unsafe package {package} is used in generated code and cannot be executed."
        ):
            _safeguard_check(code)

    @pytest.mark.parametrize("package", ["sys", "pickle", "os", "subprocess", "eval", "exec", "compile", "open"])
    def test_malicious_import_in_nested_function(self, package):
        code = f"def get_import():\n    x = 1\n    def get_inner_import():\n        import {package}"
        with pytest.raises(
            Exception, match=f"Unsafe package {package} is used in generated code and cannot be executed."
        ):
            _safeguard_check(code)

    @pytest.mark.parametrize("package", ["sys", "pickle", "os"])
    def test_malicious_import_from(self, package):
        """Test handling of ast.ImportFrom nodes."""
        code = f"from {package} import something"
        with pytest.raises(
            Exception, match=f"Unsafe package {package} is used in generated code and cannot be executed."
        ):
            _safeguard_check(code)


class TestMaliciousFunctions:
    @pytest.mark.parametrize(
        "code_line, builtin",
        [
            ("builtins_names = dir(__builtins__)", "__builtins__"),
            ("subclasses = int.__subclasses__()", "__subclasses__"),
            ("version = sys.version()", "sys"),
        ],
    )
    def test_malicious_methods_in_code(self, code_line, builtin):
        with pytest.raises(
            Exception,
            match=re.escape(
                f"Unsafe methods {builtin} are used in generated code line: {code_line} and cannot be executed."
            ),
        ):
            _safeguard_check(code_line)

    @pytest.mark.parametrize("builtin", ["eval", "exec", "compile", "open", "__import__"])
    def test_malicious_builtins_usage_in_code(self, builtin):
        code = f"import pandas as pd\n{builtin}('print(1)')"
        with pytest.raises(
            Exception,
            match=re.escape(
                f"Unsafe builtin functions {builtin} are used in generated code line: {builtin}('print(1)') and cannot "
                f"be executed. If you require a builtin package, reach out to the Vizro team."
            ),
        ):
            _safeguard_check(code)


class TestUnsafeDataFileHandling:
    @pytest.mark.parametrize(
        "data_handling",
        [
            ".to_csv",
            ".to_excel",
            ".to_parquet",
            ".to_clipboard",
            ".read_csv",
            ".read_excel",
            ".read_parquet",
            ".read_clipboard",
            ".netcdf",
        ],
    )
    def test_unsafe_data_import_export_in_code(self, data_handling):
        code = f"import pandas\ndf = pd.DataFrame()\ndf{data_handling}('testfile')"
        with pytest.raises(
            Exception,
            match=re.escape(
                f"Unsafe loading or saving of data files is used in code: {data_handling} in line df{data_handling}"
                f"('testfile')"
            ),
        ):
            _safeguard_check(code)

    @pytest.mark.parametrize(
        "data_handling",
        [
            ".to_csv",
            ".to_excel",
            ".to_parquet",
            ".to_clipboard",
            ".read_csv",
            ".read_excel",
            ".read_parquet",
            ".read_clipboard",
            ".netcdf",
        ],
    )
    def test_unsafe_data_import_export_in_function(self, data_handling):
        code = f"import pandas\ndef data_handling():\n    df = pd{data_handling}('testfile')"
        with pytest.raises(
            Exception,
            match=re.escape(
                f"Unsafe loading or saving of data files is used in code: {data_handling} in line df = "
                f"pd{data_handling}('testfile')"
            ),
        ):
            _safeguard_check(code)

    @pytest.mark.parametrize(
        "datafile, file_type",
        [
            ("test.csv", ".csv"),
            ("test.xls", ".xls"),
            ("test.zip", ".zip"),
            ("test.pkl", ".pkl"),
            ("test.txt", ".txt"),
            ("test.mat", ".mat"),
        ],
    )
    def test_unsafe_datafiles(self, datafile, file_type):
        code = f"import pandas\ndef data_handling():\n    x = {datafile}"
        with pytest.raises(
            Exception,
            match=(f"Unsafe loading or saving of data files is used in code: {file_type} in line x = {datafile}"),
        ):
            _safeguard_check(code)


class TestFilesystemReachingMethodBypass:
    """Regression tests for the numpy file-access bypass reported via SECURITY.md.

    numpy is a whitelisted package, but several of its methods reach the filesystem
    directly. These must be caught by the data-handling denylist even though the
    package import itself is allowed.
    """

    @pytest.mark.parametrize(
        "code_line, method",
        [
            # Read + exfiltration variant from the report.
            ('arr = np.memmap("/tmp/secret.env", dtype="uint8", mode="r")', ".memmap"),
            # Arbitrary write variant from the report.
            ('arr = np.memmap("/tmp/out.dat", dtype="uint8", mode="w+", shape=(2,))', ".memmap"),
            # Additional bypass found during triage: previously masked by the malformed
            # ".fromfile.save" entry, which matched neither ".fromfile" nor ".save" alone.
            ('arr = np.fromfile("/tmp/secret.env", dtype="uint8")', ".fromfile"),
            ('np.save("/tmp/out", np.arange(3))', ".save"),
        ],
    )
    def test_numpy_filesystem_methods_blocked(self, code_line, method):
        code = f"import numpy as np\n{code_line}"
        with pytest.raises(Exception, match="Unsafe loading or saving of data files is used in code") as excinfo:
            _safeguard_check(code)
        assert method in str(excinfo.value)


class TestBestEffortWarning:
    """The safeguard's best-effort nature must be surfaced whenever generated code is executed."""

    def test_warn_helper_emits_security_warning(self):
        with pytest.warns(VizroAICodeExecutionWarning, match="best-effort"):
            warn_code_execution_is_best_effort()

    def test_exec_code_emits_security_warning(self):
        from vizro_ai.agents.response_models._response_models import _exec_code

        with pytest.warns(VizroAICodeExecutionWarning):
            _exec_code("x = 1", {})


class TestInvalidCodeParsing:
    def test_syntax_error(self):
        code = "def invalid syntax here"
        with pytest.raises(ValueError, match="Generated code is not valid"):
            _safeguard_check(code)

    def test_unicode_decode_error(self, mocker):
        # Mock ast.parse to raise UnicodeDecodeError
        mocker.patch("ast.parse", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte"))
        code = "def valid_code(): pass"
        with pytest.raises(ValueError, match="Generated code is not valid"):
            _safeguard_check(code)

    def test_overflow_error(self, mocker):
        # Mock ast.parse to raise OverflowError
        mocker.patch("ast.parse", side_effect=OverflowError("Result too large"))
        code = "def valid_code(): pass"
        with pytest.raises(ValueError, match="Generated code is too long to be parsed by ast"):
            _safeguard_check(code)

    def test_general_exception(self, mocker):
        # Mock ast.parse to raise a generic Exception
        mocker.patch("ast.parse", side_effect=Exception("Mock parsing error"))
        code = "def valid_code(): pass"
        expected_msg = "Generate code def valid_code(): pass cannot be parsed by ast due to error: Mock parsing error"
        with pytest.raises(ValueError, match=re.escape(expected_msg)):
            _safeguard_check(code)
