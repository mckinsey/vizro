"""Unit tests for vizro.themes._consistent_colors."""

from vizro.themes._consistent_colors import _clear, _consistent_color_discrete_map, _get_color
from vizro.themes._palettes import qualitative


def test_get_color_assigns_and_caches():
    """Test that the same category always gets the same color, and new categories get new colors."""
    _clear()
    assert _get_color("France") == qualitative[0]
    assert _get_color("Germany") == qualitative[1]
    # Requesting "France" again, after other categories were assigned, still returns its original color.
    assert _get_color("France") == qualitative[0]


def test_consistent_color_discrete_map_reuses_existing_assignments():
    """Test that a category already seen keeps its color when a new call introduces extra categories."""
    _clear()
    first_map = _consistent_color_discrete_map(["France", "Germany"])
    second_map = _consistent_color_discrete_map(["France", "Belgium"])

    assert first_map["France"] == second_map["France"]
    assert second_map["Belgium"] not in first_map.values()


def test_clear_resets_assignments():
    """Test that _clear() removes previous assignments and restarts the palette cycle."""
    _clear()
    _get_color("France")
    _clear()
    assert _get_color("Germany") == qualitative[0]
