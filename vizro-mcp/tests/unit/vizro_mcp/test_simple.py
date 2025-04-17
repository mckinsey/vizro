"""Simple test for Vizro MCP."""

import pytest
import vizro_mcp


def test_package_importable():
    """Test that the package can be imported."""
    try:
        assert True  # If we get here, the import was successful
    except ImportError as e:
        pytest.fail(f"Failed to import vizro_mcp: {e}")


def test_version():
    """Test that the package has a version."""
    assert hasattr(vizro_mcp, "__version__")
    assert isinstance(vizro_mcp.__version__, str)
    assert vizro_mcp.__version__ != ""


def test_main_function_exists():
    """Test that the main function exists."""
    assert hasattr(vizro_mcp, "main")
    assert callable(vizro_mcp.main)
