from vizro.managers import color_manager
from vizro.themes._palettes import qualitative


def test_get_color_discrete_map_assigns_and_caches():
    """Test that the same category always gets the same color, and new categories get new colors."""
    color_manager._clear()
    color_map = color_manager._get_color_discrete_map(["France", "Germany"])

    assert color_map["France"] == qualitative[0]
    assert color_map["Germany"] == qualitative[1]
    # Requesting "France" again, after other categories were assigned, still returns its original color.
    assert color_manager._get_color_discrete_map(["France"])["France"] == qualitative[0]


def test_get_color_discrete_map_reuses_existing_assignments():
    """Test that a category already seen keeps its color when a new call introduces extra categories."""
    color_manager._clear()
    first_map = color_manager._get_color_discrete_map(["France", "Germany"])
    second_map = color_manager._get_color_discrete_map(["France", "Belgium"])

    assert first_map["France"] == second_map["France"]
    assert second_map["Belgium"] not in first_map.values()


def test_get_color_discrete_map_handles_mixed_type_categories():
    """Test that categories that can't be compared to each other (e.g. mixed int/str) don't raise."""
    color_manager._clear()
    color_map = color_manager._get_color_discrete_map(["a", 1, "b"])

    assert len(color_map) == 3
    assert len(set(color_map.values())) == 3


def test_clear_resets_assignments():
    """Test that _clear() removes previous assignments and restarts the palette cycle."""
    color_manager._clear()
    color_manager._get_color_discrete_map(["France"])
    color_manager._clear()

    assert color_manager._get_color_discrete_map(["Germany"])["Germany"] == qualitative[0]
