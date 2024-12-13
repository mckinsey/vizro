from hamcrest import any_of, assert_that, contains_string
from e2e_constants import (
    INVALID_PROP_ERROR,
    REACT_NOT_RECOGNIZE_ERROR,
    REACT_RENDERING_ERROR,
    READPIXELS_WARNING,
    SCROLL_ZOOM_ERROR,
    UNMOUNT_COMPONENTS_ERROR,
    WEBGL_WARNING,
    WILLMOUNT_RENAMED_WARNING,
    WILLRECEIVEPROPS_RENAMED_WARNING,
)


def browser_console_warnings_checker(log_level, log_levels):
    assert_that(
        log_level["message"],
        any_of(
            contains_string(INVALID_PROP_ERROR),
            contains_string(REACT_NOT_RECOGNIZE_ERROR),
            contains_string(SCROLL_ZOOM_ERROR),
            contains_string(REACT_RENDERING_ERROR),
            contains_string(UNMOUNT_COMPONENTS_ERROR),
            contains_string(WILLMOUNT_RENAMED_WARNING),
            contains_string(WILLRECEIVEPROPS_RENAMED_WARNING),
            contains_string(READPIXELS_WARNING),
            contains_string(WEBGL_WARNING),
        ),
        reason=f"Error outoput: {log_levels}",
    )
