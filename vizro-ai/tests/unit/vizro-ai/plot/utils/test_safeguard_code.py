import re

import pytest

from vizro_ai.plot._utils._safeguard import _safeguard_check


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
