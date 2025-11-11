"""Unit tests for vizro.themes public API."""

from types import SimpleNamespace

from vizro.themes import colors, palettes


def test_import_colors_and_palettes():
    """Test colors/palettes can be imported and is a SimpleNamespace."""
    assert isinstance(palettes, SimpleNamespace)
    assert isinstance(colors, SimpleNamespace)
    


def test_access_color():
    """Test individual colors can be accessed."""
    assert colors.cyan == "#00B4FF"


def test_access_default_qualitative_palette():
    """Test qualitative palette can be accessed."""
    assert palettes.qualitative == [
        "#00B4FF",
        "#FF9222",
        "#3949AB",
        "#FF5267",
        "#08BDBA",
        "#FDC935",
        "#689F38",
        "#976FD1",
        "#F781BF",
        "#52733E",
    ]


def test_access_default_sequential_palette():
    """Test sequential palette can be accessed (used for all numerical sequences)."""
    assert palettes.sequential_cyan == [
        "#AFE7F9",
        "#8BD0F6",
        "#6CBAEC",
        "#52A3DD",
        "#3B8DCB",
        "#2777B7",
        "#1661A2",
        "#074C8C",
        "#003875",
    ]
    

