"""Unit tests for vizro.themes public API."""

from types import SimpleNamespace

from vizro.themes import colors, palettes


def test_import_colors_and_palettes():
    """Test colors/palettes can be imported and is a SimpleNamespace."""
    assert isinstance(palettes, SimpleNamespace)
    assert isinstance(colors, SimpleNamespace)


def test_access_color():
    """Test individual colors can be accessed."""
    assert colors.blue == "#097DFE"


def test_access_default_qualitative_palette():
    """Test qualitative palette can be accessed."""
    assert palettes.qualitative == [
        "#097DFE",
        "#6F39E3",
        "#05D0F0",
        "#0F766E",
        "#8C8DE9",
        "#11B883",
        "#E77EC2",
        "#C84189",
        "#C0CA33",
        "#3E495B",
    ]


def test_access_default_sequential_palette():
    """Test sequential palette can be accessed (used for all numerical sequences)."""
    assert palettes.sequential_blue == [
        "#EFF6FE",
        "#DBEBFE",
        "#BDDCFE",
        "#8CC6FF",
        "#4BA5FF",
        "#097DFE",
        "#0063F6",
        "#004DE0",
        "#0B40B4",
        "#163B8B",
        "#142654",
    ]
