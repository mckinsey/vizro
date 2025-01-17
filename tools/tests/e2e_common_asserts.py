from hamcrest import any_of, assert_that, contains_string


def browser_console_warnings_checker(log_level, log_levels):
    assert_that(
        log_level["message"],
        any_of(
            contains_string("Invalid prop `persisted_props[0]` of value `on` supplied to `t`"),
            contains_string("React does not recognize the `%s` prop on a DOM element"),
            contains_string("_scrollZoom"),
            contains_string("unstable_flushDiscreteUpdates: Cannot flush updates when React is already rendering"),
            contains_string("React state update on an unmounted component"),
            contains_string("componentWillMount has been renamed"),
            contains_string("componentWillReceiveProps has been renamed"),
            contains_string("GPU stall due to ReadPixels"),
            contains_string("WebGL"),  # https://issues.chromium.org/issues/40277080
        ),
        reason=f"Error outoput: {log_levels}",
    )
