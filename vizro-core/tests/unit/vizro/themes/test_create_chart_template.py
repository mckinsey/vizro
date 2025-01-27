import pytest

from vizro._themes.generate_plotly_templates import _extract_last_two_occurrences, extract_bs_variables_from_css


@pytest.fixture
def css_content():
    css_content = """
        :root, [data-bs-theme=light] {
            --bs-primary: #007bff;
            --bs-tertiary-color: #adb5bd;
        }
        :root, [data-bs-theme=dark] {
            --bs-primary: #375a7f;
            --bs-secondary: #6c757d;

        }
        [data-bs-theme=light] {
            --bs-primary: #976fd1;
            --bs-secondary: #444fff;
        }
        """

    return css_content


@pytest.mark.parametrize(
    "variable, expected",
    [
        ("--bs-primary", ("#375a7f", "#976fd1")),
        ("--bs-secondary", ("#6c757d", "#444fff")),
        ("--bs-tertiary", (None, None)),
    ],
)
def test_extract_last_two_occurrences(variable, css_content, expected):
    result_dark, result_light = _extract_last_two_occurrences(variable, css_content)
    assert (result_dark, result_light) == expected


def test_extract_bs_variables_from_css_file(css_content):
    expected_dark = {
        "BS-PRIMARY": "#375a7f",
        "BS-SECONDARY": "#6c757d",
    }
    expected_light = {
        "BS-PRIMARY": "#976fd1",
        "BS-SECONDARY": "#444fff",
    }

    result_dark, result_light = extract_bs_variables_from_css(
        ["--bs-primary", "--bs-secondary", "--bs-tertiary"], css_content
    )

    assert result_dark == expected_dark
    assert result_light == expected_light
