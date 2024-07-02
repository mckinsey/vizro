"""Safeguard Code Execution."""

import ast
import builtins
import re
from typing import Union

from ._constants import REDLISTED_CLASS_METHODS, REDLISTED_DATA_HANDLING, WHITELISTED_BUILTINS, WHITELISTED_PACKAGES


def _check_imports(node: Union[ast.Import, ast.ImportFrom]):
    """Check if imports are whitelisted."""
    if isinstance(node, ast.Import):
        module = node.names[0].name
    else:
        module = node.module

    package = module.split(".")[0]

    if (package not in WHITELISTED_PACKAGES) and (package not in WHITELISTED_BUILTINS):
        raise Exception(f"Unsafe package {package} is used in generated code and cannot be executed.")


def _check_data_handling(node: ast.stmt):
    """Check usage of unsafe data file loading and saving."""
    code = ast.unparse(node)
    redlisted_data_handling = [method for method in REDLISTED_DATA_HANDLING if method in code]

    if redlisted_data_handling:
        methods_str = ", ".join(redlisted_data_handling)
        raise Exception(f"Unsafe loading or saving of data files is used in code: {methods_str} in line {code}")


def _check_class_method_usage(node: ast.stmt):
    """Check usage of unsafe builtin in code."""
    code = ast.unparse(node)
    redlisted_builtins = [funct for funct in REDLISTED_CLASS_METHODS if funct in code]

    if redlisted_builtins:
        functions_str = ", ".join(redlisted_builtins)
        raise Exception(
            f"Unsafe methods {functions_str} are used in generated code line: {code} and cannot be executed."
        )


def _check_builtin_function_usage(node: ast.stmt):
    """Check usage of unsafe builtin functions."""
    code = ast.unparse(node)

    builtin_list = [name for name, obj in vars(builtins).items()]
    non_whitelisted_builtins = [
        builtin
        for builtin in builtin_list
        if re.search(r"\b" + re.escape(builtin) + r"\b", code) and builtin not in WHITELISTED_BUILTINS
    ]

    if non_whitelisted_builtins:
        builtin_str = ", ".join(non_whitelisted_builtins)
        raise Exception(
            f"Unsafe builtin functions {builtin_str} are used in generated code line: {code} and cannot be executed. If"
            f" you require a builtin package, reach out to the Vizro team."
        )


def _analyze_node(node):
    if hasattr(node, "body"):
        for child in node.body:
            _analyze_node(child)
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        _check_imports(node)
    else:
        _check_data_handling(node)
        _check_class_method_usage(node)
        _check_builtin_function_usage(node)


def _safeguard_check(code: str):
    """Perform safeguard checks to avoid execution of malicious code."""
    try:
        tree = ast.parse(code)
    except (SyntaxError, UnicodeDecodeError):
        raise ValueError(f"Generated code is not valid: {code}")
    except OverflowError:
        raise ValueError(f"Generated code is too long to be parsed by ast: {code}")
    except Exception as e:
        raise ValueError(f"Generate code {code} cannot be parsed by ast due to error: {e}")

    for node in tree.body:
        _analyze_node(node)
